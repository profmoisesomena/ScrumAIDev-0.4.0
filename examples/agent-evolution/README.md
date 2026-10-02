# Example — Agent Evolution Lab with `/scope-idea`

## User input

```text
/scope-idea Quero construir um sistema que acompanhe a evolucao de agentes de IA. Inicialmente preciso registrar um agente, suas versoes, seus componentes e capacidades, e depois avaliar mudancas entre versoes.
```

## Expected ScrumAIDev interaction

### 1. Work Classification

```text
Recomendacao: HEAVY PROCESS
Motivo: novo produto, modelo de dominio ainda aberto e decisoes de versionamento/governanca relevantes.
Processo: Discovery+ → Requirements+ → Stories.

Voce pode aprovar ou alterar a classificacao.
```

### 2. Discovery proposal

O agente propoe Intent, Problem, Users, Desired Outcome, Success Criteria, IN/OUT/LATER, constraints, assumptions e perguntas bloqueantes.

O usuario pode editar qualquer secao antes de `PROBLEM READY`.

### 3. Requirements proposal

O agente apresenta FR/BR/NFR completos, cenarios e decisoes importantes. Exemplo:

```text
Derivei 7 FR, 5 BR e 3 NFR.
Decisao importante proposta: criar nova versao nao altera automaticamente a versao estavel.

Voce pode editar, adicionar, remover ou reclassificar qualquer item.
```

Somente depois dos ajustes e aprovacao o gate vira `REQUIREMENTS READY`.

### 4. Stories proposal (via `/create-user-story` — Passo 0, Modo Backlog)

Não existe um comando `/stories` separado: depois de `REQUIREMENTS_READY`, `/create-user-story` entra automaticamente no seu Passo 0 (Modo Backlog), propõe o menor backlog útil e um vertical slice inicial. O usuário pode dividir/unir/reordenar antes da materialização das Stories.

### 5. Agile Delivery → Engineering as Needed → Agentic Execution

A partir das Stories aprovadas, segue `/sprint-planning`, `/feature-development`, reviews, testes, deploy e retrospectiva — a engenharia entra somente na profundidade que a Story exigir, e a execução agêntica (geração de código, testes, PR) acontece dentro desses workflows já existentes, não como uma etapa nova.

## Nota

Este exemplo ilustra a experiência pretendida; não é um teste automatizado nem um resultado real de execução. Para uma comparação empírica real entre processos (ScrumAIDev vs. outro framework) usando este mesmo domínio, veja o projeto `agent-evolution-baseline`, que é independente deste repositório.
