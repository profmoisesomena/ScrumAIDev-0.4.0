# Análise Automática de Exemplos para Sprint Planning

Esta pasta permite que você utilize **análise automática de exemplos** para gerar automaticamente o product backlog, roadmap e planejamento de sprint baseado em código, designs ou documentação existentes.

---

## 🎯 Como Funciona

Ao colocar exemplos nesta pasta, o workflow de sprint planning pode analisá-los e gerar automaticamente:

- ✅ **User stories** baseadas nas features identificadas no código/design
- ✅ **Product backlog** organizado em epics
- ✅ **Roadmap** com organização de sprints
- ✅ **Estimativas** de story points

---

## 📁 Formatos Suportados

### ⭐ Formato Principal: Arquivos ZIP do Figma

O **formato principal e recomendado** são arquivos ZIP exportados do Figma contendo o código do projeto:

- **Arquivos `.zip` do Figma Dev Mode** - Exportação completa com código-fonte
- Contém toda a estrutura do projeto
- Inclui componentes, assets e código gerado
- **Exemplo incluído neste repositório:** `MeetingFlow-MPI.zip`

**Como exportar do Figma:**
1. Abra seu design no Figma
2. Acesse o **Dev Mode** (ícone `</>`)
3. Selecione o frame ou projeto completo
4. Clique em **"Export"** → **"Code"** → **"Download ZIP"**
5. Salve o arquivo ZIP nesta pasta

### Formatos Complementares

Você também pode incluir para enriquecer a análise:

#### 1. Screenshots e Imagens
- Designs exportados do Figma (`.png`, `.jpg`, `.pdf`)
- Mockups de interfaces
- Fluxos de usuário capturados
- Diagramas de arquitetura

#### 2. Código-Fonte Adicional
- Arquivos `.js`, `.py`, `.java`, `.tsx`, `.vue`, etc.
- Protótipos funcionais
- APIs ou backend de exemplo
- Componentes de frontend

#### 3. Documentação
- Especificações de features (`.md`, `.txt`)
- Requisitos funcionais
- Casos de uso descritos
- Diagramas técnicos

---

## 🚀 Como Usar

### Passo 1: Adicione seus exemplos

**Opção A: Arquivo ZIP do Figma (Recomendado)**

Exporte seu projeto do Figma como ZIP e coloque nesta pasta:

```bash
# 1. Exportar do Figma Dev Mode
# - Abra seu design no Figma
# - Acesse o Dev Mode (ícone </> no canto superior)
# - Selecione o projeto/frame
# - Clique em "Export" → "Code" → "Download ZIP"

# 2. Mover para a pasta
cp ~/Downloads/Seu-Projeto.zip examples/figma/

# 3. Pronto! O arquivo ZIP contém todo o código do projeto
```

**Opção B: Arquivos Complementares**

```bash
# Adicionar screenshots, documentação extra, etc.
cp -r /caminho/para/screenshots/* examples/figma/
cp OVERVIEW.md examples/figma/
```

### Passo 2: Execute o workflow de sprint planning

No chat do seu agente de IA, execute:

```
/sprint-planning
```

### Passo 3: Use o prompt de análise automática

Caso deseje, durante o **passo 1.5** do workflow, ocorre análise automática de insumos.
Se você tem designs do Figma, mockups, código de exemplo ou documentação que represente o projeto a ser desenvolvido:

#### a) Adicione os exemplos na pasta destinada a esse fim.

Coloque seus arquivos em `examples/figma/`:
- 📦 **Arquivo ZIP do Figma** (.zip) - **Formato principal recomendado**
  - Exportado do Figma Dev Mode com código completo
- 📸 Imagens exportadas do Figma (.png, .jpg, .pdf)
- 🖼️ Screenshots de interfaces
- 💻 Código de exemplo ou protótipos (.js, .py, .tsx, etc.)
- 📄 Documentos descritivos (.md, .txt)

**Dica:** O arquivo ZIP do Figma é o mais completo - contém toda a estrutura do projeto.


ocorrerá um pompt no seguinte formato:
```
Analise os exemplos na pasta examples/figma/ e:
1. Se houver arquivo ZIP, extraia e analise todo o código do projeto
2. Identifique todas as features e funcionalidades visíveis/implementadas
3. Crie uma lista completa de user stories necessárias
4. Organize as stories em epics lógicos
5. Sugira um roadmap de sprints para implementação
6. Estime story points baseado na complexidade aparente
7. Gere um product_backlog.md completo baseado nesta análise
8. Identifique dependências técnicas entre as stories
```

### Passo 4: Revise e ajuste o backlog gerado

A IA gerará o backlog completo, mas você pode e deve:
- ✏️ Editar user stories para maior clareza
- 📊 Ajustar estimativas de story points
- 🎯 Reorganizar prioridades
- ➕ Adicionar stories adicionais
- ➖ Remover ou consolidar stories duplicadas

---

## 💡 Melhores Práticas

### ✅ Para Melhores Resultados

**Organize os exemplos de forma clara:**
```
examples/figma/
├── 01-autenticacao/         # Agrupe por feature
│   ├── login.png
│   ├── signup.png
│   └── auth-api.js
├── 02-dashboard/
│   ├── dashboard-layout.png
│   └── dashboard-component.tsx
└── OVERVIEW.md              # Descrição geral do projeto
```

