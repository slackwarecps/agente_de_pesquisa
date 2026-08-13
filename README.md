# Agente Multiorquestrador de Pesquisa

Sistema simples de pesquisa multi-agente construído com o **Claude Agent SDK**.
Um agente coordenador delega para 4 subagentes especializados:

1. **web-researcher** — busca fontes atuais na web
2. **document-analyzer** — aprofunda nas fontes e extrai fatos citáveis
3. **synthesizer** — consolida os achados em uma síntese organizada
4. **report-writer** — escreve o relatório final em Markdown com citações

## Pré-requisitos

- Python 3.10+
- Uma `ANTHROPIC_API_KEY` válida no ambiente
- Node.js (o Claude Agent SDK usa o Claude Code CLI internamente; uma versão
  vem empacotada com o SDK, mas ter Node.js instalado evita problemas em
  alguns ambientes)

## Instalação

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

## Uso

```bash
python research_agent.py "avanços recentes em computação quântica"
```

O progresso da pesquisa (delegação entre os subagentes) aparece no console em
tempo real e também é gravado em `research.log` (append, com timestamp por
linha). Para acompanhar rodando em segundo plano:

```bash
tail -f research.log
```

Ao final, o relatório completo é salvo em `reports/<slug-do-topico>.md`.

### Variáveis de Ambiente

- `RESEARCH_MODEL` — Define o modelo LLM para toda a pesquisa (coordenador + 
  subagentes). Padrão: `claude-haiku-4-5-20251001` (versão econômica). 
  Exemplos:
  ```bash
  RESEARCH_MODEL="claude-opus-5" python research_agent.py "seu tópico"
  RESEARCH_MODEL="claude-sonnet-5" python research_agent.py "seu tópico"
  ```
  Haiku é recomendado para custos controlados; use Sonnet ou Opus se precisar
  de raciocínio mais sofisticado (especialmente no synthesizer).

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

A suíte roda isolada (sem rede nem SDK real) e mede cobertura automaticamente
via `pytest-cov` (configurado em `pyproject.toml`, com `fail_under = 100`).


## Custom Slash Commands
When you see these commands, follow the pattern:

/passa-skill-de-seguranca
- Executa: pip audit
- Verifica secrets em código
- Valida OWASP top 10
- Gera security report
