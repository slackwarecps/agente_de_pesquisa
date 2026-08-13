"""Testes de `main()` — o ponto de entrada da CLI.

Aqui a técnica é monkeypatch em `sys.argv` (para simular a linha de
comando) e em `research_agent.research` (para não disparar uma pesquisa de
verdade quando o teste só quer confirmar que `main()` chama `research()`
com o tópico certo).
"""

import sys

import pytest

import research_agent
from research_agent import main


def test_main_sem_topico_encerra_com_erro(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["research_agent.py"])

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert 'Uso: python research_agent.py "tópico da pesquisa"' in capsys.readouterr().err


def test_main_chama_research_com_topico_montado_a_partir_do_argv(monkeypatch):
    topicos_recebidos = []

    async def fake_research(topic):
        topicos_recebidos.append(topic)

    monkeypatch.setattr(research_agent, "research", fake_research)
    monkeypatch.setattr(sys, "argv", ["research_agent.py", "avanços", "em", "IA"])

    main()

    assert topicos_recebidos == ["avanços em IA"]
