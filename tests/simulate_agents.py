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

    # Implementação do ciclo de vida e troca de mensagens 
    try:
        # Envia a primeira mensagem requisitada pela especificação: REGISTER
        con.send({"type": "REGISTER", "name": name, "interval": interval})
        
        # Aguarda resposta síncrona do servidor
        response = con.receive()
        if not response or response.get("type") != "OK":
            print(f"[Agente {agent_id}] Erro ou rejeição ao registrar. Resposta: {response}")
            con.close()
            return
            
        print(f"[Agente {agent_id}] Registrado com sucesso! Enviando métricas...")

        start_time = time.time()
        
        # Loop de envio de métricas durante o run_time
        while time.time() - start_time < run_time:
            # Simulação de morte abrupta e dados simulados (Dummy)
            # Aos 50% do tempo de execução, se ativado, o agente simula uma queda de energia
            if die_abruptly and (time.time() - start_time) > (run_time / 2):
                print(f"[Agente {agent_id}] ⚠️ Simulando MORTE ABRUPTA. Silenciando socket sem fechar.")
                # A thread dorme indefinidamente em vez de enviar dados
                # Como o socket não foi fechado com '.close()', o servidor vai ter q processar a ausência de dados pelo timeout de 3x o intervalo
                time.sleep(run_time) 
                return

            # Cria dados fictícios
            dummy_metrics = {
                "type": "METRICS",
                "cpu": {"overall": 45.5, "cores": [40.0, 50.0, 45.0, 47.0]},
                "memory": {"total_mb": 16000, "used_mb": 8000, "free_mb": 8000}
            }
            
            con.send(dummy_metrics)
            time.sleep(interval)
            
    except Exception as e:
        print(f"[Agente {agent_id}] Conexão perdida ou erro inesperado: {e}")
    finally:
        # Tenta fechar a conexão de forma limpa caso não tenha morrido abruptamente
        if not die_abruptly:
            try:
                con.close()
                print(f"[Agente {agent_id}] Finalizado e desconectado graciosamente.")
            except:
                pass