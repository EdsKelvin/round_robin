# =============================================================================
# ESCALONAMENTO DE PROCESSOS - ROUND ROBIN
# Projeto Fase 01 - Sistemas Operacionais | UNIFACISA
# =============================================================================
# Cenário: P1=10, P2=5, P3=8 | Quantum=2
# =============================================================================


def criar_processo(pid, tempo_total):
    """
    Cria e retorna um dicionário representando um processo.

    Um processo é modelado como um dicionário contendo:
      - pid          : identificador único do processo (ex: "P1")
      - tempo_total  : tempo de CPU necessário para concluir o processo
      - tempo_restante: quanto tempo de CPU ainda falta executar
      - finalizado_em: instante de tempo global em que o processo terminou
                       (None enquanto ainda não terminou)

    Parâmetros:
        pid (str)        : nome/identificador do processo
        tempo_total (int): unidades de tempo necessárias para concluir

    Retorna:
        dict: estrutura de dados do processo
    """
    return {
        "pid": pid,
        "tempo_total": tempo_total,
        "tempo_restante": tempo_total,
        "finalizado_em": None,
    }


def executar_ciclo(processo, quantum, tempo_atual):
    """
    Simula a execução de um processo por no máximo 'quantum' unidades de tempo.

    O processo recebe a CPU pelo tempo do quantum. Se o tempo restante for
    menor que o quantum, o processo apenas conclui seu tempo restante
    (escalonamento preemptivo: o processo é interrompido ao fim do quantum,
    ou termina antes se concluir sua execução).

    Parâmetros:
        processo    (dict): dicionário do processo (criado por criar_processo)
        quantum     (int) : máximo de unidades de tempo por fatia (time slice)
        tempo_atual (int) : instante global de tempo antes deste ciclo

    Retorna:
        tempo_executado (int): quantas unidades de tempo foram efetivamente usadas
        tempo_atual     (int): instante global atualizado após o ciclo
    """
    # O processo executa no mínimo 0 e no máximo 'quantum' unidades
    tempo_executado = min(quantum, processo["tempo_restante"])

    # Desconta o tempo executado do tempo restante do processo
    processo["tempo_restante"] -= tempo_executado

    # Avança o relógio global
    tempo_atual += tempo_executado

    # Se o tempo restante chegou a zero, o processo finalizou neste instante
    if processo["tempo_restante"] == 0:
        processo["finalizado_em"] = tempo_atual

    return tempo_executado, tempo_atual


def imprimir_cabecalho(processos, quantum):
    """
    Exibe o cabeçalho da simulação com as informações iniciais dos processos.

    Parâmetros:
        processos (list): lista de dicionários de processo
        quantum   (int) : valor do quantum definido
    """
    print("=" * 60)
    print("   SIMULAÇÃO DE ESCALONAMENTO - ROUND ROBIN")
    print("   UNIFACISA | Sistemas Operacionais")
    print("=" * 60)
    print(f"\n  Quantum definido: {quantum} unidades de tempo\n")
    print("  Processos carregados:")
    for p in processos:
        print(f"    [{p['pid']}] Tempo total = {p['tempo_total']} unidades")
    print("\n" + "=" * 60)
    print("  INÍCIO DA SIMULAÇÃO")
    print("=" * 60)


def imprimir_estado_fila(fila, tempo_atual):
    """
    Exibe o estado atual da fila de prontos antes de cada ciclo.

    Parâmetros:
        fila        (list): processos que ainda não terminaram
        tempo_atual (int) : relógio global no momento da exibição
    """
    nomes = [p["pid"] for p in fila]
    print(f"\n  [t={tempo_atual}] Fila de prontos: {' → '.join(nomes)}")


def imprimir_ciclo(processo, tempo_executado, tempo_atual):
    """
    Exibe os detalhes de execução de um ciclo (um quantum de um processo).

    Parâmetros:
        processo        (dict): processo que acabou de executar
        tempo_executado (int) : unidades usadas neste ciclo
        tempo_atual     (int) : relógio global após o ciclo
    """
    pid = processo["pid"]
    restante = processo["tempo_restante"]

    status = "✔ FINALIZADO" if restante == 0 else f"Restante: {restante} ut"

    print(
        f"    → Executando {pid} | "
        f"Executou: {tempo_executado} ut | "
        f"{status} | "
        f"[t global = {tempo_atual}]"
    )

    # Aviso destacado quando o processo termina
    if restante == 0:
        print(f"    ★ {pid} concluído no instante t={processo['finalizado_em']}!")


