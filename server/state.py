import threading
import time
from collections import deque

MAX_READINGS = 20


class State:
    """Agentes conectados e as últimas leituras de cada um, protegidos por um Lock."""

    def __init__(self):
        self._lock = threading.Lock()
        self._agents = {}

    def register(self, name, interval):
        with self._lock:
            if name in self._agents:
                return False
            self._agents[name] = {
                "interval": interval,
                "connected_at": time.time(),
                "last_message": None,
                "readings": deque(maxlen=MAX_READINGS),
            }
            return True

    def add_reading(self, name, metrics):
        with self._lock:
            agent = self._agents.get(name)
            if agent is None:
                return
            agent["readings"].append(metrics)
            agent["last_message"] = time.time()

    def remove(self, name):
        with self._lock:
            self._agents.pop(name, None)

    def snapshot(self):
        # devolve uma cópia, para o painel ler sem segurar o Lock
        with self._lock:
            return {
                name: {
                    "interval": agent["interval"],
                    "connected_at": agent["connected_at"],
                    "last_message": agent["last_message"],
                    "readings": list(agent["readings"]),
                }
                for name, agent in self._agents.items()
            }
