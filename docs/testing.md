# Roteiro e Resultados dos Testes — APS 01, Equipe 06

**Disciplina:** CIN0143 — Introdução aos Sistemas Distribuídos e Redes de Computadores  

**Instituição:** Universidade Federal de Pernambuco (UFPE) — Centro de Informática  

**Projeto:** Sistema Distribuído de Monitoramento de Desempenho  

**Responsável pela documentação e execução dos testes:** Lais Saraiva  

**Data dos testes:** 30/10/2026  

**Commit de referência:** `f73f2ac`

---

## 1. Objetivo

Este documento apresenta os procedimentos e os resultados dos testes realizados no Sistema Distribuído de Monitoramento de Desempenho, desenvolvido pela Equipe 06 como parte da APS 01.

O objetivo dos testes é verificar o funcionamento das principais funcionalidades do sistema, incluindo:

- Comunicação cliente-servidor utilizando sockets TCP.
- Registro e identificação dos agentes conectados.
- Coleta e transmissão periódica de métricas de CPU e memória RAM.
- Configuração de diferentes intervalos de monitoramento.
- Atendimento simultâneo de múltiplos agentes.
- Armazenamento das métricas em memória.
- Atualização automática do painel de monitoramento.
- Tratamento de desconexões e agentes silenciosos.
- Validação de mensagens recebidas.
- Controle de concorrência e integridade dos dados.
- Reinicialização do servidor.

Os testes foram realizados manualmente e por meio de scripts automatizados disponibilizados no repositório.

---

## 2. Ambiente de Testes

| Componente | Configuração |
|---|---|
| Sistema operacional | macOS |
| Linguagem de programação | Python |
| Versão do Python | 3.9.6 |
| Biblioteca de monitoramento | psutil 7.2.2 |
| Protocolo de transporte | TCP |
| Formato das mensagens | JSON delimitado por quebra de linha |
| Endereço do servidor | 127.0.0.1 |
| Porta dos testes manuais | 5001 |
| Intervalos utilizados nos testes manuais | 3, 4 e 5 segundos |
| Intervalo da simulação de estresse | 2 segundos |
| Ambiente de desenvolvimento | Visual Studio Code |
| Commit de referência | f73f2ac |
| Data da execução | 30/10/2026 |

**Observação:** os testes manuais com múltiplos agentes foram executados em terminais diferentes do mesmo computador. Portanto, comprovam a execução simultânea de processos clientes, mas não substituem um teste de comunicação entre computadores físicos distintos.

O commit `f73f2ac` corresponde à referência inicial do projeto. Os arquivos da P5 foram posteriormente salvos no commit local `7f05257`, na branch `ajustes-finais-aps01`. As correções subsequentes da coleta, do protocolo e do simulador ainda precisam ser registradas em commit e enviadas ao GitHub. O hash final deverá ser atualizado após a integração.

---

## 3. Preparação do Ambiente

Todos os comandos foram executados a partir da raiz do repositório `tcp-performance-monitoring`.

### 3.1. Instalação das dependências

Comando utilizado:

`python3 -m pip install -r requirements.txt`

**Resultado:** a biblioteca `psutil` foi instalada com sucesso.

### 3.2. Inicialização do servidor

Comando utilizado:

`python3 -m server.server --port 5001`

**Resultado:** o servidor iniciou corretamente e apresentou o painel de monitoramento, inicialmente sem agentes conectados.

A porta 5000 foi testada inicialmente, porém estava ocupada por outro processo no macOS, produzindo a mensagem `Address already in use`.

Por esse motivo, os testes manuais foram realizados utilizando a porta 5001.

### 3.3. Inicialização dos agentes

Os agentes foram iniciados em terminais separados, utilizando os seguintes comandos:

**Agente 01 — Intervalo de 5 segundos**

`python3 -m agent.agent --host 127.0.0.1 --port 5001 --name agente-01 --interval 5`

**Agente 02 — Intervalo de 3 segundos**