def imprimir_resultado_final(processos, tempo_total_sistema):
    """
    Exibe o resumo final após todos os processos terem sido concluídos.

    Parâmetros:
        processos            (list): lista completa de processos
        tempo_total_sistema  (int) : instante em que o último processo terminou
    """
    print("\n" + "=" * 60)
    print("  SIMULAÇÃO CONCLUÍDA — TODOS OS PROCESSOS FINALIZARAM")
    print("=" * 60)
    print("\n  Resumo por processo:")
    print(f"  {'Processo':<12} {'Tempo Total':<15} {'Finalizado em'}")
    print("  " + "-" * 40)
    for p in processos:
        print(
            f"  {p['pid']:<12} {p['tempo_total']:<15} t = {p['finalizado_em']}"
        )
    print("\n" + "=" * 60)
    print(f"  Tempo total de execução do sistema: {tempo_total_sistema} unidades")
    print("=" * 60 + "\n")


def round_robin(processos, quantum):
    """
    Executa o algoritmo de escalonamento Round Robin.

    Funcionamento:
      1. Todos os processos entram na fila de prontos.
      2. O escalonador retira o primeiro processo da fila.
      3. O processo executa por no máximo 'quantum' unidades de tempo.
      4. Se ainda tiver tempo restante, volta ao fim da fila.
      5. Se terminar, é marcado como finalizado e removido definitivamente.
      6. O ciclo continua até a fila de prontos ficar vazia.

    Esta é uma implementação preemptiva: nenhum processo monopoliza a CPU
    por mais do que 'quantum' unidades por vez.

    Parâmetros:
        processos (list): lista de dicionários criados por criar_processo()
        quantum   (int) : fatia de tempo máxima por ciclo

    Retorna:
        int: tempo total de execução do sistema (quando o último processo terminou)
    """
    # Relógio global: conta as unidades de tempo decorridas desde o início
    tempo_atual = 0

    # Fila de prontos: todos os processos começam aguardando a CPU
    # Usamos uma lista como fila FIFO (First In, First Out)
    fila = list(processos)  # cópia da lista original para não modificar a original

    imprimir_cabecalho(processos, quantum)

    # -----------------------------------------------------------------------
    # LAÇO PRINCIPAL — continua enquanto houver processos na fila de prontos
    # -----------------------------------------------------------------------
    while fila:
        # Mostra o estado atual da fila antes do próximo ciclo
        imprimir_estado_fila(fila, tempo_atual)

        # Retira o primeiro processo da fila (política FIFO do Round Robin)
        processo_atual = fila.pop(0)

        # Executa o processo pelo quantum (ou pelo restante, se for menor)
        tempo_executado, tempo_atual = executar_ciclo(
            processo_atual, quantum, tempo_atual
        )

        # Exibe o resultado deste ciclo na tela
        imprimir_ciclo(processo_atual, tempo_executado, tempo_atual)

        # Se ainda tem tempo restante, o processo volta ao FIM da fila
        # (preempção: foi interrompido pelo fim do quantum)
        if processo_atual["tempo_restante"] > 0:
            fila.append(processo_atual)
        # Se tempo_restante == 0, o processo está concluído e NÃO volta à fila

    # Retorna o instante em que o sistema finalizou todos os processos
    return tempo_atual


# =============================================================================
# PONTO DE ENTRADA DO PROGRAMA
# =============================================================================
if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # 1. DEFINIÇÃO DO QUANTUM
    # -------------------------------------------------------------------------
    QUANTUM = 2  # fatia de tempo máxima por ciclo, conforme especificação

    # -------------------------------------------------------------------------
    # 2. CRIAÇÃO DOS PROCESSOS
    #    Cada processo é criado com seu PID e tempo total de execução necessário
    # -------------------------------------------------------------------------
    lista_processos = [
        criar_processo("P1", 10),  # Processo 1: precisa de 10 unidades de tempo
        criar_processo("P2", 5),   # Processo 2: precisa de  5 unidades de tempo
        criar_processo("P3", 8),   # Processo 3: precisa de  8 unidades de tempo
    ]

    # -------------------------------------------------------------------------
    # 3. EXECUÇÃO DO ALGORITMO ROUND ROBIN
    # -------------------------------------------------------------------------
    tempo_final = round_robin(lista_processos, QUANTUM)

    # -------------------------------------------------------------------------
    # 4. EXIBIÇÃO DO RESULTADO FINAL
    # -------------------------------------------------------------------------
    imprimir_resultado_final(lista_processos, tempo_final)
