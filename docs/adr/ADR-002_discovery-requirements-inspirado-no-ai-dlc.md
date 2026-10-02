# ADR-002: Work Classification, Discovery e Requirements inspirados no AI-DLC, com nomenclatura própria

## Status

Aceita

## Contexto

O ScrumAIDev, na sua forma anterior a esta decisão, não tinha uma fase explícita de investigação de problema antes da User Story: `/create-user-story` partia diretamente de "descreva a funcionalidade desejada". Isso é uma lacuna real de maturidade do framework, não uma escolha filosófica deliberada — Scrum clássico também pressupõe um backlog já refinado, mas não prescreve como chegar lá.

Durante uma análise comparativa entre ScrumAIDev e o AWS AI-DLC (AI-Driven Development Life Cycle), observamos que o AI-DLC resolve essa lacuna com uma fase de Ideation (intent framing, stakeholders, feasibility, scope, success criteria) seguida de uma fase de Inception com Requirements Analysis estruturado em múltiplas perspectivas, ambas com gates de aprovação humana.

## Decisão

Adicionamos ao ScrumAIDev uma camada de **Work Classification (LIGHT/NORMAL/HEAVY)** e, para NORMAL/HEAVY, dois artefatos compactos e editáveis — **Discovery** e **Requirements** — com checkpoints obrigatórios de "Review & Adjust" antes de qualquer gate (`PROBLEM READY`, `REQUIREMENTS READY`) ser aprovado.

Isto **não é uma cópia** do AI-DLC:

- **Conceitos, não código ou texto.** Discovery e Requirements Analysis são vocabulário padrão de engenharia de requisitos e produto (BABOK/IIBA, Design Thinking, Dual-Track Agile, Rational Unified Process) — mais antigo que o próprio AI-DLC, que também os herdou dessa tradição. Nenhum arquivo de stage, código TypeScript ou texto do AI-DLC foi copiado; os workflows `.agents/workflows/discover.md` e `.agents/workflows/requirements.md` são prosa original do ScrumAIDev.
- **Granularidade deliberadamente menor.** O AI-DLC usa 7 stages de Ideation + 9 de Inception como pipeline formal. O ScrumAIDev absorve o mesmo valor em **dois artefatos** (`discovery.md`, `requirements.md`) com profundidade que varia por classificação, não uma sequência fixa de estágios obrigatórios.
- **Nomenclatura própria, escolhida deliberadamente diferente do AI-DLC:**
  - O comando de entrada se chama **`/scope-idea`**, não `/start`. Duas razões: (1) o ScrumAIDev já usa `/init-project` para "início de projeto"; um segundo comando chamado "start" colidiria conceitualmente com esse vocabulário existente; (2) mesmo o AI-DLC não usa `/start` — o comando dele é `/aidlc [scope]` — então "start" não tinha nem a defesa de ser um termo do AI-DLC preservado por reconhecimento; era apenas um nome genérico sem identidade própria.
  - **Não existe um comando `/stories` separado.** Em vez de duplicar o que `/create-user-story` já faz, a materialização do backlog a partir de Requirements aprovados foi incorporada como um passo condicional (Passo 0 — Modo Backlog) dentro do próprio `/create-user-story`, evitando redundância de comandos e reaproveitando vocabulário que o ScrumAIDev já tinha antes desta decisão.
  - `discover` e `requirements` mantiveram nomes curtos e genéricos por serem termos de mercado, não porque o AI-DLC os usa dessa forma.

## Alternativas Consideradas

| Alternativa | Vantagens | Riscos / Custos |
|---|---|---|
| Não fazer nada (manter `/create-user-story` como único ponto de entrada) | Zero esforço | Mantém uma lacuna real de investigação de problema; o AI-DLC "venceria" essa dimensão por ausência de mecanismo, não por mérito de processo |
| Adotar a nomenclatura e a granularidade do AI-DLC como estão (`/start`, `/discover`, `/requirements`, `/stories`, stages fixos) | Familiaridade para quem já conhece o AI-DLC | Colide com `/init-project`; duplica `/create-user-story`; passa a impressão de reskin do AI-DLC em vez de evolução própria; nomes escolhidos sem identidade do ScrumAIDev |
| **Adotar os conceitos, com nomenclatura e granularidade próprias do ScrumAIDev (escolhida)** | Preenche a lacuna real; identidade própria preservada; reaproveita `/create-user-story` em vez de duplicar; nenhuma dependência de licença ou nomenclatura de terceiros | Exige manter a documentação de proveniência (este ADR) para que a inspiração fique registrada de forma transparente |

## Aspecto legal

Direito autoral protege expressão (texto, código), não ideias, conceitos, métodos ou processos (dicotomia ideia-expressão). Classificar trabalho por risco/complexidade, ter uma fase de descoberta antes de requisitos, e exigir revisão humana antes de aprovar uma proposta não são elementos apropriáveis por nenhum framework — são práticas de engenharia de requisitos e produto de uso comum. Nenhum código, texto ou estrutura de arquivo do AI-DLC foi copiado; nenhuma licença ou permissão precisa ser solicitada para usar os conceitos. Este ADR existe por honestidade de proveniência (prática acadêmica e de engenharia), não por exigência legal.

## Consequências

- O ScrumAIDev passa a ter uma fase de investigação de problema e requisitos proporcional à classificação do trabalho, sem virar um pipeline cerimonial.
- `/init-project` e `/scope-idea` continuam com responsabilidades distintas e não sobrepostas.
- `/create-user-story` ganha um passo condicional novo (Modo Backlog) em vez de um comando irmão duplicado.
- Futuras inspirações externas (AI-DLC, Spec Kit ou outros) devem seguir o mesmo critério: absorver o conceito, não o nome nem a cerimônia, e registrar a proveniência em ADR.

## Rastreabilidade

- User Story: N/A
- Spec: N/A
- Contract: N/A
- BDD: N/A
- Nivel ScrumAIDev: 0 (decisão de processo/governança do próprio framework)
