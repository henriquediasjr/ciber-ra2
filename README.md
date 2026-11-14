# Partes 2 e 3 — Threads, semáforos e deadlock (Python)

Rodar: `python3 contador.py`, `python3 deadlock.py` e `python3 deadlock.py corrigido`.

## Parte 2 — Contador concorrente (T=8 threads, M=200.000, esperado = 1.600.000)

Arquivo: `contador.py`. O incremento é feito em 3 passos (ler, somar, escrever) com um `time.sleep(0)` no meio
(cede o GIL) para a corrida ficar observável no Python.

| Versão | Execução | Esperado | Obtido | Tempo |
|---|---|---|---|---|
| Sem sincronização | 1 | 1.600.000 | 200.064 | 8,51 s |
| Sem sincronização | 2 | 1.600.000 | 200.017 | 7,58 s |
| Sem sincronização | 3 | 1.600.000 | 200.003 | 8,40 s |
| Semáforo binário | 1 | 1.600.000 | 1.600.000 | 22,86 s |
| Semáforo binário | 2 | 1.600.000 | 1.600.000 | 22,31 s |
| Semáforo binário | 3 | 1.600.000 | 1.600.000 | 18,25 s |

### Discussão
- **Por que perde incrementos:** `count = count + 1` não é atômico (ler → somar → escrever). Duas threads leem o mesmo
  valor, ambas gravam valor+1, e um incremento se perde (*lost update*). Aqui, como a thread cede o GIL entre a leitura
  e a escrita, quase todas as atualizações são sobrescritas.
- **Por que o semáforo corrige:** com 1 permissão, só uma thread por vez executa a seção crítica (exclusão mútua). O
  ler-somar-escrever vira indivisível, então o resultado é sempre T×M.
- **Trade-off de throughput:** a versão correta foi ~2,5–3× mais lenta: as threads serializam na seção crítica e ainda há o
  custo de bloquear/acordar threads (troca de contexto). Correção custa desempenho. O `threading.Semaphore` do Python
  não garante justiça FIFO (o `Semaphore(fair=true)` do Java sim, ao custo de ainda menos throughput).
- **Visibilidade/ordenação:** o `release()` de uma thread *acontece-antes* do `acquire()` seguinte de outra (happens-before
  em Java). Assim, a escrita de `count` feita por quem liberou fica visível a quem adquire. Em Python, o GIL e os
  locks internos do semáforo funcionam como barreiras de memória implícitas, dando essa mesma garantia.
- Obs.: sem o `sleep(0)`, no Python 3.15 do teste a corrida quase não aparecia (o GIL raramente troca no meio do `+=`).

## Parte 3 — Deadlock

Arquivo: `deadlock.py`. T1 pega A depois B; T2 pega B depois A, com `sleep(50ms)` entre as aquisições.

### Log da versão que trava (`python3 deadlock.py`)
```
[0.00s] T1 quer o lock A
[0.00s] T2 quer o lock B
[0.00s] T1 pegou o lock A
[0.00s] T2 pegou o lock B
[0.05s] T1 quer o lock B
[0.05s] T2 quer o lock A
[6.01s] DEADLOCK! Essas threads ainda estão vivas, presas esperando um lock:
    MainThread
    Thread-1 (trabalhar)
    Thread-2 (trabalhar)
```
Nunca aparece "T1 concluiu" nem "T2 concluiu": as duas threads continuam vivas, bloqueadas para sempre.

### Condições de Coffman presentes
1. **Exclusão mútua:** cada lock só pode ser de uma thread por vez.
2. **Manter-e-esperar:** T1 segura A e espera B; T2 segura B e espera A.
3. **Não preempção:** um lock não pode ser tomado à força.
4. **Espera circular:** T1 → B (de T2) → A (de T1): ciclo.

### Correção (`python3 deadlock.py corrigido`)
Ambas as threads sempre adquirem **A antes de B**:
```
[0.00s] T1 quer o lock A
[0.00s] T1 pegou o lock A
[0.00s] T2 quer o lock A
[0.05s] T1 quer o lock B
[0.05s] T1 pegou o lock B
[0.05s] T1 concluiu!
[0.05s] T2 pegou o lock A
[0.11s] T2 quer o lock B
[0.11s] T2 pegou o lock B
[0.11s] T2 concluiu!
[0.11s] Todo mundo terminou, sem deadlock.
```
Condição quebrada: **espera circular**. Com ordem global, não existe ciclo no grafo de espera: quem pegou A nunca
espera por alguém que segura B e quer A.
