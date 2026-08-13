"""Fixtures compartilhadas pelos testes de research_agent.py.

Duas técnicas concentradas aqui, para não repetir em cada arquivo de teste:

1. `isolated_paths` — redireciona os caminhos globais do módulo
   (REPORTS_DIR / LOG_PATH) para dentro de um diretório temporário, para que
   nenhum teste escreva no disco real do projeto.
2. `make_query` — fábrica de um `query()` falso: um gerador assíncrono que
   apenas devolve, em ordem, as mensagens que o teste passar. Isso permite
   "dirigir" `research()` sem nenhuma chamada de rede real, usando as
   próprias classes de mensagem da SDK (então os `isinstance(...)` dentro de
   `research_agent.py` continuam funcionando normalmente).
"""

import pytest

import research_agent


@pytest.fixture
def isolated_paths(tmp_path, monkeypatch):
    """Redireciona REPORTS_DIR e LOG_PATH para um diretório temporário."""
    reports_dir = tmp_path / "reports"
    log_path = tmp_path / "research.log"
    monkeypatch.setattr(research_agent, "REPORTS_DIR", reports_dir)
    monkeypatch.setattr(research_agent, "LOG_PATH", log_path)
    return reports_dir, log_path


@pytest.fixture
def make_query():
    """Retorna uma fábrica que transforma uma lista de mensagens em um
    `query()` falso (async generator function) pronto para substituir
    `research_agent.query` via monkeypatch.
    """

    def _factory(*messages):
        async def fake_query(*, prompt, options):
            for message in messages:
                yield message

        return fake_query

    return _factory
