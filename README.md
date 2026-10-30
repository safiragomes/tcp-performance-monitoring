# Monitoramento Distribuído de Desempenho — APS 01, Equipe 06

Projeto da disciplina **CIN0143 — Introdução aos Sistemas Distribuídos e Redes de Computadores**, do Centro de Informática (CIn) da Universidade Federal de Pernambuco (UFPE).

## Objetivo

Implementar um sistema distribuído cliente-servidor com **sockets TCP**, no qual múltiplos agentes coletam e enviam periodicamente informações de **CPU** (uso geral e por núcleo lógico) e **memória RAM** (total, utilizada e livre).

O servidor mantém conexões TCP persistentes, identifica cada agente, armazena as leituras em memória e apresenta um painel de monitoramento atualizado automaticamente no terminal.

## Tecnologias

- **Python 3** — testes realizados com Python **3.9.6** no macOS.
- **`socket` e `threading`** — comunicação TCP e execução concorrente.
- **`json`** — mensagens JSON codificadas em UTF-8 e delimitadas por quebra de linha.
- **`psutil`** — coleta de dados de CPU e memória RAM.

## Estrutura do projeto

```text
tcp-performance-monitoring/
├── agent/
│   ├── __init__.py
│   ├── collector.py        # Coleta de métricas
│   └── agent.py            # Agente TCP
├── server/
│   ├── __init__.py
│   ├── server.py           # Servidor TCP
│   ├── state.py            # Estado dos agentes
│   └── dashboard.py        # Painel no terminal
├── common/
│   ├── __init__.py
│   └── protocol.py         # Protocolo de comunicação
├── tests/
│   ├── test_protocol.py    # Testes do protocolo
│   ├── check_server.py     # Testes do servidor e do estado
│   └── simulate_agents.py  # Simulação de agentes
├── docs/
│   ├── protocol.md         # Documentação do protocolo
│   └── testing.md          # Procedimentos e resultados dos testes
├── requirements.txt
└── README.md
```

## Instalação

Abra um terminal **na raiz do repositório** e instale as dependências:

```bash
python3 -m pip install -r requirements.txt
```

> Os comandos abaixo usam `python3`, conforme a execução validada no macOS. Em outros ambientes, o executável pode ser `python`.

## Execução

Execute o servidor e cada agente em **terminais separados**, sempre a partir da raiz do projeto.

### 1. Iniciar o servidor

```bash
python3 -m server.server --port 5001
```

O servidor exibe o painel de monitoramento. Sem clientes registrados, o painel informa que há **zero agentes conectados**.

A porta é configurável. A porta `5001` foi utilizada nos testes porque a `5000` estava ocupada no ambiente de execução.

### 2. Iniciar o primeiro agente

Em outro terminal:

```bash
python3 -m agent.agent --host 127.0.0.1 --port 5001 --name agente-01 --interval 5
```

### 3. Iniciar mais dois agentes

Em dois novos terminais, execute:

```bash
python3 -m agent.agent --host 127.0.0.1 --port 5001 --name agente-02 --interval 3
```

```bash
python3 -m agent.agent --host 127.0.0.1 --port 5001 --name agente-03 --interval 4
```

O painel deve mostrar os agentes registrados, seus intervalos e as informações de CPU e memória recebidas.

**Atenção:** `127.0.0.1` indica o próprio computador. Para usar máquinas diferentes na mesma rede, é necessário configurar o servidor para escutar em um endereço acessível, utilizar o IP da máquina servidora no agente e verificar as regras do firewall. Esse cenário não foi validado nos testes registrados em `docs/testing.md`.

### 4. Encerrar os processos

No terminal de cada agente ou do servidor, pressione **Ctrl+C**. Se o servidor for reiniciado, os agentes precisam ser iniciados ou reconectados para voltar a aparecer no painel; a reconexão automática não foi verificada nos testes.

## Funcionamento

1. O agente estabelece uma conexão TCP com o servidor.
2. O agente envia uma mensagem `REGISTER`, contendo o nome e o intervalo configurado.
3. O servidor responde `OK` ou `ERROR`, conforme a validade do registro.
4. Após o registro, o agente envia mensagens `METRICS` periodicamente **pela mesma conexão TCP**.
5. O servidor armazena em memória as **últimas 20 leituras por agente** e atualiza o painel.
6. O painel apresenta CPU geral, uso por núcleo, memória total, utilizada e livre, além de informações da conexão.
7. Se um agente se desconectar ou permanecer sem enviar mensagens até o timeout, ele é removido da lista de conectados.

O timeout de inatividade é definido em função do intervalo de envio do agente (aproximadamente **3 × intervalo**). O protocolo completo está em [`docs/protocol.md`](docs/protocol.md).

## Testes

Os scripts automatizados podem ser executados na raiz do repositório. O teste do servidor cria seu próprio listener TCP em uma porta disponível, portanto **não é necessário iniciar o servidor manualmente** para executá-lo.

### Testes do protocolo

```bash
python3 tests/test_protocol.py
```

**Resultado observado:** 5 de 5 testes aprovados.

### Testes do servidor

```bash
python3 tests/check_server.py
```

**Resultado observado:** 10 de 10 testes aprovados. Entre os cenários verificados estão registro, mensagens inválidas, nomes duplicados, timeout, buffer de 20 leituras e concorrência com 20 threads.

### Testes manuais

Também foram executados **7 cenários de aceitação**, incluindo um agente, três agentes simultâneos, intervalos diferentes, desconexão com Ctrl+C, suspensão com Ctrl+Z, nome duplicado e reinicialização do servidor.

**Resultado observado:** 7 de 7 cenários aprovados.

**Resumo:** 22 testes/cenários executados e aprovados (7 manuais e 15 automatizados).

Os procedimentos, os resultados e as verificações ainda não realizadas estão documentados em [`docs/testing.md`](docs/testing.md). O arquivo `tests/simulate_agents.py` está presente no projeto, mas a simulação de dez agentes por um minuto não foi executada nesta validação.

## Limitações e observações

- As leituras são armazenadas **somente em memória** e não persistem após o encerramento do servidor.
- O painel é exibido no terminal; não há interface web.
- Os testes com múltiplos agentes foram realizados em processos separados **no mesmo computador**, não em máquinas físicas diferentes.
- O protocolo não implementa mecanismos próprios de autenticação ou criptografia; o projeto é destinado a demonstrações acadêmicas em ambientes confiáveis.
- A reconexão automática de agentes após a reinicialização do servidor não foi validada.
- Recomenda-se revisar a correspondência entre o valor da CPU geral e as medições por núcleo em `agent/collector.py`, conforme observação registrada nos testes.

## Integrantes e responsabilidades

- **Safira Moraes:** protocolo TCP e documentação do protocolo.
- **Leticia Staundiger:** coleta das métricas e simulação de agentes.
- **Laura Fonseca:** desenvolvimento do agente TCP.
- **Marcos Silva:** servidor TCP e armazenamento em memória.
- **Laís Saraiva:** painel de monitoramento, documentação de uso e registro dos testes.

