import sys
import threading
import time

lock_a = threading.Lock()
lock_b = threading.Lock()
começo = time.perf_counter()


def log(mensagem):
    print(f"[{time.perf_counter() - começo:4.2f}s] {mensagem}", flush=True)


def trabalhar(nome, primeiro, segundo, nome_primeiro, nome_segundo):
    log(f"{nome} quer o lock {nome_primeiro}")
    with primeiro:
        log(f"{nome} pegou o lock {nome_primeiro}")
        time.sleep(0.05)  # espera um pouco pra garantir que a outra thread pegue o dela
        log(f"{nome} quer o lock {nome_segundo}")
        with segundo:
            log(f"{nome} pegou o lock {nome_segundo}")
            log(f"{nome} concluiu!")


def main(corrigido):
    if corrigido:
        # os dois sempre pedem A primeiro e B depois -> não tem como dar ciclo
        pedidos = [("T1", lock_a, lock_b, "A", "B"),
                   ("T2", lock_a, lock_b, "A", "B")]
    else:
        # T2 pede na ordem inversa -> deadlock
        pedidos = [("T1", lock_a, lock_b, "A", "B"),
                   ("T2", lock_b, lock_a, "B", "A")]

    threads = [threading.Thread(target=trabalhar, args=p, daemon=True) for p in pedidos]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=3)  # não espera pra sempre, senão o programa nunca acabaria

    travadas = [t for t in threads if t.is_alive()]
    if travadas:
        log("DEADLOCK! Essas threads ainda estão vivas, presas esperando um lock:")
        for t in threading.enumerate():
            print("   ", t.name)
    else:
        log("Todo mundo terminou, sem deadlock.")


if __name__ == "__main__":
    main(corrigido="corrigido" in sys.argv)
