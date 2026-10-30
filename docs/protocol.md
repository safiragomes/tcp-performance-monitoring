# Protocolo de comunicação — APS 01, Equipe 06

## Visão geral

O sistema utiliza **sockets TCP** para comunicação entre os agentes e o servidor de monitoramento.

- **Transporte:** TCP.
- **Porta padrão:** `5000`, configurável por meio do argumento `--port`. Nos testes manuais da equipe foi usada a porta `5001`.
- **Codificação:** UTF-8.
- **Formato:** uma mensagem JSON por linha, terminada em `\n` (JSON Lines).
- **Implementação:** `common/protocol.py`, classe `Connection`, com os métodos `send()`, `receive()` e `close()`.
- **Persistência:** o mesmo socket é utilizado para o registro e os envios periódicos de métricas até a desconexão.

## Fluxo da comunicação

1. O agente abre uma conexão TCP com o servidor.
2. A primeira mensagem do agente deve ser `REGISTER`, informando um nome único e o intervalo de envio.
3. O servidor valida o registro e responde com `OK` ou `ERROR`.
4. Após `OK`, o agente envia mensagens `METRICS` pela mesma conexão TCP no intervalo configurado.
5. O servidor guarda as últimas 20 leituras por agente em memória e atualiza o painel.
6. Se a conexão for encerrada, o agente é removido do estado do servidor.
7. Se um agente registrado ficar sem enviar mensagens por **3 vezes seu intervalo**, o servidor encerra a conexão, envia `ERROR` com motivo `timeout` quando possível e remove o agente.

O servidor também aplica um timeout inicial de **10 segundos** para receber o `REGISTER` (valor padrão de `REGISTER_TIMEOUT`).

## Mensagens

### 1. REGISTER — agente para servidor

Deve ser a primeira mensagem da conexão.

```json
{"type": "REGISTER", "name": "agente-01", "interval": 5}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `type` | texto | Deve ser `REGISTER`. |
| `name` | texto não vazio | Nome único do agente. No cliente, o padrão é o hostname da máquina. |
| `interval` | número positivo | Intervalo de envio em segundos. |

### 2. OK — servidor para agente

Confirma que o registro foi aceito.

```json
{"type": "OK"}
```

### 3. ERROR — servidor para agente

Indica registro recusado ou timeout.

```json
{"type": "ERROR", "reason": "name already in use"}
```

Outros motivos previstos na implementação:

```json
{"type": "ERROR", "reason": "invalid REGISTER"}
```

```json
{"type": "ERROR", "reason": "timeout"}
```

Se um registro for inválido ou usar um nome já registrado, o servidor responde com `ERROR` e encerra aquela conexão. Uma mensagem `METRICS` inválida recebida **após o registro** é ignorada, sem necessariamente derrubar o agente.

### 4. METRICS — agente para servidor

Enviada periodicamente após o registro.

```json
{
  "type": "METRICS",
  "cpu": {
    "overall": 23.5,
    "cores": [20.1, 30.4, 18.0, 25.5]
  },
  "memory": {
    "total_mb": 16000,
    "used_mb": 8200,
    "free_mb": 7800
  }
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `type` | texto | Deve ser `METRICS`. |
| `cpu.overall` | número | Percentual geral de uso da CPU. |
| `cpu.cores` | lista de números | Percentual de utilização por núcleo lógico. |
| `memory.total_mb` | número | Memória RAM total em MB. |
| `memory.used_mb` | número | Memória RAM utilizada em MB. |
| `memory.free_mb` | número | Memória RAM fisicamente livre em MB. |

O nome do agente não precisa ser repetido em cada `METRICS`, pois o servidor associa as leituras à conexão registrada.

## Exemplo de uso da classe Connection

```python
from common.protocol import Connection

con = Connection(sock)
con.send({"type": "REGISTER", "name": "agente-01", "interval": 5})
resposta = con.receive()
# Resposta esperada para um registro aceito: {"type": "OK"}
con.close()
```

O método `send()` serializa um objeto Python como JSON UTF-8 e acrescenta a quebra de linha. O método `receive()` mantém um buffer interno para lidar com mensagens TCP fragmentadas ou múltiplas mensagens recebidas juntas, retornando `None` quando a outra extremidade fecha normalmente a conexão.

**Importante:** cada socket deve ser encapsulado por apenas uma instância de `Connection`, pois ela mantém o buffer de leitura da conexão.
