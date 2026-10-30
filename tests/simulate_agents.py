# Script que simula múltiplos clientes concorrentes conectando-se ao servidor

import os
import sys
import time
import threading
import socket

# Garante que a pasta raiz do projeto esteja no Python Path para importar a classe Connection corretamente
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.protocol import Connection

# Tarefa rodada por cada thread - conecta no servidor, registra-se e envia dados
def agent_task(agent_id, interval, run_time, die_abruptly=False):
    # Cria o socket puro
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Tenta conectar na porta padrão do servidor
        sock.connect(('127.0.0.1', 5000))
    except Exception as e:
        print(f"[Agente {agent_id}] Falha ao conectar no servidor: {e}")
        return

    # Envolve o socket na abstração de comunicação requerida
    con = Connection(sock)
    name = f"simulated-agent-{agent_id}"