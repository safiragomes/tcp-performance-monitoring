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