`python3 -m agent.agent --host 127.0.0.1 --port 5001 --name agente-02 --interval 3`

**Agente 03 — Intervalo de 4 segundos**

`python3 -m agent.agent --host 127.0.0.1 --port 5001 --name agente-03 --interval 4`

**Resultado:** os três agentes foram registrados e suas métricas apareceram no painel do servidor.

---

## 4. Testes Manuais de Aceitação

Os testes a seguir foram realizados para validar o comportamento do sistema em situações de funcionamento normal e de falha.

| ID | Cenário | Resultado observado | Situação |
|---|---|---|---|
| T01 | Um agente conectado | O agente foi registrado e suas métricas foram exibidas no painel. | APROVADO |
| T02 | Três agentes simultâneos | O servidor exibiu três agentes conectados, cada um identificado separadamente. | APROVADO |
| T03 | Intervalos diferentes | Os agentes enviaram atualizações periódicas compatíveis com os intervalos configurados. | APROVADO |
| T04 | Desconexão com Ctrl+C | O agente encerrado foi removido da lista e os demais continuaram funcionando. | APROVADO |
| T05 | Agente silencioso | O agente suspenso deixou de enviar métricas e foi removido pelo servidor. | APROVADO |
| T06 | Nome duplicado | O servidor recusou o segundo registro com o mesmo nome. | APROVADO |
| T07 | Reinicialização do servidor | O servidor reiniciou, apresentou o painel vazio e aceitou uma nova conexão. | APROVADO |

### T01 — Conexão de um agente

**Procedimento:**

1. Iniciar o servidor TCP.
2. Executar o agente-01.
3. Aguardar o registro e o envio das métricas.
4. Observar as informações apresentadas no painel.

**Resultado esperado:** o agente deve aparecer na lista de conectados, apresentando métricas de CPU e memória RAM.

**Resultado observado:** o servidor registrou o agente-01 e apresentou CPU geral, porcentagem por núcleo, memória total, memória utilizada e memória livre.

As informações foram atualizadas automaticamente.

**Situação: APROVADO.**

### T02 — Três agentes simultâneos

**Procedimento:**

1. Manter o servidor em execução.
2. Iniciar três agentes com nomes distintos.
3. Aguardar o recebimento das métricas.
4. Verificar a quantidade de agentes conectados e suas informações.

**Resultado esperado:** o servidor deve atender simultaneamente aos três agentes, mantendo suas informações individualizadas.

**Resultado observado:** o painel apresentou `Agentes conectados: 3` e exibiu os agentes 01, 02 e 03 com suas métricas.

Foram observadas atualizações sucessivas sem interrupção do monitoramento.

**Situação: APROVADO.**

### T03 — Intervalos de envio diferentes

**Procedimento:**

1. Configurar o agente-01 com intervalo de 5 segundos.
2. Configurar o agente-02 com intervalo de 3 segundos.
3. Configurar o agente-03 com intervalo de 4 segundos.
4. Observar os horários de atualização das métricas.

**Resultado esperado:** cada agente deve enviar suas métricas de acordo com o intervalo configurado.

**Resultado observado:** os registros de recebimento apresentaram atualizações periódicas compatíveis com os intervalos definidos.

Os agentes continuaram sendo monitorados simultaneamente.

**Situação: APROVADO.**

### T04 — Desconexão normal de um agente

**Procedimento:**

1. Manter vários agentes conectados.
2. Selecionar o terminal do agente-02.
3. Pressionar `Ctrl+C`.
4. Observar o painel do servidor.

**Resultado esperado:** o servidor deve remover o agente encerrado da lista, sem interromper as conexões dos demais.

**Resultado observado:** o agente-02 deixou de aparecer entre os conectados, enquanto os agentes restantes continuaram enviando informações.

**Situação: APROVADO.**

### T05 — Timeout de agente silencioso

**Procedimento:**

