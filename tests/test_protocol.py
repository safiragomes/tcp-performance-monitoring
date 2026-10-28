import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.protocol import Connection

def make_pair():
    a, b = socket.socketpair()
    return a, Connection(a), Connection(b)

def test_single_message():
    _, sender, receiver = make_pair()
    sender.send({"type": "OK"})
    assert receiver.receive() == {"type": "OK"}

def test_two_messages_in_one_send():
    raw, _, receiver = make_pair()
    raw.sendall(b'{"n": 1}\n{"n": 2}\n')
    assert receiver.receive() == {"n": 1}
    assert receiver.receive() == {"n": 2}

def test_message_split_in_pieces():
    raw, _, receiver = make_pair()
    raw.sendall(b'{"type": "ME')
    raw.sendall(b'TRICS"}\n')
    assert receiver.receive() == {"type": "METRICS"}

def test_accents():
    _, sender, receiver = make_pair()
    sender.send({"reason": "nome já em uso"})
    assert receiver.receive() == {"reason": "nome já em uso"}

def test_closed_connection_returns_none():
    _, sender, receiver = make_pair()
    sender.close()
    assert receiver.receive() is None

if __name__ == "__main__":
    tests = [f for name, f in sorted(globals().items()) if name.startswith("test_")]
    for test in tests:
        test()
        print("ok  ", test.__name__)
    print("todos os testes passaram")