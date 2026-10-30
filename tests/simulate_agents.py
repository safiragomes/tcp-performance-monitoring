
# Simulador de estresse com multiplos agentes TCP concorrentes.

import argparse
import os
import socket
import sys
import threading
import time

# Permite importar os modulos a partir da raiz do projeto.
sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from common.protocol import Connection


def agent_task(agent_id, interval, run_time, host, port, die_abruptly=False):
    name = f"simulated-agent-{agent_id}"

    # Estabelece uma conexao TCP com o servidor.
    try:
        sock = socket.create_connection((host, port), timeout=5)
    except OSError as e:
        print(f"[Agente {agent_id}] Falha ao conectar: {e}")
        return

    con = Connection(sock)
    became_silent = False

    try:
        # Registra o agente antes de enviar metricas.
        con.send({
            "type": "REGISTER",
            "name": name,
            "interval": interval
        })

        response = con.receive()

        if not isinstance(response, dict) or response.get("type") != "OK":
            print(
                f"[Agente {agent_id}] Registro recusado. "
                f"Resposta: {response}"
            )
            return

        print(f"[Agente {agent_id}] Registrado com sucesso!")

        start_time = time.monotonic()

        # Envia metricas periodicamente pela mesma conexao TCP.
        while time.monotonic() - start_time < run_time:
            elapsed = time.monotonic() - start_time

            # Simula um agente que deixa de enviar mensagens
            # sem fechar imediatamente a conexao.
            if die_abruptly and elapsed >= run_time / 2:
                became_silent = True

                print(
                    f"[Agente {agent_id}] Simulando agente silencioso. "
                    "Aguardando deteccao de timeout pelo servidor..."
                )

                # Mantem o socket aberto por tempo suficiente
                # para o servidor identificar a inatividade.
                remaining = run_time - elapsed
                silence_time = max(remaining, 3 * interval + 1)

                time.sleep(silence_time)
                return

            # Dados ficticios usados para testar o servidor.
            dummy_metrics = {
                "type": "METRICS",
                "cpu": {
                    "overall": 45.5,
                    "cores": [40.0, 50.0, 45.0, 47.0]
                },
                "memory": {
                    "total_mb": 16000,
                    "used_mb": 8000,
                    "free_mb": 8000
                }
            }

            con.send(dummy_metrics)

            # Aguarda o proximo envio sem ultrapassar
            # desnecessariamente a duracao configurada.
            remaining = run_time - (time.monotonic() - start_time)

            if remaining > 0:
                time.sleep(min(interval, remaining))

    except Exception as e:
        print(f"[Agente {agent_id}] Erro durante a simulacao: {e}")

    finally:
        # O agente silencioso permanece conectado durante a
        # espera e somente depois libera os recursos.
        try:
            con.close()

            if became_silent:
                print(f"[Agente {agent_id}] Simulacao de silencio encerrada.")
            else:
                print(f"[Agente {agent_id}] Conexao encerrada.")

        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de multiplos agentes TCP"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Endereco IP do servidor"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Porta TCP do servidor"
    )

    parser.add_argument(
        "--agents",
        type=int,
        default=10,
        help="Quantidade de agentes simulados"
    )

    parser.add_argument(
        "--duration",
        type=float,
        default=60,
        help="Duracao da simulacao em segundos"
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=2,
        help="Intervalo de envio das metricas em segundos"
    )

    parser.add_argument(
        "--silent-agent",
        type=int,
        default=3,
        help="ID do agente que ficara silencioso; -1 desativa"
    )

    args = parser.parse_args()

    if args.agents < 1 or args.duration <= 0 or args.interval <= 0:
        parser.error(
            "--agents deve ser positivo e "
            "--duration e --interval devem ser maiores que zero"
        )

    if not 0 <= args.port <= 65535:
        parser.error("--port deve estar entre 0 e 65535")

    print("=" * 60)
    print("SIMULACAO DE AGENTES TCP - EQUIPE 06")
    print("=" * 60)
    print(f"Servidor: {args.host}:{args.port}")
    print(f"Quantidade de agentes: {args.agents}")
    print(f"Duracao: {args.duration} segundos")
    print(f"Intervalo: {args.interval} segundos")
    print(f"Agente silencioso: {args.silent_agent}")
    print("=" * 60)

    threads = []

    for i in range(args.agents):
        will_die = (i == args.silent_agent)

        t = threading.Thread(
            target=agent_task,
            args=(
                i,
                args.interval,
                args.duration,
                args.host,
                args.port,
                will_die
            )
        )

        threads.append(t)
        t.start()

        # Pequeno atraso entre as conexoes.
        time.sleep(0.1)

    for t in threads:
        t.join()

    print("=" * 60)
    print("Simulacao encerrada.")
    print("Consulte o painel e os logs para verificar os resultados.")
    print("=" * 60)


if __name__ == "__main__":
    main()
