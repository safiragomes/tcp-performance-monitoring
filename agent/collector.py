# Módulo responsável por coletar as métricas de CPU e Memória da máquina local

import psutil

# Coleta o uso atual de memória RAM e converte os valores para Megabytes (MB)
# Os valores retornados são inteiros pra bater com a especificação do protocolo
def collect_memory():
    mem_info = psutil.virtual_memory()
    
    # Fator de conversão de Bytes pra Megabytes
    mb_divisor = 1024 * 1024
    
    # Retorna o dicionário com as chaves
    return {
        "total_mb": int(mem_info.total / mb_divisor),
        "used_mb": int(mem_info.used / mb_divisor),
        "free_mb": int(mem_info.available / mb_divisor) # available reflete melhor a RAM livre no Gerenciador de Tarefas
    }

# Coleta o uso percentual da CPU
# Usa um pequeno intervalo (0.1s) para garantir uma leitura precisa do sistema
def collect_cpu():
    # Coleta a média geral de uso da CPU (0 a 100%)
    overall_cpu = psutil.cpu_percent(interval=0.1)
    
    # Coleta o percentual individual de cada núcleo/thread
    cores_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
    
    return {
        "overall": overall_cpu,
        "cores": cores_cpu
    }

# Une as informações de CPU e memória em um único dicionário para ser enviado pelo socket, com o contrato estabelecido no protocolo
def collect_metrics():
    # A chave principal deve ser "type" com o valor "METRICS"
    return {
        "type": "METRICS",
        "cpu": collect_cpu(),
        "memory": collect_memory()
    }