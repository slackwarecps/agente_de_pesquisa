# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## O que é este projeto

Agente multiorquestrador de pesquisa construído sobre o **Claude Agent SDK**
(`claude_agent_sdk`). É um único script Python (`research_agent.py`) que
recebe um tópico via linha de comando e produz um relatório em Markdown com
citações, salvo em `reports/`.

## Comandos

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave-aqui"

python research_agent.py "tópico da pesquisa"
```

Requisitos: Python 3.10+; Node.js recomendado (o Claude Agent SDK usa o
Claude Code CLI internamente).

## Testes

Testes são **obrigatórios** neste projeto com **mínimo 83% de cobertura de código**.

> **Por que 83%?** Mantém um padrão alto de qualidade (83% é excelente) enquanto permite desenvolvimento mais ágil. O foco está no code coverage dos principais fluxos e lógica crítica.

### Convenções

- **Localização:** Todos os testes devem estar em `tests/`
- **Linguagem:** Português brasileiro
- **Nomenclatura:** Seguir o padrão `test_<nome_descritivo_em_portugues>`
  - Exemplos: `test_ignorar_texto_em_branco`, `test_validar_tópico_vazio`, `test_criar_relatório_markdown`

### Rodar testes

```bash
# Com cobertura obrigatória (83%, configurado em pyproject.toml)
pytest tests/ -v
# Falhará se coverage < 83%

# Cobertura explícita com limite de 83%
pytest tests/ -v --cov=research_agent --cov-report=term-missing --cov-fail-under=83

# Sem cobertura (desenvolvimento rápido, sem validação)
pytest tests/ -v --no-cov
```

### Configuração de Cobertura

A configuração está em `pyproject.toml`:
```toml
[tool.coverage.report]
fail_under = 83  # Mínimo de 83% de cobertura
show_missing = true  # Mostra linhas não cobertas
```

### Monitorar execução em tempo real

```bash
tail -f research.log
```

## Arquitetura

Tudo em `research_agent.py`. Um agente **coordenador** (prompt de sistema em
`COORDINATOR_SYSTEM_PROMPT`) nunca pesquisa nem escreve diretamente — ele
apenas delega, via a ferramenta `Task`, para 4 subagentes definidos em
`AGENTS` (dict de `AgentDefinition`), sempre nesta ordem fixa:

1. **web-researcher** (`WebSearch`, `WebFetch`) — levanta fontes e achados iniciais.
2. **document-analyzer** (`WebFetch`, `Read`, `Grep`) — aprofunda nas fontes mais promissoras e extrai fatos citáveis.
3. **synthesizer** (sem ferramentas) — consolida os achados por tema, remove redundâncias, sinaliza contradições e preserva todas as citações.
4. **report-writer** (`Write`) — escreve o relatório final em Markdown e salva no caminho exato informado pelo coordenador.

Cada subagente tem seu próprio `description` (usado pelo coordenador para
decidir a delegação) e `prompt` de sistema restrito ao seu papel — ao alterar
o comportamento de uma etapa, editar a entrada correspondente em `AGENTS` em
vez de mexer no prompt do coordenador.

A função `research()` monta as `ClaudeAgentOptions` (agentes, `allowed_tools`,
`system_prompt`, `permission_mode="bypassPermissions"`, `model=MODEL`), dispara
`query(...)` e consome o stream de mensagens em tempo real, tratando por tipo:
`TaskStartedMessage`/`TaskNotificationMessage` (início/fim de subagente),
`AssistantMessage` com `ToolUseBlock` do tipo `Task` (delegações) ou
`TextBlock` (falas do coordenador), e `ResultMessage` (custo/turnos finais).

`ProgressLogger` grava cada evento simultaneamente no console e em
`research.log` (append, com flush imediato) para permitir acompanhar
execuções longas com `tail -f`.

O caminho do relatório é derivado do tópico via `_slugify()` e passado
explicitamente no prompt do coordenador — o report-writer deve salvar
exatamente nesse caminho (`reports/<slug-do-tópico>.md`); ao final,
`research()` confere se o arquivo realmente foi criado nesse caminho.

O modelo usado por coordenador e subagentes é fixado na constante `MODEL`
(topo do arquivo) — atualize-a ali quando um Haiku mais recente for lançado.
