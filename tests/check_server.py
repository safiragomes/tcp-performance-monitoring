import os
import socket
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Connection
from server import server as srv
from server.state import State

srv.REGISTER_TIMEOUT = 1 


def start_server():
    state = State()
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen()

    def loop():
        while True:
            try:
                sock, addr = listener.accept()
            except OSError:
                return
            threading.Thread(target=srv.handle_client, args=(sock, addr, state), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()
    return state, listener.getsockname()[1]


def connect(port):
    return Connection(socket.create_connection(("127.0.0.1", port), timeout=5))


METRICS = {"type": "METRICS", "cpu": {"overall": 10.0, "cores": [10.0, 11.0]},
           "memory": {"total_mb": 100, "used_mb": 40, "free_mb": 60}}


def wait_for(cond, seconds=3):
    end = time.time() + seconds
    while time.time() < end:
        if cond():
            return True
        time.sleep(0.05)
    return False


state, port = start_server()

# 1) registro normal e leitura guardada
a = connect(port)
a.send({"type": "REGISTER", "name": "a", "interval": 1})
assert a.receive() == {"type": "OK"}
a.send(METRICS)
assert wait_for(lambda: len(state.snapshot().get("a", {}).get("readings", [])) == 1)
print("ok  registro e leitura")

# 2) nome repetido é recusado e não derruba o agente original
b = connect(port)
b.send({"type": "REGISTER", "name": "a", "interval": 1})
assert b.receive() == {"type": "ERROR", "reason": "name already in use"}
time.sleep(0.3)
assert "a" in state.snapshot()
print("ok  nome repetido recusado, original continua na lista")

# 3) mensagens inválidas são ignoradas sem derrubar o agente
a.sock.sendall(b"isso nao e json\n")
a.send({"type": "METRICS", "cpu": "errado"})
a.send([1, 2, 3])
a.send(METRICS)
assert wait_for(lambda: len(state.snapshot()["a"]["readings"]) == 2)
print("ok  lixo ignorado, agente continua conectado")

# 4) REGISTER inválido
c = connect(port)
c.send({"type": "REGISTER", "name": "", "interval": 1})
assert c.receive()["type"] == "ERROR"
d = connect(port)
d.send({"type": "REGISTER", "name": "d", "interval": -5})
assert d.receive()["type"] == "ERROR"
e = connect(port)
e.send({"type": "METRICS"})  # primeira mensagem não é REGISTER
assert e.receive()["type"] == "ERROR"
print("ok  REGISTER inválido recusado")

# 5) buffer circular: só as últimas 20 leituras
for _ in range(30):
    a.send(METRICS)
assert wait_for(lambda: len(state.snapshot()["a"]["readings"]) == 20)
time.sleep(0.3)
assert len(state.snapshot()["a"]["readings"]) == 20
print("ok  guarda só as últimas 20 leituras")

# 6) desconexão normal remove da lista
a.close()
assert wait_for(lambda: "a" not in state.snapshot())
print("ok  desconexão remove da lista")

# 7) agente mudo (não fecha o socket) é removido por timeout e recebe ERROR
f = connect(port)
f.send({"type": "REGISTER", "name": "f", "interval": 0.3})  # timeout = 0.9 s
assert f.receive() == {"type": "OK"}
assert "f" in state.snapshot()
assert wait_for(lambda: "f" not in state.snapshot(), 3)
assert f.receive() == {"type": "ERROR", "reason": "timeout"}
print("ok  agente mudo removido por timeout")

# 8) conectou e não mandou REGISTER: servidor não trava nem lança NameError
g = connect(port)
assert g.receive() == {"type": "ERROR", "reason": "timeout"}
print("ok  sem REGISTER: timeout tratado")

# 9) nome pode ser reutilizado depois que o agente sai
h = connect(port)
h.send({"type": "REGISTER", "name": "a", "interval": 1})
assert h.receive() == {"type": "OK"}
print("ok  nome liberado volta a ser aceito")

# 10) State com várias threads escrevendo ao mesmo tempo
s = State()
for i in range(20):
    s.register(f"n{i}", 1)


def worker(i):
    for _ in range(500):
        s.add_reading(f"n{i}", METRICS)
        s.snapshot()


ts = [threading.Thread(target=worker, args=(i,)) for i in range(20)]
[t.start() for t in ts]
[t.join() for t in ts]
assert all(len(v["readings"]) == 20 for v in s.snapshot().values())
print("ok  State com 20 threads")

print("todos os testes do servidor passaram")