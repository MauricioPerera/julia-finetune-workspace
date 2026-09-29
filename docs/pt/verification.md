# O que foi verificado na versão 0.1.0

Ferramenta independente para adaptar decisões de seleção (`choice`) de Julia-1.
Modelo fixado na revisão `a85b127321d580d65176c89ced8273f305745d85` de
[SupersonicLabs/Julia-1](https://huggingface.co/SupersonicLabs/Julia-1).

## Testes realizados em 29 de setembro de 2026

- Instalação isolada e dependências sem conflitos: Windows/Python 3.14 e Ubuntu/Python 3.12, em CPU.
- Treinamento com pesos reais, gradientes finitos e não nulos e alterações nos pesos.
- Modelo original preservado, checkpoint ajustado salvo e recarregado pelo runtime de Julia, com previsões iguais.
- Métricas recalculadas pelo comando `verify`, usando novas inferências.
- Retomada após encerrar o processo: histórico e todos os tensores exatamente iguais aos de uma execução contínua.
- Retomada com dados modificados rejeitada.
- Sete testes de importação, validação, divisão por grupos e bloqueio de execuções simultâneas em ambas as plataformas.
- Capacidade opcional instalada em novas instâncias do Portable Agent Workspace, com validadores de estrutura, primeiro uso e contrato Julia aprovados.
- Instalação Linux a partir do pacote de distribuição e primeiro uso completo.

## Resultado do teste sintético

30 exemplos fictícios em espanhol: 18 para treinar, 6 para validar e 6 para testar.
Uma época, nove lotes. Foram treinados 3.699.073 parâmetros dos componentes de
decisão, mantendo o encoder congelado.

| Modelo | Acertos no teste |
|---|---|
| Original | 3 de 6 |
| Ajustado | 3 de 6 |

O teste confirmou o funcionamento da ferramenta. **Não demonstrou uma melhoria
na precisão.** Também não mede o desempenho com dados reais de um nicho nem a
preservação das capacidades multilíngues.

## Limites da primeira versão

- O procedimento verificado é o treinamento em CPU no modo `head`. O modo `full` é uma opção avançada sem teste completo de integração.
- Paráfrases e traduções relacionadas precisam de um identificador de grupo e revisão para evitar que apareçam tanto no treinamento quanto no teste.
- As versões das dependências estão fixadas; não há um catálogo de hashes de wheels para todas as plataformas.
- Os hashes detectam alterações em relação ao registro; não são assinaturas independentes.
- O comando `predict` usa probabilidades arredondadas da API legacy de Julia. Elas não devem ser interpretadas como certeza garantida.
- A integração com o workspace referencia caminhos locais. Movê-lo para outro computador exige reinstalar o ambiente e atualizar essas referências.
- Uma IA assistente precisa de acesso real a arquivos e terminal. A página web não executa o treinamento.

[Voltar ao guia](index.html) · [Ler o código](https://github.com/MauricioPerera/julia-finetune-workspace)
