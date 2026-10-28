# Protocolo agente ↔ servidor

- Transporte: TCP, porta padrão **5000**.
- Formato: uma mensagem JSON por linha, terminada em `\n`, codificada em UTF-8.
- Implementação: `comum/protocolo.py` (classe `Conexao`).

## Fluxo

1. O agente conecta e envia **REGISTER**.
2. O servidor responde **OK** ou **ERRO**. Em caso de ERRO, fecha a conexão.
3. Depois do OK, o agente envia **METRICAS** a cada `intervalo` segundos.
4. Se o servidor ficar 3 × `intervalo` sem receber nada, considera o agente
   desconectado e o remove da lista.

## Mensagens

### REGISTER (agente → servidor)
Sempre a primeira mensagem da conexão.

```json
{"tipo": "REGISTER", "nome": "agente-ana", "intervalo": 5}
```

| Campo | Tipo | Descrição |
|---|---|---|
| nome | texto | Nome único do agente (padrão: hostname) |
| intervalo | número > 0 | Segundos entre os envios de METRICAS |

### OK / ERRO (servidor → agente)
Resposta ao REGISTER.

```json
{"tipo": "OK"}
{"tipo": "ERRO", "motivo": "nome ja em uso"}
```

### METRICAS (agente → servidor)
Enviada a cada intervalo, depois do registro. O servidor associa a mensagem à
conexão, então o nome não é repetido.

```json
{"tipo": "METRICAS",
 "cpu": {"geral": 23.5, "nucleos": [20.1, 30.4, 18.0, 26.2]},
 "mem": {"total_mb": 16000, "usada_mb": 8200, "livre_mb": 7800}}
```

| Campo | Tipo | Descrição |
|---|---|---|
| cpu.geral | número | % de uso médio da CPU (0 a 100) |
| cpu.nucleos | lista de números | % de uso de cada núcleo |
| mem.total_mb | inteiro | Memória total em MB |
| mem.usada_mb | inteiro | Memória usada em MB |
| mem.livre_mb | inteiro | Memória disponível em MB |

## Como usar no código

```python
from comum.protocolo import Conexao

con = Conexao(sock)
con.enviar({"tipo": "OK"})
msg = con.receber()      # dicionário, ou None se o outro lado fechou
```

Cada socket deve ter **uma única** `Conexao`, porque ela guarda o buffer.