1. Iniciar três agentes.
2. Selecionar o agente-02, com intervalo de 3 segundos.
3. Pressionar `Ctrl+Z` para suspender temporariamente o processo.
4. Observar o comportamento do servidor.
5. Retomar posteriormente o processo utilizando `fg`.

**Resultado esperado:** após um período sem receber mensagens, o servidor deve considerar o agente desconectado e removê-lo da lista.

De acordo com o protocolo do projeto, o timeout corresponde a três vezes o intervalo configurado.

**Resultado observado:** após a suspensão do agente-02, o painel passou de três para dois agentes conectados.

Os agentes 01 e 03 continuaram sendo monitorados.

Ao retomar o agente suspenso, ocorreu a mensagem `Broken pipe`, indicando que ele tentou utilizar uma conexão que já havia sido encerrada pelo servidor.

O tempo exato do timeout não foi medido durante esse teste manual. Entretanto, o comportamento de remoção foi comprovado.

**Situação: APROVADO.**

### T06 — Recusa de nome duplicado

**Procedimento:**

1. Manter o agente-01 conectado.
2. Iniciar outro agente utilizando o mesmo nome.
3. Verificar a resposta do servidor.

**Resultado esperado:** o servidor deve rejeitar a segunda tentativa de registro, preservando o agente original.

**Resultado observado:** o servidor retornou a mensagem `name already in use`, recusando o registro duplicado.

O agente original permaneceu conectado.

**Situação: APROVADO.**

### T07 — Reinicialização do servidor

**Procedimento:**

1. Manter o servidor funcionando com agentes conectados.
2. Encerrar o servidor utilizando `Ctrl+C`.
3. Reiniciar o servidor na porta 5001.
4. Verificar a inicialização do painel.
5. Executar um novo agente chamado `agente-teste`.
6. Observar o recebimento das métricas.

**Resultado esperado:** o servidor deve conseguir reiniciar e voltar a aceitar conexões TCP.

**Resultado observado:** após a reinicialização, o painel apresentou zero agentes conectados.

Em seguida, o agente-teste foi registrado e suas métricas passaram a ser exibidas e atualizadas normalmente.

O teste demonstrou que o servidor voltou a aceitar novas conexões após a reinicialização. Não foi verificada reconexão automática dos agentes anteriores.

**Situação: APROVADO.**

---

## 5. Testes Automatizados do Protocolo

Os testes do protocolo foram executados por meio do arquivo `tests/test_protocol.py`.

**Comando utilizado:**

`python3 tests/test_protocol.py`

### Resultados

| Teste | Funcionalidade validada | Situação |
|---|---|---|
| test_accents | Envio e recebimento de caracteres acentuados | APROVADO |
| test_closed_connection_returns_none | Tratamento do encerramento da conexão | APROVADO |
| test_message_split_in_pieces | Recebimento de mensagens fragmentadas | APROVADO |
| test_single_message | Envio e recebimento de uma mensagem JSON | APROVADO |
| test_two_messages_in_one_send | Tratamento de duas mensagens recebidas juntas | APROVADO |

**Resultado final observado:** `todos os testes passaram`.

**Total: 5 testes executados e 5 aprovados.**

Os resultados demonstram o funcionamento dos mecanismos básicos de codificação, envio, recebimento e separação das mensagens sobre o fluxo TCP.

---

## 6. Testes Automatizados do Servidor

Os testes do servidor foram executados por meio do arquivo `tests/check_server.py`.

**Comando utilizado:**

`python3 tests/check_server.py`

### Resultados

| ID | Funcionalidade validada | Situação |
|---|---|---|
| S01 | Registro de agente e armazenamento de leitura | APROVADO |
| S02 | Recusa de nomes duplicados | APROVADO |
| S03 | Tratamento de mensagens inválidas | APROVADO |
| S04 | Validação do comando REGISTER | APROVADO |
| S05 | Armazenamento limitado às últimas 20 leituras | APROVADO |
| S06 | Remoção de agente após desconexão | APROVADO |
| S07 | Timeout de agente silencioso | APROVADO |
| S08 | Timeout sem registro inicial | APROVADO |
| S09 | Reutilização de nome após desconexão | APROVADO |
| S10 | Concorrência com 20 threads | APROVADO |

