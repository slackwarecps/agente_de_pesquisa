"""Testes de `ProgressLogger` — introduz duas técnicas novas em relação ao
teste de `_slugify`: `capsys` (captura o que foi impresso no console) e
leitura de um arquivo real escrito em `tmp_path` (diretório temporário do
pytest, apagado automaticamente ao final do teste).
"""

import re

from research_agent import ProgressLogger


def test_log_escreve_no_console_e_no_arquivo_com_timestamp(tmp_path, capsys):
    log_path = tmp_path / "research.log"
    logger = ProgressLogger(log_path)

    logger.log("mensagem de teste")
    logger.close()

    console_output = capsys.readouterr().out
    file_output = log_path.read_text(encoding="utf-8")

    # Mesmo conteúdo nos dois destinos, no formato "[HH:MM:SS] mensagem".
    padrao = re.compile(r"^\[\d{2}:\d{2}:\d{2}\] mensagem de teste\n$")
    assert padrao.match(console_output)
    assert padrao.match(file_output)


def test_log_faz_flush_imediato_antes_do_close(tmp_path):
    log_path = tmp_path / "research.log"
    logger = ProgressLogger(log_path)

    logger.log("linha 1")
    # Sem chamar close(): se o flush não fosse imediato, o arquivo lido "por
    # fora" (nova leitura do disco) poderia não conter a linha ainda.
    conteudo_antes_do_close = log_path.read_text(encoding="utf-8")

    logger.close()

    assert "linha 1" in conteudo_antes_do_close


def test_close_fecha_o_arquivo(tmp_path):
    logger = ProgressLogger(tmp_path / "research.log")
    logger.close()

    assert logger._fh.closed is True


def test_log_acumula_multiplas_linhas_em_modo_append(tmp_path):
    log_path = tmp_path / "research.log"

    primeiro_logger = ProgressLogger(log_path)
    primeiro_logger.log("primeira execução")
    primeiro_logger.close()

    segundo_logger = ProgressLogger(log_path)
    segundo_logger.log("segunda execução")
    segundo_logger.close()

    conteudo = log_path.read_text(encoding="utf-8")
    assert "primeira execução" in conteudo
    assert "segunda execução" in conteudo
