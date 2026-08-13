"""Testes de `research()` — o coração do módulo.

Técnica principal: `research_agent.query` (a função da SDK que faria a
chamada real de rede) é substituída, via `monkeypatch`, por um generator
assíncrono que produz mensagens já prontas (`make_query`, de conftest.py).
Como `research()` também só enxerga REPORTS_DIR/LOG_PATH através dos nomes
globais do módulo, a fixture `isolated_paths` os redireciona para um
diretório temporário antes de cada teste — nada aqui toca o disco real do
projeto nem a rede.

Cada teste cobre um branch específico de `research()`; juntos, fecham 100%
das combinações de mensagem tratadas pelo laço `async for`.
"""

import asyncio
import importlib

import pytest
from claude_agent_sdk import (
    AssistantMessage,
    ResultMessage,
    StreamEvent,
    TaskNotificationMessage,
    TaskStartedMessage,
    TextBlock,
    ToolUseBlock,
)

import research_agent
from research_agent import _slugify


def _run(monkeypatch, make_query, isolated_paths, messages, topic="tema de teste"):
    """Roda research_agent.research(topic) com um query() falso que produz
    `messages`, e devolve o conteúdo do research.log gerado."""
    monkeypatch.setattr(research_agent, "query", make_query(*messages))
    asyncio.run(research_agent.research(topic))
    _, log_path = isolated_paths
    return log_path.read_text(encoding="utf-8")


def test_subagente_iniciado_registra_log(monkeypatch, make_query, isolated_paths):
    msg = TaskStartedMessage(
        subtype="task_started",
        data={},
        task_id="t1",
        description="buscando fontes",
        uuid="u1",
        session_id="s1",
    )
    log = _run(monkeypatch, make_query, isolated_paths, [msg])
    assert "▶️  Subagente iniciado: buscando fontes" in log


def test_notificar_subagente_sucesso_e_falha(monkeypatch, make_query, isolated_paths):
    completed = TaskNotificationMessage(
        subtype="task_notification",
        data={},
        task_id="t1",
        status="completed",
        output_file="",
        summary="achou 5 fontes",
        uuid="u1",
        session_id="s1",
    )
    failed = TaskNotificationMessage(
        subtype="task_notification",
        data={},
        task_id="t2",
        status="failed",
        output_file="",
        summary="não achou nada",
        uuid="u2",
        session_id="s1",
    )
    log = _run(monkeypatch, make_query, isolated_paths, [completed, failed])
    assert "✅ Subagente finalizado [completed]: achou 5 fontes" in log
    assert "⚠️ Subagente finalizado [failed]: não achou nada" in log


def test_ignorar_texto_em_branco(monkeypatch, make_query, isolated_paths):
    msg = AssistantMessage(
        content=[TextBlock(text="   "), TextBlock(text="Analisando o tema")],
        model="claude-test",
    )
    log = _run(monkeypatch, make_query, isolated_paths, [msg])
    assert "🗣️  Coordenador: Analisando o tema" in log
    # O bloco em branco não deve ter gerado uma segunda linha de fala.
    assert log.count("🗣️") == 1


def test_delegar_ferramenta_registra_log(monkeypatch, make_query, isolated_paths):
    msg = AssistantMessage(
        content=[
            ToolUseBlock(
                id="1",
                name="Task",
                input={"description": "pesquisar fontes", "subagent_type": "web-researcher"},
            ),
            ToolUseBlock(id="2", name="WebSearch", input={}),
        ],
        model="claude-test",
    )
    log = _run(monkeypatch, make_query, isolated_paths, [msg])
    assert "🔧 Delegando para 'web-researcher': pesquisar fontes" in log
    # A chamada de ferramenta que não é "Task" não deve gerar log de delegação.
    assert log.count("🔧") == 1


@pytest.mark.parametrize(
    "kwargs, esperado",
    [
        (
            dict(subtype="error_max_turns", is_error=True, result="falha de rede"),
            "❌ Erro: falha de rede",
        ),
        (
            # Sem `result`: a mensagem cai no fallback `message.subtype`.
            dict(subtype="error_max_turns", is_error=True, result=None),
            "❌ Erro: error_max_turns",
        ),
    ],
)
def test_resultado_erro_registra_mensagem(monkeypatch, make_query, isolated_paths, kwargs, esperado):
    msg = ResultMessage(duration_ms=100, duration_api_ms=90, num_turns=3, session_id="s1", **kwargs)
    log = _run(monkeypatch, make_query, isolated_paths, [msg])
    assert esperado in log


@pytest.mark.parametrize(
    "kwargs, esperado",
    [
        (
            dict(subtype="success", is_error=False, total_cost_usd=0.1234),
            "✅ Concluído em 3 turnos (custo: $0.1234)",
        ),
        (
            # Sem custo reportado: cai no fallback "N/A".
            dict(subtype="success", is_error=False, total_cost_usd=None),
            "✅ Concluído em 3 turnos (custo: N/A)",
        ),
    ],
)
def test_resultado_sucesso_registra_mensagem(monkeypatch, make_query, isolated_paths, kwargs, esperado):
    msg = ResultMessage(duration_ms=100, duration_api_ms=90, num_turns=3, session_id="s1", **kwargs)
    log = _run(monkeypatch, make_query, isolated_paths, [msg])
    assert esperado in log


