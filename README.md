# TDE — Programação Concorrente (Python)

**Integrantes do grupo**

- João Vitor Lima Cecilio
- Henrique Dias

[Vídeo da apresentação](https://www.youtube.com/watch?v=yQuWZgt2R5g)

## Como rodar

No Windows, abra um terminal na pasta do projeto e escolha o comando da parte que quer testar.

```powershell
py filosofos.py ingenuo
py filosofos.py corrigido
py contador.py
py deadlock.py
py deadlock.py corrigido
```

No Linux ou macOS, use `python3` no lugar de `py`.

## Parte 1 — Jantar dos Filósofos

### Versão ingênua

Cada filósofo pega um garfo e segura ele enquanto espera o segundo. Como o segundo garfo está com o vizinho, a espera forma um círculo e os cinco ficam bloqueados.

```text
Filósofo 4 esperando o garfo 4.
Filósofo 2 esperando o garfo 2.
Filósofo 0 esperando o garfo 0.
Filósofo 3 esperando o garfo 3.
Filósofo 1 esperando o garfo 1.
Deadlock demonstrado. Threads ainda vivas: 5/5.
```

### Versão corrigida com garçom

O garçom entrega os dois garfos juntos quando chega a vez do filósofo e os dois estão livres. Isso quebra a condição de **manter e esperar**, porque quem está esperando ainda está de mãos vazias. Cada novo pedido entra no fim da fila, dando vez a quem já estava esperando.

### Pseudocódigo da correção

```text
Para cada filósofo, repetir três vezes
    Pensar e entrar no fim da fila
    Esperar a vez e os dois garfos ficarem livres
    Reservar os dois garfos e sair da fila
    Comer
    Devolver os dois garfos e avisar quem está esperando
```

No teste, cada filósofo chegou à terceira refeição, totalizando 15 refeições. Estas são as linhas da última refeição de cada um.

```text
Filósofo 0 comendo (refeição 3) com os garfos 4 e 0.
Filósofo 2 comendo (refeição 3) com os garfos 1 e 2.
Filósofo 1 comendo (refeição 3) com os garfos 0 e 1.
Filósofo 4 comendo (refeição 3) com os garfos 3 e 4.
Filósofo 3 comendo (refeição 3) com os garfos 2 e 3.
Fim da versão corrigida.
```


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