**Resultado final observado:** `todos os testes do servidor passaram`.

**Total: 10 testes executados e 10 aprovados.**

### 6.1. Validação de mensagens

O servidor foi submetido a mensagens JSON inválidas, estruturas inesperadas e comandos de registro incorretos.

As entradas inválidas foram tratadas sem derrubar o processo principal do servidor.

### 6.2. Armazenamento de métricas

O teste automatizado enviou múltiplas leituras para verificar se o servidor armazenava somente as últimas 20 medições de cada agente.

O limite foi respeitado.

### 6.3. Timeout automatizado

Foi simulado um agente com intervalo de 0,3 segundo.

O servidor detectou a ausência de mensagens após aproximadamente 0,9 segundo e removeu o agente, retornando uma resposta de erro por timeout.

### 6.4. Concorrência

Foi realizado um teste com 20 threads, cada uma executando 500 operações de atualização e consulta ao estado.

O teste terminou sem falhas nas verificações e confirmou a manutenção do limite de 20 leituras para cada agente.

Esse resultado valida o cenário de concorrência implementado no teste, sem constituir garantia de ausência de falhas em qualquer carga possível.

---

## 7. Testes Adicionais e Verificações Pendentes

| Verificação | Resultado |
|---|---|
| Painel com zero agentes conectados | APROVADO |
| Painel com um agente conectado | APROVADO |
| Painel com três agentes simultâneos | APROVADO |
| Atualização periódica das métricas | APROVADO |
| Teste de concorrência com 20 threads | APROVADO |
| Buffer de 20 leituras por agente | APROVADO |
| Simulação de 10 agentes por um minuto | APROVADO |
| Comparação direta das métricas com o monitor do macOS | NÃO EXECUTADO |
| Teste com computadores físicos diferentes | NÃO EXECUTADO |
| Teste isolado da independência da cópia retornada por snapshot() | NÃO EXECUTADO |

### 7.1. Simulação de estresse com dez agentes

**Comando executado:**

```bash
python3 tests/simulate_agents.py --port 5001
```

**Configuração:** dez agentes simulados, duração configurada de 60 segundos, intervalo de 2 segundos entre envios e agente `simulated-agent-3` configurado para ficar silencioso após metade da duração.

**Resultado observado:** os dez agentes foram registrados com sucesso. O painel do servidor exibiu `Agentes conectados: 10`, com métricas simuladas recebidas periodicamente. Depois que o agente 3 interrompeu os envios, o painel passou para `Agentes conectados: 9`, enquanto os demais continuaram ativos. Ao final, o simulador informou `Simulacao encerrada` e o encerramento das conexões.

**Situação: APROVADO.** As métricas desse teste são valores fictícios: ele valida o atendimento simultâneo, o fluxo de mensagens e a remoção por inatividade, mas não a precisão das medições de CPU e RAM.

Esta simulação foi executada **além dos 22 testes e cenários** contabilizados nas seções anteriores.

As verificações não executadas foram registradas separadamente e não foram consideradas aprovadas.

---

## 8. Observações Técnicas

### 8.1. Exibição de horários

O painel apresenta os horários de conexão e de última mensagem utilizando timestamps Unix.

Esses valores representam instantes de tempo, mas podem ser convertidos para o formato convencional de data e hora para melhorar a legibilidade.

### 8.2. CPU geral e uso por núcleo

Nas medições iniciais, a porcentagem da CPU geral diferiu da média aritmética dos valores exibidos por núcleo porque eram realizadas leituras em momentos distintos.