def test_mensagem_desconhecida_ignora_continua(
    monkeypatch, make_query, isolated_paths
):
    # StreamEvent não é nenhum dos quatro tipos tratados pelo if/elif: cai
    # por fora de todos os ramos e o laço deve simplesmente seguir para a
    # próxima mensagem, sem logar nada para ela nem quebrar a execução.
    nao_tratada = StreamEvent(uuid="u0", session_id="s1", event={})
    depois = TaskStartedMessage(
        subtype="task_started",
        data={},
        task_id="t1",
        description="continua normalmente",
        uuid="u1",
        session_id="s1",
    )
    log = _run(monkeypatch, make_query, isolated_paths, [nao_tratada, depois])
    assert "▶️  Subagente iniciado: continua normalmente" in log


def test_loop_continua_apos_resultado(monkeypatch, make_query, isolated_paths):
    # Garante que o `async for` segue para a próxima mensagem mesmo depois
    # de processar um ResultMessage no meio do stream (na prática isso não
    # deveria acontecer com o coordenador atual, mas o laço não impede).
    resultado = ResultMessage(
        duration_ms=100,
        duration_api_ms=90,
        num_turns=1,
        session_id="s1",
        subtype="success",
        is_error=False,
        total_cost_usd=0.01,
    )
    depois = TaskStartedMessage(
        subtype="task_started",
        data={},
        task_id="t2",
        description="segunda rodada",
        uuid="u2",
        session_id="s1",
    )
    log = _run(monkeypatch, make_query, isolated_paths, [resultado, depois])
    assert "✅ Concluído em 1 turnos (custo: $0.0100)" in log
    assert "▶️  Subagente iniciado: segunda rodada" in log


def test_relatorio_criado_registra_sucesso(monkeypatch, make_query, isolated_paths):
    reports_dir, log_path = isolated_paths
    topic = "tema com relatorio"
    expected_path = reports_dir / f"{_slugify(topic)}.md"

    async def fake_query(*, prompt, options):
        # Simula o report-writer salvando o arquivo antes do fim da pesquisa.
        # REPORTS_DIR já existe neste ponto: research() cria o diretório
        # antes de chamar query().
        expected_path.write_text("# Relatório\n", encoding="utf-8")
        return
        yield  # nunca executado; só torna a função um async generator

    monkeypatch.setattr(research_agent, "query", fake_query)
    asyncio.run(research_agent.research(topic))

    log = log_path.read_text(encoding="utf-8")
    assert f"📄 Relatório salvo em: {expected_path}" in log


def test_relatorio_nao_criado_gera_aviso(monkeypatch, make_query, isolated_paths):
    log = _run(monkeypatch, make_query, isolated_paths, [], topic="tema sem relatorio")
    assert "⚠️  Não encontrei o arquivo esperado" in log


def test_log_inicial_mostra_modelo_usado(monkeypatch, make_query, isolated_paths):
    # A linha de modelo deve aparecer logo abaixo de "Nova pesquisa", antes
    # do caminho do relatório.
    log = _run(monkeypatch, make_query, isolated_paths, [], topic="tema qualquer")
    assert f"   Modelo: {research_agent.MODEL}" in log
    assert log.index("🔎 Nova pesquisa") < log.index(f"Modelo: {research_agent.MODEL}") < log.index("Relatório será salvo em")


def test_options_usa_modelo_configurado(monkeypatch, isolated_paths):
    # Garante que research() sempre passa o modelo fixado em MODEL para o
    # ClaudeAgentOptions, e não deixa o SDK escolher um modelo padrão.
    opcoes_capturadas = {}

    async def fake_query(*, prompt, options):
        opcoes_capturadas["options"] = options
        return
        yield  # nunca executado; só torna a função um async generator

    monkeypatch.setattr(research_agent, "query", fake_query)
    asyncio.run(research_agent.research("tema qualquer"))

    assert opcoes_capturadas["options"].model == research_agent.MODEL
    assert "haiku" in research_agent.MODEL.lower()  # custo controlado, versão livre


def test_prompt_report_writer_define_limite_de_palavras():
    """Verifica que o prompt do report-writer menciona o limite de 500 palavras."""
    prompt = research_agent.AGENTS["report-writer"].prompt
    assert "500 palavras" in prompt


def test_subagentes_usam_modelo_configurado():
    """Verifica que todos os subagentes herdam explicitamente MODEL."""
    for nome, definicao in research_agent.AGENTS.items():
        assert definicao.model == research_agent.MODEL, (
            f"Subagente '{nome}' não herda o modelo configurado"
        )


def test_model_respeita_variavel_de_ambiente(monkeypatch):
    """Verifica que MODEL pode ser configurado via env var RESEARCH_MODEL."""
    monkeypatch.setenv("RESEARCH_MODEL", "claude-opus-5")
    # Recarrega o módulo para ler a nova variável de ambiente
    importlib.reload(research_agent)
    try:
        assert research_agent.MODEL == "claude-opus-5"
    finally:
        # Limpa o env var e recarrega novamente para restaurar o estado
        monkeypatch.delenv("RESEARCH_MODEL", raising=False)
        importlib.reload(research_agent)
