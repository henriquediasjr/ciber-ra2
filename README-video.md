# Roteiro do vídeo: Threads, semáforos e deadlock

Duração estimada: 7 a 9 minutos falando com calma.

**Antes de gravar:** abra `contador.py`, `deadlock.py` e um terminal na pasta do projeto. Aumente a fonte do editor. Rode cada programa uma vez para saber o que vai aparecer. O `contador.py` demora cerca de 1 minuto, então avise na gravação que vai pular a espera.

| # | Trecho | Duração |
|---|---|---|
| 1 | Introdução | 30s |
| 2 | Conceitos rápidos | 45s |
| 3 | Contador sem proteção | 2min |
| 4 | Contador com semáforo | 2min |
| 5 | Deadlock | 2min |
| 6 | Correção do deadlock | 1min |
| 7 | Encerramento | 30s |

As falas abaixo são um guia. Fale com as suas palavras, mas passe por todos os pontos.

---

## 1. Introdução
**Mostrar:** a pasta do projeto, com os arquivos `contador.py`, `deadlock.py` e o README.

> "Olá, eu sou [seu nome], e nesse vídeo eu vou explicar o código que fiz para as Partes 2 e 3 do trabalho de sistemas operacionais, sobre threads, semáforos e deadlock."
>
> "Usei Python. São dois programas: o `contador.py`, que mostra uma condição de corrida e como corrigi com um semáforo, e o `deadlock.py`, que reproduz um deadlock e mostra a correção. Vou mostrar o código e rodar cada um."

## 2. Conceitos rápidos
**Mostrar:** pode continuar na pasta, ou mostrar o topo do `contador.py`.

> "Antes de começar, só dois conceitos. Uma *condição de corrida* acontece quando várias threads mexem no mesmo dado ao mesmo tempo e o resultado depende da ordem em que elas são executadas, que é imprevisível."
>
> "Um *semáforo* é um contador de permissões. Para entrar numa região protegida, a thread faz `acquire`, que pega uma permissão. Se não tem permissão sobrando, ela espera. Quando termina, faz `release` e devolve a permissão. Se o semáforo começa com uma única permissão, ele é binário e funciona como um cadeado: só uma thread entra por vez."

## 3. Parte 2: Contador sem proteção
**Mostrar:** `contador.py`, do topo até a função `incrementar_sem_proteção`.

> "No topo eu defino os parâmetros: 8 threads, 200 mil incrementos por thread. Então o valor esperado no final é 8 vezes 200 mil, 1 milhão e 600 mil. O contador é uma variável global compartilhada por todas as threads."

**Mostrar:** a função `incrementar_sem_proteção`.

> "Essa é a versão sem proteção. Olhem que, em vez de escrever `contador += 1`, eu separei em três passos: leio o valor, somo um, e depois escrevo de volta. Na verdade o Python já faz isso por baixo, eu só deixei explícito para ficar claro onde está o problema."
>
> "O problema é que esses três passos não são atômicos, ou seja, uma thread pode ser interrompida no meio. Imagina que o contador vale 10. A thread 1 lê 10. Antes de escrever, a thread 2 também lê 10. As duas somam um e as duas gravam 11. Foram feitos dois incrementos, mas o contador só subiu um. Esse incremento perdido tem nome: *lost update*."
>
> "Tem uma observação importante: coloquei um `time.sleep(0)` entre a soma e a escrita. Ele faz a thread ceder a vez para outra. Eu precisei disso porque o Python tem o GIL, uma trava global que deixa só uma thread executar código Python por vez, e ele faz a troca de threads raramente. Sem o sleep, a corrida quase não aparecia nos meus testes. Com ele, o bug fica visível, que é o objetivo do experimento."

**Mostrar:** a função `executar` e o bloco `if __name__ == "__main__"`.

> "A função `executar` cria as 8 threads, dispara todas, espera todas terminarem com `join`, e mede o tempo. No final ela devolve o valor do contador e a duração. O bloco principal roda cada versão 3 vezes e imprime o valor esperado, o obtido e quantos incrementos foram perdidos."

**Rodar:** `python3 contador.py` (corte a espera na edição e volte quando aparecerem as linhas).

> "Vamos ver a versão sem semáforo. Esperado: 1 milhão e 600 mil. Obtido: mais ou menos 200 mil, e nas 3 rodadas o valor foi parecido. Ou seja, mais de 85% dos incrementos se perderam. Isso mostra bem como a corrida é grave."

## 4. Parte 2: Contador com semáforo
**Mostrar:** a função `incrementar_com_semaforo` e a linha que cria o `semaforo`.

> "Agora a versão correta. No topo do arquivo eu criei `threading.Semaphore(1)`, um semáforo com uma permissão, ou seja, binário."
>
> "Na função, antes de mexer no contador, a thread chama `acquire`. Se outra thread já está lá dentro, ela espera. Depois eu uso `try` e `finally` para garantir que o `release` sempre aconteça, mesmo se der algum erro no meio. Sem isso, um erro deixaria o semáforo preso para sempre e travaria todo mundo."
>
> "Repararam que o `sleep(0)` continua dentro da região protegida? É de propósito: o trabalho é o mesmo, só que agora nenhuma outra thread consegue entrar no meio. Isso é a *exclusão mútua*: o ler, somar e escrever vira uma operação indivisível."

