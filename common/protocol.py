import json

DEFAULT_PORT = 5000

class Connection:

    def __init__(self, sock):
        self.sock = sock
        self.buffer = b""

    def send(self, message):

        text = json.dumps(message) + "\n"
        self.sock.sendall(text.encode("utf-8"))

    def receive(self):

        while b"\n" not in self.buffer:
            chunk = self.sock.recv(4096)
            if chunk == b"":
                return None
            self.buffer += chunk

        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line.decode("utf-8"))

    def close(self):
        self.sock.close()