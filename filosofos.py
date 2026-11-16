import sys
import threading
import time


NUM_FILOSOFOS = 5
REFEICOES = 3


def pensar(numero):
    print(f"Filósofo {numero} pensando.", flush=True)
    time.sleep(0.1)
    print(f"Filósofo {numero} com fome.", flush=True)


def filosofo_ingenuo(numero, garfos, barreira):
    esquerda = (numero - 1) % NUM_FILOSOFOS
    direita = numero
    pensar(numero)

    with garfos[esquerda]:
        print(f"Filósofo {numero} pegou o garfo {esquerda}.", flush=True)
        
        barreira.wait()

        print(f"Filósofo {numero} esperando o garfo {direita}.", flush=True)
        with garfos[direita]:
            print(f"Filósofo {numero} comendo.", flush=True)
            time.sleep(0.1)


def executar_ingenuo():
    garfos = [threading.Lock() for _ in range(NUM_FILOSOFOS)]
    barreira = threading.Barrier(NUM_FILOSOFOS + 1, timeout=5)
    threads = []

    for numero in range(NUM_FILOSOFOS):
        thread = threading.Thread(
            target=filosofo_ingenuo,
            args=(numero, garfos, barreira),
            daemon=True,
        )
        threads.append(thread)
        thread.start()

    barreira.wait()
    for thread in threads:
        thread.join(timeout=0.2)

    bloqueadas = sum(thread.is_alive() for thread in threads)
    print(f"Deadlock demonstrado. Threads ainda vivas: {bloqueadas}/{NUM_FILOSOFOS}.")


def filosofo_com_garcom(numero, garfos_livres, fila, garcom):
    esquerda = (numero - 1) % NUM_FILOSOFOS
    direita = numero

    for refeicao in range(1, REFEICOES + 1):
        pensar(numero)

        with garcom:
            print(f"Filósofo {numero} entrou na fila.", flush=True)
            fila.append(numero)

            while (
                fila[0] != numero
                or not garfos_livres[esquerda]
                or not garfos_livres[direita]
            ):
                garcom.wait()

            garfos_livres[esquerda] = False
            garfos_livres[direita] = False
            fila.pop(0)

            print(
                f"Filósofo {numero} comendo (refeição {refeicao}) "
                f"com os garfos {esquerda} e {direita}.",
                flush=True,
            )
            garcom.notify_all()

        try:
            time.sleep(0.1)
        finally:
            with garcom:
                garfos_livres[esquerda] = True
                garfos_livres[direita] = True
                print(f"Filósofo {numero} devolveu os dois garfos.", flush=True)
                garcom.notify_all()


def executar_corrigido():
    garfos_livres = [True] * NUM_FILOSOFOS
    fila = []
    garcom = threading.Condition()
    threads = []

    for numero in range(NUM_FILOSOFOS):
        thread = threading.Thread(
            target=filosofo_com_garcom,
            args=(numero, garfos_livres, fila, garcom),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Fim da versão corrigida.")


if __name__ == "__main__":
    argumentos = sys.argv[1:]

    if argumentos == [] or argumentos == ["ingenuo"]:
        executar_ingenuo()
    elif argumentos == ["corrigido"]:
        executar_corrigido()
    else:
        print("Use py filosofos.py ingenuo ou py filosofos.py corrigido.")
        sys.exit(1)