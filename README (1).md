# Escalonamento de Processos com Round Robin

> **Projeto Fase 01 — Sistemas Operacionais | UNIFACISA**  
> Simulação do algoritmo Round Robin em Python — P1=10, P2=5, P3=8, quantum=2.

Esse projeto implementa o algoritmo de escalonamento **Round Robin** do zero, em Python puro, sem nenhuma biblioteca externa. A ideia é simples: três processos disputam a CPU, e o sistema garante que nenhum deles fique "travando a fila" — cada um recebe sua fatia de tempo e passa a vez. O código mostra isso acontecendo ciclo por ciclo, em tempo real no terminal.

---

## Sumário

1. [O que é o Round Robin — e por que ele existe](#1-o-que-é-o-round-robin--e-por-que-ele-existe)
   - [A ideia central](#11-a-ideia-central)
   - [Como funciona na prática](#12-como-funciona-na-prática)
   - [Preempção — o SO no controle](#13-preempção--o-so-no-controle)
   - [O quantum — o parâmetro que muda tudo](#14-o-quantum--o-parâmetro-que-muda-tudo)
   - [Por que o Round Robin é tão usado](#15-por-que-o-round-robin-é-tão-usado)
2. [Como o programa funciona](#2-como-o-programa-funciona)
   - [Criando os processos](#21-criando-os-processos)
   - [A fila de prontos](#22-a-fila-de-prontos)
   - [Executando e finalizando](#23-executando-e-finalizando)
   - [O quantum em ação](#24-o-quantum-em-ação)
3. [Resultado da simulação](#3-resultado-da-simulação)
   - [Cenário](#31-cenário)
   - [Ciclo a ciclo](#32-ciclo-a-ciclo)
   - [Resumo final](#33-resumo-final)
   - [Diagrama de Gantt](#34-diagrama-de-gantt)
4. [Como rodar](#4-como-rodar)
5. [Estrutura do código](#5-estrutura-do-código)

---

## 1. O que é o Round Robin — e por que ele existe

### 1.1 A ideia central

Imagina um grupo de amigos esperando para usar o mesmo computador. Se uma pessoa sentar e ficar lá o tempo que quiser, os outros vão esperar eternamente. A solução óbvia? Todo mundo tem direito a um tempo fixo. Usou, levanta e vai pro fim da fila. Quando chegar a vez de novo, senta de novo.

É exatamente isso que o **Round Robin** faz com os processos de um sistema operacional.

Cada processo que quer usar a CPU entra numa fila. O escalonador pega o primeiro da fila, deixa ele rodar por um tempo fixo — o **quantum** — e então interrompe. Se o processo não terminou, ele volta pro fim da fila e espera sua vez. Se terminou, sai de vez. Isso se repete até todo mundo ter concluído.

O nome "Round Robin" vem do inglês e se refere exatamente a esse esquema circular de turnos — ninguém é mais importante que ninguém, todos recebem fatias iguais do recurso compartilhado.

---

### 1.2 Como funciona na prática

O ciclo de vida de um processo no Round Robin segue sempre o mesmo caminho:

```
  Chega no sistema
        ↓
  Entra na fila de prontos
        ↓
  Recebe a CPU por 'quantum' unidades
        ↓
   ┌────────────────────────┐
   │ Terminou antes do fim  │──→ Sai do sistema ✅
   │    do quantum?         │
   └────────────────────────┘
        │ Não
        ↓
   Foi interrompido (preempção)
        ↓
   Volta pro fim da fila
        ↓
   (aguarda próxima vez...)
```

Três coisas que vale fixar:

- **A fila é FIFO** — quem chegou primeiro, sai primeiro. Sem furar a fila.
- **Ninguém monopoliza** — mesmo que um processo demore muito, ele só ocupa a CPU por `quantum` unidades de cada vez.
- **Processos curtos terminam rápido** — se P2 precisa de só 5 unidades e o quantum é 2, ele termina em poucos ciclos enquanto P1 e P3 ainda estão "dando voltas" na fila.

---

### 1.3 Preempção — o SO no controle

Esse é um ponto que às vezes causa confusão, então vale explicar direito.

Em alguns algoritmos de escalonamento — como o FCFS (First Come, First Served) — o processo que recebe a CPU fica lá até acabar ou pedir alguma operação de I/O. O sistema operacional não interfere. Se um processo entrar num loop infinito, boa sorte para os outros.

O Round Robin é **preemptivo**. Isso significa que o sistema operacional tem autoridade total para interromper qualquer processo, mesmo que ele não tenha pedido nada. Quem executa essa "interrupção forçada" é um temporizador de hardware: quando o quantum começa, um relógio interno é ativado. Quando o tempo acaba, esse relógio dispara uma interrupção que devolve o controle para o SO.

O SO então faz uma **troca de contexto**: salva o estado atual do processo (em que instrução estava, valores dos registradores etc.), carrega o estado do próximo processo da fila, e manda ele rodar. Tudo isso transparente para os programas.

| | Não-preemptivo (ex: FCFS) | Preemptivo (Round Robin) |
|---|---|---|
| Quem controla a CPU | O processo em si | O sistema operacional |
| Pode ser interrompido à força? | Não | Sim, pelo quantum |
| Risco de travamento por um processo | Alto | Zero |
| Serve para sistemas interativos? | Não muito | Sim, muito bem |

---

### 1.4 O quantum — o parâmetro que muda tudo

O quantum parece um detalhe, mas define completamente o comportamento do sistema.

**Quantum muito pequeno** — digamos, 1 unidade. O sistema fica trocando de processo o tempo todo. Cada troca de contexto tem um custo (salvar e restaurar o estado do processo), e se o quantum for menor que esse custo, o sistema passa mais tempo fazendo gerência do que trabalhando de verdade. É como se você trocasse de tarefa tão rápido que nunca conseguisse terminar nenhuma.

**Quantum muito grande** — digamos, 100 unidades. Processos com pouco tempo de execução ficam esperando na fila por muito tempo enquanto o primeiro da fila ocupa a CPU. No limite (quantum infinito), o Round Robin vira FCFS — quem chegou primeiro fica até o fim, sem interrupção. Perde toda a graça.

**Quantum ideal** — é o equilíbrio. Em sistemas reais, ele costuma ficar entre 10ms e 100ms. A referência prática é: idealmente, 80% dos processos deveriam conseguir terminar dentro de um único quantum. Assim, a maioria não precisa nem voltar à fila.

```
   custo de overhead
         ↑
         │╲  quantum pequeno: mais trocas, mais overhead
         │ ╲
         │  ╲___________
         │              ‾‾‾‾‾‾‾‾  quantum ideal: overhead estável
         │
         └──────────────────────────→ tamanho do quantum
```

Neste projeto usamos `quantum = 2` — um valor pequeno, propositalmente escolhido para deixar bem visível a alternância entre os processos na saída do programa.

---

### 1.5 Por que o Round Robin é tão usado

Não é à toa que ele é o algoritmo de referência em sistemas de tempo compartilhado. Ele resolve um problema real de forma elegante:

**É justo.** Com `n` processos e quantum `q`, cada processo recebe `1/n` do tempo de CPU. Nenhum processo espera mais do que `(n-1) × q` unidades entre dois acessos à CPU — isso é uma garantia matemática, não uma esperança.

**Responde rápido.** Sistemas interativos — terminais, interfaces gráficas, servidores — precisam que qualquer processo possa responder logo. O Round Robin garante que todo processo terá a CPU em breve, independente do que os outros estejam fazendo.

**É previsível.** Saber que "nenhum processo vai esperar mais do que X unidades de tempo" é muito valioso para quem projeta sistemas. Algoritmos como o SJF, apesar de eficientes em média, podem fazer um processo esperar indefinidamente se sempre chegarem processos mais curtos.

**Não deixa ninguém para trás.** Mesmo um processo que demora muito (tipo nosso P1 com 10 unidades) sempre vai avançar — devagar, talvez, mas vai. Não existe starvation no Round Robin.

---

## 2. Como o programa funciona

### 2.1 Criando os processos

Cada processo é representado por um dicionário Python simples — uma estrutura que guarda tudo que o escalonador precisa saber sobre aquele processo:

```python
def criar_processo(pid, tempo_total):
    return {
        "pid": pid,                    # Nome do processo: "P1", "P2", "P3"
        "tempo_total": tempo_total,    # Quanto tempo ele precisa no total
        "tempo_restante": tempo_total, # Quanto falta ainda — vai diminuindo
        "finalizado_em": None,         # Em que instante terminou (None = ainda rodando)
    }
```

No `main`, os três processos do cenário são criados e jogados numa lista — que vai virar a fila de prontos:

```python
lista_processos = [
    criar_processo("P1", 10),
    criar_processo("P2", 5),
    criar_processo("P3", 8),
]
```

Nada sofisticado: é uma lista Python normal, operada como uma fila. O que importa é a lógica de quem entra e quem sai.

---

### 2.2 A fila de prontos

A fila de prontos é o coração do algoritmo. Ela determina quem executa, em que ordem, e quem volta após ser interrompido.

A implementação usa `list.pop(0)` para retirar o processo da frente e `list.append()` para colocar no fim — o comportamento clássico de uma fila FIFO:

```python
# Retira o primeiro da fila → vai executar
processo_atual = fila.pop(0)

# ... executa o processo ...

# Se não terminou, volta pro fim da fila
if processo_atual["tempo_restante"] > 0:
    fila.append(processo_atual)
# Se terminou, simplesmente não volta — some da simulação
```

Visualmente, a rotação da fila fica assim:

```
Início:    [P1] [P2] [P3]
Após c.1:  [P2] [P3] [P1]   ← P1 executou, voltou pro fim
Após c.2:  [P3] [P1] [P2]   ← P2 executou, voltou pro fim
Após c.3:  [P1] [P2] [P3]   ← P3 executou, voltou pro fim
...
```

Quando P2 termina (ciclo 8), ele simplesmente não volta:

```
Após c.8:  [P3] [P1]         ← P2 saiu de vez ✅
```

O `while fila:` no laço principal cuida disso automaticamente — quando a lista fica vazia, a simulação encerra.

---

### 2.3 Executando e finalizando

A função `executar_ciclo()` é onde a preempção acontece de verdade. Ela recebe o processo atual, o quantum e o relógio global, e devolve quanto tempo foi usado e o novo horário:

```python
def executar_ciclo(processo, quantum, tempo_atual):
    # A linha mais importante: executa o mínimo entre o quantum e o que resta
    # Se restam 1ut e o quantum é 2, executa só 1 — sem desperdiçar
    tempo_executado = min(quantum, processo["tempo_restante"])

    processo["tempo_restante"] -= tempo_executado
    tempo_atual += tempo_executado

    # Se zerou, registra o instante de conclusão
    if processo["tempo_restante"] == 0:
        processo["finalizado_em"] = tempo_atual

    return tempo_executado, tempo_atual
```

O `min(quantum, processo["tempo_restante"])` é o detalhe que faz toda a diferença. Sem ele, um processo com 1 unidade restante "ocuparia" 2 unidades do relógio global — o que é errado. Com ele, o processo usa exatamente o que precisa e libera a CPU sem desperdício.

---

### 2.4 O quantum em ação

Com `quantum = 2`, cada processo ganha no máximo 2 unidades por turno. Isso cria um padrão bem interessante:

- **P1** (10 ut) vai precisar de **5 turnos completos** — passa pela fila cinco vezes antes de terminar.
- **P2** (5 ut) vai precisar de **2 turnos completos + 1 parcial** — no último turno, só tem 1 unidade restante, então executa por 1 (não 2) e finaliza.
- **P3** (8 ut) vai precisar de **4 turnos completos** — passa pela fila quatro vezes.

Repara que P2, mesmo sendo o processo do meio na ordem de chegada, termina **antes de P3 e P1** — simplesmente porque é o menor. O Round Robin não privilegia nenhum processo, mas processos menores naturalmente terminam mais cedo ao acumular fatias.

Se tivéssemos usado `quantum = 10`, P1 monopolizaria a CPU e terminaria em t=10, antes de P2 e P3 rodarem pela primeira vez — o que seria muito menos justo. O valor pequeno do quantum aqui torna a rotação bem visível na saída do programa.

---

## 3. Resultado da simulação

### 3.1 Cenário

| Parâmetro | Valor |
|---|---|
| Algoritmo | Round Robin |
| Quantum | 2 unidades de tempo |
| P1 — tempo necessário | 10 unidades |
| P2 — tempo necessário | 5 unidades |
| P3 — tempo necessário | 8 unidades |
| Duração total da simulação | **23 unidades de tempo** |

---

### 3.2 Ciclo a ciclo

Cada linha representa um turno de execução. O relógio avança conforme os processos executam, e o `tempo_restante` de cada um vai caindo até chegar a zero.

| Ciclo | t início → fim | Processo | Executou | P1 restante | P2 restante | P3 restante | O que aconteceu |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 1 | 0 → 2 | **P1** | 2 ut | **8** | 5 | 8 | Preemptado, volta pra fila |
| 2 | 2 → 4 | **P2** | 2 ut | 8 | **3** | 8 | Preemptado, volta pra fila |
| 3 | 4 → 6 | **P3** | 2 ut | 8 | 3 | **6** | Preemptado, volta pra fila |
| 4 | 6 → 8 | **P1** | 2 ut | **6** | 3 | 6 | Preemptado, volta pra fila |
| 5 | 8 → 10 | **P2** | 2 ut | 6 | **1** | 6 | Preemptado, volta pra fila |
| 6 | 10 → 12 | **P3** | 2 ut | 6 | 1 | **4** | Preemptado, volta pra fila |
| 7 | 12 → 14 | **P1** | 2 ut | **4** | 1 | 4 | Preemptado, volta pra fila |
| 8 | 14 → 15 | **P2** | 1 ut | 4 | **0** | 4 | ✅ **P2 finalizado** em t=15 |
| 9 | 15 → 17 | **P3** | 2 ut | 4 | — | **2** | Preemptado, volta pra fila |
| 10 | 17 → 19 | **P1** | 2 ut | **2** | — | 2 | Preemptado, volta pra fila |
| 11 | 19 → 21 | **P3** | 2 ut | 2 | — | **0** | ✅ **P3 finalizado** em t=21 |
| 12 | 21 → 23 | **P1** | 2 ut | **0** | — | — | ✅ **P1 finalizado** em t=23 |

> `—` indica processo já concluído. Os valores em **negrito** na coluna de restante são do processo que rodou naquele ciclo.

**Repara no ciclo 8:** P2 tinha só 1 unidade restante, mas o quantum é 2. O algoritmo é inteligente o suficiente para não "cobrar" 2 unidades de quem precisa de 1 — executa exatamente o que falta e finaliza. Isso acontece graças ao `min(quantum, tempo_restante)` no código.

---

### 3.3 Resumo final

| Processo | Tempo de execução | Finalizou em | Ficou esperando |
|:---:|:---:|:---:|:---:|
| P1 | 10 ut | t = 23 | 13 ut na fila |
| P2 | 5 ut | t = 15 | 10 ut na fila |
| P3 | 8 ut | t = 21 | 13 ut na fila |

> O tempo de espera é calculado como: `instante de finalização − tempo total de execução`.  
> P2, por exemplo: terminou em t=15, executou 5ut, logo ficou `15 − 5 = 10ut` aguardando na fila ao longo da simulação.

P2 foi o mais rápido a terminar — não porque foi privilegiado, mas porque era o processo mais curto. O Round Robin não distingue processos, mas processos menores naturalmente acumulam suas fatias e concluem antes.

---

### 3.4 Diagrama de Gantt

O diagrama abaixo mostra quem estava na CPU em cada unidade de tempo. Cada `██` é 1 unidade de tempo em uso, cada `·` é 1 unidade aguardando na fila.

```
t   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22

P1  ██ ██ ·  ·  ·  ·  ·  ·  ██ ██ ·  ·  ·  ·  ██ ██ ·  ·  ·  ·  ·  ██ ██
P2  ·  ·  ██ ██ ·  ·  ·  ·  ·  ·  ██ ██ ·  ·  ·  ██ ·  ·  ·  ·  ·  ·  ·
P3  ·  ·  ·  ·  ██ ██ ·  ·  ·  ·  ·  ·  ██ ██ ·  ·  ·  ██ ██ ·  ·  ·  ·

                                              ↑             ↑         ↑
                                           P2 fim        P3 fim    P1 fim
                                           (t=15)        (t=21)    (t=23)
```

Dá pra ver claramente o padrão de alternância: nenhum processo ocupa dois blocos consecutivos (exceto nos instantes finais, quando os outros já saíram). É a equidade do Round Robin em forma visual.

---

## 4. Como rodar

Só precisa de Python instalado. Sem pip install, sem virtualenv, sem nada.

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/round-robin-so.git
cd round-robin-so

# Roda
python round_robin.py
```

A saída vai aparecer ciclo por ciclo no terminal, mostrando a fila, o processo em execução, o tempo restante de cada um e o momento exato em que cada processo finaliza. No final, um resumo com todos os instantes de conclusão.

**Versão mínima:** Python 3.6. Nenhuma dependência externa.

---

## 5. Estrutura do código

O código foi escrito para ser fácil de ler e de modificar. Cada função tem uma responsabilidade clara:

```
round_robin.py
│
├── criar_processo(pid, tempo_total)
│   └── Monta o dicionário de dados de um processo
│
├── executar_ciclo(processo, quantum, tempo_atual)
│   └── Roda um processo por no máximo 'quantum' unidades
│       Implementa o min(quantum, restante) — a preempção de verdade
│
├── imprimir_cabecalho(processos, quantum)
│   └── Cabeçalho da simulação com os processos carregados
│
├── imprimir_estado_fila(fila, tempo_atual)
│   └── Mostra quem está na fila antes de cada ciclo
│
├── imprimir_ciclo(processo, tempo_executado, tempo_atual)
│   └── Resultado de um ciclo: tempo usado, restante, se finalizou
│
├── imprimir_resultado_final(processos, tempo_total_sistema)
│   └── Tabela de resumo no final da simulação
│
└── round_robin(processos, quantum)
    └── O laço principal — fila FIFO, pop/append, while até esvaziar
```

Quer experimentar? Muda os valores de P1, P2, P3 ou do quantum no `main` e roda de novo. O comportamento muda bastante dependendo do quantum escolhido — vale testar com quantum=1, quantum=5 e ver a diferença.

---

## Referências

- TANENBAUM, Andrew S. **Sistemas Operacionais Modernos**. 4. ed. Pearson, 2016.
- SILBERSCHATZ, Abraham et al. **Fundamentos de Sistemas Operacionais**. 9. ed. LTC, 2015.
- STALLINGS, William. **Sistemas Operacionais**. 8. ed. Pearson, 2017.

---

*Projeto Fase 01 — Sistemas Operacionais | UNIFACISA — Campina Grande, PB.*