**Mostrar:** o resultado da versão com semáforo no terminal.

> "O resultado: obtido 1 milhão e 600 mil nas 3 rodadas, zero perdidos. Correto!"
>
> "Mas olhem o tempo. A versão sem proteção levou uns 6 segundos, e a com semáforo levou mais de 20. Isso é o *trade-off*: para ser correta, as threads agora passam uma de cada vez pela região crítica, então perdemos o paralelismo. Além disso, tem o custo de bloquear e acordar threads o tempo todo. Em resumo, correção custa desempenho."
>
> "Sobre justiça, ou *fairness*: o semáforo do Python não garante ordem de chegada, ou seja, não é FIFO. Em Java dá para pedir um semáforo justo, que atende na ordem, mas isso deixa o programa ainda um pouco mais lento."
>
> "E por fim, a questão da *visibilidade*. Não basta só uma thread de cada vez: é preciso que o valor escrito por uma thread seja visto pela próxima. Em Java isso é garantido pela relação *happens-before*: o `release` de uma thread acontece antes do `acquire` da outra. Em Python, o GIL e os locks internos do semáforo funcionam como barreiras de memória implícitas, e garantem a mesma coisa."

## 5. Parte 3: Deadlock
**Mostrar:** `deadlock.py`, do topo até a função `trabalhar`.

> "Agora a Parte 3, o deadlock. Deadlock é quando um grupo de threads fica parado para sempre porque cada uma espera algo que está com outra. Aqui eu criei dois locks, o A e o B."
>
> "A função `trabalhar` pega um primeiro lock, espera 50 milissegundos, e então tenta pegar o segundo. Esse `sleep` é importante: ele garante que, antes de qualquer thread pedir o segundo lock, a outra já tenha pego o primeiro. Isso deixa o deadlock previsível. A função também imprime um log em cada passo, com o tempo, para a gente acompanhar."

**Mostrar:** a função `main`, ramo que não é corrigido.

> "Na função `main`, quando não está corrigido, a Thread 1 pede A e depois B, e a Thread 2 pede B e depois A. Ordens opostas. No final tem um `join` com timeout de 3 segundos, senão o programa ficaria travado para sempre, e depois eu verifico quais threads ainda estão vivas."

**Rodar:** `python3 deadlock.py`

> "Vamos rodar. T1 pegou o lock A. T2 pegou o lock B. Agora T1 quer o B, que está com a T2, e T2 quer o A, que está com a T1. Cada uma espera a outra, e nenhuma anda. Nunca aparece 'concluiu'. Depois dos 3 segundos o programa avisa: deadlock, as threads continuam vivas, presas."
>
> "Isso acontece porque as quatro condições de Coffman estão presentes ao mesmo tempo:"
> - "*Exclusão mútua*: cada lock só pode estar com uma thread."
> - "*Manter e esperar*: cada thread segura um lock enquanto espera pelo outro."
> - "*Não preempção*: ninguém consegue tomar um lock à força."
> - "*Espera circular*: T1 espera T2, que espera T1, formando um ciclo."

## 6. Parte 3: Correção
**Mostrar:** o ramo `if corrigido` da função `main`.

> "Para corrigir, eu impus uma *ordem global* de aquisição: todas as threads sempre pedem o lock A primeiro e o B depois. Aqui, as duas tarefas usam `lock_a, lock_b` nessa mesma ordem."

**Rodar:** `python3 deadlock.py corrigido`

> "Rodando a versão corrigida: T1 pega A. T2 também quer A, mas A está ocupado, então ela espera. T1 pega B, conclui, e libera os dois. Só então T2 pega A, depois B, e conclui também. As duas terminaram e a mensagem final diz que não houve deadlock."
>
> "A condição de Coffman que foi quebrada é a *espera circular*. Com uma ordem fixa, não dá para formar um ciclo: quem segura A nunca fica esperando por alguém que segura B e quer A. Como basta quebrar uma das quatro condições para eliminar o deadlock, isso resolve."

## 7. Encerramento
> "Resumindo: na Parte 2, vimos que sem sincronização o contador perde incrementos por causa da condição de corrida, e que o semáforo binário resolve, garantindo exclusão mútua, mas com perda de desempenho. Na Parte 3, vimos como um deadlock acontece quando duas threads pedem locks em ordem oposta, e como uma ordem global de aquisição quebra a espera circular e resolve o problema."
>
> "Todo o código e os resultados estão no README do projeto. Obrigado por assistir!"

---

## Dicas
- Se esquecer uma fala, tudo bem: o importante é explicar o **porquê** de cada coisa, não só o que o código faz.
- Se alguma explicação ficar longa, corte: os pontos essenciais são lost update, exclusão mútua, trade-off de desempenho, as 4 condições de Coffman e a ordem global.
- No Mac, Cmd+Shift+5 grava a tela e o microfone.
- Os números (200 mil, 6 s, 20 s) podem variar na sua máquina: fale os que aparecerem na tela.
