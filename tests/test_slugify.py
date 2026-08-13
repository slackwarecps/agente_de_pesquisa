"""Testes de `_slugify()` — a unidade mais simples do módulo: uma função
pura (mesma entrada -> mesma saída, sem I/O nem dependências). Bom ponto de
partida para aprender `pytest.mark.parametrize`.
"""

import pytest

from research_agent import _slugify


@pytest.mark.parametrize(
    "topic, expected",
    [
        # Caso simples: minúsculas e espaço -> hífen.
        ("Computação Quântica", "computação-quântica"),
        # Pontuação é removida, não vira hífen.
        ("Impacto da IA na Educação?", "impacto-da-ia-na-educação"),
        # Espaços, underscores e hífens repetidos colapsam em um só hífen.
        ("café   com--leite_ _gelado", "café-com-leite-gelado"),
        # Espaços nas pontas são descartados antes da conversão.
        ("  IA generativa  ", "ia-generativa"),
    ],
)
def test_slugify_normal_cases(topic, expected):
    assert _slugify(topic) == expected


def test_slugify_trunca_em_60_caracteres():
    topic = "palavra " * 20  # bem mais que 60 caracteres depois do slug
    slug = _slugify(topic)
    assert len(slug) <= 60


def test_slugify_usa_fallback_quando_fica_vazio():
    # Só símbolos: depois de remover pontuação e espaços, não sobra nada.
    assert _slugify("???!!!...") == "pesquisa"
