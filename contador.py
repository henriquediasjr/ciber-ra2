import threading
import time

NUM_THREADS = 8
INCREMENTOS = 200_000
ESPERADO = NUM_THREADS * INCREMENTOS

contador = 0
semaforo = threading.Semaphore(1)  # só 1 permissão = funciona como um cadeado


def incrementar_sem_proteção():
    global contador
    for _ in range(INCREMENTOS):
        valor = contador
        valor += 1
        time.sleep(0)  # dá chance pra outra thread entrar no meio (senão o GIL esconde o bug)
        contador = valor


def incrementar_com_semaforo():
    global contador
    for _ in range(INCREMENTOS):
        semaforo.acquire()
        try:
            valor = contador
            valor += 1
            time.sleep(0)  # mesma "demora", só que agora ninguém atrapalha
            contador = valor
        finally:
            semaforo.release()


def executar(tarefa):
    global contador
    contador = 0

    threads = [threading.Thread(target=tarefa) for _ in range(NUM_THREADS)]

    inicio = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    duracao = time.perf_counter() - inicio

    return contador, duracao


if __name__ == "__main__":
    print(f"{NUM_THREADS} threads x {INCREMENTOS} incrementos -> esperado {ESPERADO}\n")

    versoes = [
        ("Sem semáforo", incrementar_sem_proteção),
        ("Com semáforo", incrementar_com_semaforo),
    ]

    for nome, tarefa in versoes:
        for rodada in range(1, 4):
            obtido, duracao = executar(tarefa)
            perdidos = ESPERADO - obtido
            print(f"{nome} (rodada {rodada}): obtido={obtido} perdidos={perdidos} tempo={duracao:.2f}s")
        print()
