import argparse
import logging
import socket
import threading

from common.protocol import DEFAULT_PORT, Connection
from server.state import State

REGISTER_TIMEOUT = 10  # segundos para o agente mandar o REGISTER
TIMEOUT_FACTOR = 3     # sem mensagens por 3x o intervalo = agente caiu

log = logging.getLogger("server")


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def valid_register(message):
    return (
        isinstance(message, dict)
        and message.get("type") == "REGISTER"
        and isinstance(message.get("name"), str)
        and message["name"].strip() != ""
        and is_number(message.get("interval"))
        and message["interval"] > 0
    )


def valid_metrics(message):
    if not isinstance(message, dict) or message.get("type") != "METRICS":
        return False
    cpu = message.get("cpu")
    memory = message.get("memory")
    return (
        isinstance(cpu, dict)
        and is_number(cpu.get("overall"))
        and isinstance(cpu.get("cores"), list)
        and isinstance(memory, dict)
        and all(is_number(memory.get(k)) for k in ("total_mb", "used_mb", "free_mb"))
    )


def send_quietly(con, message):
    try:
        con.send(message)
    except OSError:
        pass


def handle_client(sock, addr, state):
    con = Connection(sock)
    name = None  # só fica preenchido depois que o registro for aceito
    try:
        sock.settimeout(REGISTER_TIMEOUT)
        try:
            message = con.receive()
        except ValueError:
            message = None
        if message is None:
            log.info("%s:%s saiu sem se registrar", *addr)
            return
        if not valid_register(message):
            log.warning("%s:%s mandou um REGISTER inválido: %s", addr[0], addr[1], message)
            send_quietly(con, {"type": "ERROR", "reason": "invalid REGISTER"})
            return

        interval = message["interval"]
        if not state.register(message["name"], interval):
            log.warning("registro recusado, nome já em uso: %s", message["name"])
            send_quietly(con, {"type": "ERROR", "reason": "name already in use"})
            return

        name = message["name"]
        con.send({"type": "OK"})
        log.info("%s conectado (%s:%s, intervalo %ss)", name, addr[0], addr[1], interval)

        sock.settimeout(TIMEOUT_FACTOR * interval)
        while True:
            try:
                message = con.receive()
            except ValueError:
                log.warning("%s mandou uma linha que não é JSON, ignorando", name)
                continue
            if message is None:
                log.info("%s desconectou", name)
                return
            if not valid_metrics(message):
                log.warning("%s mandou METRICS inválido, ignorando", name)
                continue
            state.add_reading(name, message)

    except socket.timeout:
        if name is None:
            log.warning("%s:%s não mandou o REGISTER a tempo", addr[0], addr[1])
        else:
            log.warning("%s ficou %ss sem enviar nada, removendo", name, TIMEOUT_FACTOR * interval)
        send_quietly(con, {"type": "ERROR", "reason": "timeout"})
    except OSError as e:
        log.warning("conexão com %s perdida: %s", name or addr, e)
    finally:
        if name is not None:
            state.remove(name)
        con.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Servidor de monitoramento")
    parser.add_argument("--host", default="0.0.0.0", help="endereço em que o servidor escuta")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="porta do servidor")
    parser.add_argument("--refresh", type=float, default=2, help="segundos entre as atualizações do painel")
    parser.add_argument("--no-dashboard", action="store_true", help="não mostra o painel, imprime os logs no terminal")
    return parser.parse_args()


def setup_logging(to_terminal):
    # o painel limpa o terminal a cada atualização, então os logs vão para um arquivo
    handler = logging.StreamHandler() if to_terminal else logging.FileHandler("server.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
    log.addHandler(handler)
    log.setLevel(logging.INFO)


def main():
    args = parse_args()
    setup_logging(to_terminal=args.no_dashboard)
    state = State()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_sock.bind((args.host, args.port))
    except OSError as e:
        print(f"Não foi possível usar {args.host}:{args.port}: {e}")
        return 1
    server_sock.listen()
    log.info("servidor escutando em %s:%s", args.host, args.port)

    if not args.no_dashboard:
        from server.dashboard import start_dashboard
        start_dashboard(state, args.refresh)

    try:
        while True:
            sock, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(sock, addr, state), daemon=True).start()
    except KeyboardInterrupt:
        print("\nServidor encerrado")
    finally:
        server_sock.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