**Inclua um arquivo OVERVIEW.md:**
```markdown
# Visão Geral do Projeto

Sistema de gestão de tarefas com as seguintes funcionalidades principais:
- Autenticação de usuários
- Dashboard com métricas
- CRUD de tarefas
- Sistema de notificações
...
```

**Nomeie arquivos descritivamente:**
- ✅ `tela-login-com-google.png`
- ✅ `api-autenticacao.js`
- ❌ `Captura de tela 2026-02-12 123456.png`
- ❌ `arquivo.js`

### ⚠️ Evite

- Exemplos muito genéricos ou abstratos
- Código sem contexto ou comentários
- Muitos arquivos desorganizados (agrupe por feature)
- Designs sem descrição do que representam

---

## 📝 Exemplo Prático

### Exemplo Real Incluído: MeetingFlow-MPI

Esta pasta já contém um **exemplo real** que você pode usar para testar:

```
examples/figma/
├── MeetingFlow-MPI.zip
│   └── [Código completo do projeto exportado do Figma]
└── readme.md
```

**Para testar:**
1. Execute `/sprint-planning`
2. No passo 1.5, use o prompt sugerido
3. A IA analisará o arquivo ZIP e poderá gerar backlog completo ou propor `copia_integral_frontend` quando o ZIP trouxer um app navegável.

### Estrutura Típica de um ZIP do Figma

Quando você exporta do Figma Dev Mode, o ZIP geralmente contém:

```
Seu-Projeto.zip
├── components/
│   ├── Button.jsx
│   ├── Input.jsx
│   ├── Card.jsx
│   └── ...
├── pages/
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   └── ...
├── assets/
│   ├── icons/
│   └── images/
├── styles/
│   ├── globals.css
│   └── components.css
├── package.json
└── README.txt
```

### Resultado Esperado

Ao analisar o **MeetingFlow-MPI.zip** (ou qualquer arquivo ZIP do Figma), a IA pode gerar:

**Epics baseados na arquitetura:**
- EPIC-001: Dashboard e indicadores de reuniões
- EPIC-002: Gestão de regiões e participantes
- EPIC-003: Cadastro e processamento de reuniões
- EPIC-004: Atas, relatórios e exportações

**User Stories detalhadas:**
- US-001: Copiar integralmente o frontend exportado para a estrutura `frontend/`
- US-002: Estabilizar dependências, rotas e build do frontend copiado
- US-003: Modelar gestão de participantes e regiões
- US-004: Modelar cadastro, processamento e visualização de reuniões
- ...e mais baseado no código encontrado

**Roadmap sugerido:**
- Sprint 01: Adoção integral do frontend e build local
- Sprint 02: Contratos e backend mínimo para entidades centrais
- Sprint 03: Processamento de reuniões, atas e relatórios
- ...

---

## 🔧 Troubleshooting

### "A IA não identificou todas as features"

**Solução:** Adicione um arquivo `OVERVIEW.md` descrevendo explicitamente todas as funcionalidades esperadas.

### "Estimativas parecem incorretas"

**Solução:** Ajuste manualmente após a geração. As estimativas são sugestões baseadas na complexidade aparente.

### "Muitas stories duplicadas"

**Solução:** Consolide manualmente ou reorganize os exemplos para serem mais específicos.

### "Não gerou nenhum backlog"

**Solução:** Verifique se:
1. Os arquivos estão realmente nesta pasta
2. Você está usando o prompt correto no passo 1.5
3. Os exemplos têm conteúdo suficiente para análise

---

## 🎓 Dicas Avançadas

### Use Anotações em Screenshots

Anote seus designs com números ou descrições antes de exportar:
```
1. Botão de login com Google OAuth
2. Campo de email com validação
3. Toggle "Lembrar de mim"
```

### Combine Código + Design

Para melhores resultados, forneça ambos:
- Screenshot do design final
- Código do componente correspondente

A IA consegue correlacionar e gerar stories mais precisas.

### Inclua Casos de Uso

Crie um arquivo `USER_FLOWS.md`:
```markdown
## Fluxo: Criar Nova Tarefa
1. Usuário clica em "Nova Tarefa"
2. Preenche título e descrição
3. Seleciona prioridade
4. Clica em "Salvar"
5. Tarefa aparece na lista
```

---

## ⚡ Funcionalidade Opcional

**Importante:** Esta funcionalidade é completamente **opcional**.

- ✅ **Com exemplos:** Gera backlog automaticamente
- ✅ **Sem exemplos:** Workflow funciona normalmente (manual)

Se preferir criar o backlog manualmente, simplesmente não coloque arquivos nesta pasta e pule o passo 1.5 do workflow.

---

## 📚 Recursos Adicionais

- [Workflow de Sprint Planning](../../.agents/workflows/sprint-planning.md)
- [Template de Product Backlog](../../templates/product_backlog.md)
- [Template de Sprint Planning](../../templates/sprint_planning.md)

---

**Dúvidas?** Para operação com agente, consulte primeiro `docs/project_manifest.md`, `AGENTS.md` e o workflow ativo. O README pode existir como documentação humana, mas não é fonte operacional canônica.