O arquivo `agent/collector.py` foi atualizado para coletar os percentuais de todos os núcleos em uma única chamada a `psutil.cpu_percent(interval=0.1, percpu=True)` e calcular a média geral a partir desses valores. Após a alteração, a coleta foi executada novamente: CPU geral de **47,9%** para uma lista de dez núcleos cuja média é aproximadamente **47,9%**. Os cinco testes de protocolo e os dez testes de servidor foram reexecutados com sucesso.

A mudança foi validada localmente na branch `ajustes-finais-aps01` e ainda deve ser incluída no commit final desta branch.

### 8.3. Memória RAM

O painel apresentou informações de memória total, utilizada e livre em MB.

A coleta foi ajustada para preencher `free_mb` com `psutil.virtual_memory().free`, representando a memória fisicamente livre. No macOS, esse valor pode ser pequeno mesmo quando há memória recuperável de caches. Portanto, **memória fisicamente livre não equivale a memória disponível para novas aplicações**. A alteração foi validada com uma execução de `collect_metrics()`.

### 8.4. Persistência dos dados

O sistema armazena as métricas em memória.

Dessa forma, as leituras armazenadas são perdidas quando o servidor é encerrado ou reiniciado. Esse comportamento está de acordo com a proposta de armazenamento em memória adotada pelo grupo.

### 8.5. Ambiente distribuído

Os testes demonstraram conexões TCP simultâneas utilizando diferentes processos clientes na mesma máquina.

A comunicação entre máquinas físicas distintas não foi testada nesta etapa.

---

## 9. Resumo Geral dos Testes

| Categoria | Executados | Aprovados | Reprovados |
|---|---:|---:|---:|
| Testes manuais de aceitação | 7 | 7 | 0 |
| Testes automatizados do protocolo | 5 | 5 | 0 |
| Testes automatizados do servidor | 10 | 10 | 0 |
| **TOTAL** | **22** | **22** | **0** |

**Resultado geral: todos os 22 testes executados foram aprovados.**

Além dos 22 testes e cenários contabilizados acima, foi concluída **uma simulação adicional de estresse com dez agentes durante 60 segundos**, também aprovada. Essa simulação não altera a contagem dos testes automatizados de protocolo e servidor.

O resultado se refere aos cenários efetivamente realizados, não às verificações adicionais que permaneceram pendentes.

---

## 10. Conclusão

Os testes realizados demonstraram o funcionamento das principais funcionalidades do Sistema Distribuído de Monitoramento de Desempenho da Equipe 06.

O servidor recebeu métricas de CPU e memória RAM de múltiplos agentes, manteve os registros separados e apresentou os dados no painel com atualizações periódicas.

Também foram observados comportamentos adequados em situações de desconexão, timeout, nomes duplicados e reinicialização do servidor.

Os scripts automatizados confirmaram o funcionamento dos mecanismos do protocolo TCP, das validações do servidor, do armazenamento limitado das leituras e da sincronização dos dados compartilhados no cenário de concorrência testado.

Os 22 testes e cenários originalmente previstos foram concluídos com sucesso. A simulação adicional com dez agentes também foi concluída com resultado aprovado.

As verificações adicionais ainda não realizadas e os pontos de melhoria identificados permanecem documentados para consulta.

---

## 11. Registro Final da Execução

- **Data dos testes:** 30/10/2026
- **Responsável:** Lais Saraiva
- **Sistema operacional:** macOS
- **Python:** 3.9.6
- **psutil:** 7.2.2
- **Porta dos testes manuais:** 5001
- **Commit de referência:** `f73f2ac`
- **Testes manuais aprovados:** 7/7
- **Testes automatizados do protocolo:** 5/5
- **Testes automatizados do servidor:** 10/10
- **Resultado geral:** 22/22 testes executados aprovados
- **Simulação adicional de estresse:** 10 agentes, 60 segundos, intervalo de 2 segundos — APROVADA
- **Commit local com arquivos da P5:** `7f05257`
- **Branch de correções:** `ajustes-finais-aps01`
- **Commit final da entrega:** a preencher após o envio ao GitHub
