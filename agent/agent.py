import argparse
import socket
import sys
import time

from agent.collector import collect_metrics
from common.protocol import DEFAULT_PORT, Connection

# tempo máximo para conectar e para receber a resposta do REGISTER
CONNECT_TIMEOUT = 10


class ServerClosed(Exception):
    pass


def parse_args():
    parser = argparse.ArgumentParser(description="Agente de monitoramento de CPU e memória")
    parser.add_argument("--host", default="127.0.0.1", help="endereço do servidor")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="porta do servidor")
    parser.add_argument("--name", default=socket.gethostname(), help="nome único do agente")
    parser.add_argument("--interval", type=int, default=5, help="segundos entre os envios de METRICS")
    args = parser.parse_args()
    if args.interval <= 0:
        parser.error("--interval deve ser maior que zero")
    return args


def register(con, name, interval):
    con.send({"type": "REGISTER", "name": name, "interval": interval})
    try:
        response = con.receive()
    except socket.timeout:
        print("O servidor não respondeu ao REGISTER")
        return False
    except ValueError:
        print("Resposta inválida do servidor ao REGISTER")
        return False

    if response is None:
        raise ServerClosed()

    if response.get("type") == "OK":
        return True
    if response.get("type") == "ERROR":
        print(f"Registro recusado pelo servidor: {response.get('reason', 'sem motivo informado')}")
    else:
        print(f"Resposta inesperada ao REGISTER: {response}")
    return False


def wait_until(con, deadline):
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return True

        con.sock.settimeout(remaining)
        try:
            message = con.receive()
        except socket.timeout:
            return True
        except ValueError:
            print("Mensagem inválida recebida do servidor, ignorando")
            continue

        if message is None:
            raise ServerClosed()
        if message.get("type") == "ERROR":
            print(f"Servidor encerrou o agente: {message.get('reason', 'sem motivo informado')}")
            return False


def send_metrics(con, interval):
    next_send = time.monotonic()
    while True:
        con.send(collect_metrics())

        # se a coleta atrasar, reagenda a partir de agora em vez de enviar várias seguidas
        next_send = max(next_send + interval, time.monotonic())
        if not wait_until(con, next_send):
            return


def run(args):
    try:
        sock = socket.create_connection((args.host, args.port), timeout=CONNECT_TIMEOUT)
    except OSError as e:
        print(f"Não foi possível conectar em {args.host}:{args.port}: {e}")
        return 1

    con = Connection(sock)
    try:
        if not register(con, args.name, args.interval):
            return 1
        print(f"Registrado como {args.name} em {args.host}:{args.port}, enviando métricas a cada {args.interval}s")
        send_metrics(con, args.interval)
        return 1
    except ServerClosed:
        print("O servidor fechou a conexão")
        return 1
    except OSError as e:
        print(f"Conexão com o servidor perdida: {e}")
        return 1
    finally:
        con.close()


def main():
    args = parse_args()
    try:
        sys.exit(run(args))
    except KeyboardInterrupt:
        print("\nAgente encerrado")
        sys.exit(0)


if __name__ == "__main__":
    main()
