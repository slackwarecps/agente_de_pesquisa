#!/usr/bin/env python3
"""
Agente multiorquestrador de pesquisa usando o Claude Agent SDK.

Um agente coordenador delega (via a ferramenta Task) para 4 subagentes
especializados:

  - web-researcher    : busca informação atual na web
  - document-analyzer : aprofunda em fontes específicas e extrai fatos
  - synthesizer       : consolida os achados em uma síntese coerente
  - report-writer     : escreve o relatório final em Markdown com citações

Uso:
    python research_agent.py "tópico da pesquisa"
"""

__version__ = "1.0.2"

import asyncio
import re
import sys
import time
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TaskNotificationMessage,
    TaskStartedMessage,
    TextBlock,
    ToolUseBlock,
    query,
)

REPORTS_DIR = Path(__file__).parent / "reports"
LOG_PATH = Path(__file__).parent / "research.log"


class ProgressLogger:
    """Escreve cada linha de progresso no console e em research.log,
    com flush imediato para que `tail -f research.log` funcione em tempo real.
    """

    def __init__(self, log_path: Path):
        """Abre (ou cria) o arquivo de log em modo 'append', mantendo o
        arquivo aberto durante toda a execução para permitir escritas
        sucessivas sem reabrir o arquivo a cada linha.
        """
        self._fh = log_path.open("a", encoding="utf-8")

    def log(self, message: str) -> None:
        """Registra uma mensagem com timestamp (HH:MM:SS) no console e no
        arquivo de log, forçando o flush em ambos imediatamente — assim um
        `tail -f research.log` mostra o progresso em tempo real, sem
        esperar o buffer do sistema operacional encher.
        """
        line = f"[{time.strftime('%H:%M:%S')}] {message}"
        print(line, flush=True)
        self._fh.write(line + "\n")
        self._fh.flush()

    def close(self) -> None:
        """Fecha o arquivo de log, liberando o descritor de arquivo.
        Deve ser chamado ao final da pesquisa (mesmo em caso de erro).
        """
        self._fh.close()

AGENTS = {
    "web-researcher": AgentDefinition(
        description=(
            "Busca informação atual na web sobre um tópico. Use para descobrir "
            "fontes, notícias, dados e visões recentes antes de aprofundar em "
            "qualquer uma delas."
        ),
        prompt=(
            "Você é um pesquisador web. Dado um tópico ou pergunta, use a "
            "ferramenta WebSearch para encontrar múltiplas fontes relevantes e "
            "recentes (diversifique as buscas — não pare na primeira). Para cada "
            "achado relevante, registre: o fato/afirmação, a URL de origem e a "
            "data da fonte quando disponível. Retorne uma lista objetiva de "
            "achados com suas fontes — não escreva prosa longa, apenas fatos e "
            "URLs."
        ),
        tools=["WebSearch", "WebFetch"],
    ),
    "document-analyzer": AgentDefinition(
        description=(
            "Aprofunda em URLs ou documentos específicos para extrair fatos "
            "precisos e citáveis. Use depois que o web-researcher já identificou "
            "fontes promissoras, para verificar e detalhar o conteúdo delas."
        ),
        prompt=(
            "Você é um analista de documentos. Dada uma lista de URLs/fontes, use "
            "WebFetch para ler o conteúdo de cada uma e extrair os fatos mais "
            "relevantes para o tópico da pesquisa. Para cada fato, cite a URL "
            "exata de onde veio. Sinalize claramente se uma fonte não pôde ser "
            "acessada ou não continha informação relevante. Retorne uma lista "
            "estruturada de fato → fonte."
        ),
        tools=["WebFetch", "Read", "Grep"],
    ),
    "synthesizer": AgentDefinition(
        description=(
            "Consolida achados de pesquisa e análise de documentos em uma "
            "síntese coerente e organizada por tema. Use depois de reunir os "
            "achados dos outros agentes, antes de escrever o relatório final."
        ),
        prompt=(
            "Você é um sintetizador de pesquisa. Receberá achados de múltiplas "
            "fontes (possivelmente com sobreposição ou contradição). Organize-os "
            "por tema, elimine redundâncias, sinalize contradições entre fontes "
            "quando existirem, e preserve TODAS as citações/URLs associadas a "
            "cada afirmação — nunca solte um fato sem sua fonte. Não invente "
            "informação que não veio das fontes fornecidas."
        ),
        tools=[],
    ),
    "report-writer": AgentDefinition(
        description=(
            "Escreve o relatório final de pesquisa em Markdown e salva em "
            "disco. Use por último, depois que a síntese estiver pronta."
        ),
        prompt=(
            "Você é um redator de relatórios. Dada uma síntese de pesquisa já "
            "organizada e citada, escreva um relatório completo em Markdown com: "
            "um título, um resumo executivo, seções temáticas com as citações "
            "inline (formato [fonte](URL) ou numeradas), e uma seção final "
            "'Referências' listando todas as URLs usadas. Salve o arquivo com a "
            "ferramenta Write no caminho exato que foi instruído. Depois de "
            "salvar, responda apenas confirmando o caminho do arquivo salvo."
        ),
        tools=["Write"],
    ),
}

COORDINATOR_SYSTEM_PROMPT = """\
Você é o coordenador de um sistema de pesquisa multi-agente. Seu único trabalho \
é orquestrar subagentes especializados via a ferramenta Task — você mesmo não \
deve pesquisar, analisar ou escrever o relatório diretamente.

Para cada pedido de pesquisa, siga esta sequência:

1. Delegue ao subagente "web-researcher" para levantar fontes e achados \
iniciais sobre o tópico.
2. Delegue ao subagente "document-analyzer" para aprofundar nas fontes mais \
promissoras encontradas no passo 1 e extrair fatos citáveis.
3. Delegue ao subagente "synthesizer" passando os achados dos passos 1 e 2, \
pedindo uma síntese organizada e citada.
4. Delegue ao subagente "report-writer" passando a síntese do passo 3 e o \
caminho exato onde o relatório deve ser salvo (informado no prompt do \
usuário). Ele deve salvar o arquivo com a ferramenta Write.

Depois que o report-writer confirmar que salvou o arquivo, responda ao \
usuário com uma confirmação curta e o caminho do arquivo. Não repita o \
conteúdo do relatório inteiro no seu resumo final.
"""


def _slugify(topic: str) -> str:
    """Converte o tópico de pesquisa em um nome de arquivo seguro (slug).

    Coloca tudo em minúsculas, remove pontuação/caracteres especiais,
    substitui espaços e underscores/hifens repetidos por um único hífen,
    e limita o resultado a 60 caracteres. Se o resultado ficar vazio
    (ex.: tópico só com símbolos), usa "pesquisa" como padrão.

    Exemplo: "Impacto da IA na Educação?" -> "impacto-da-ia-na-educacao"
    """
    slug = re.sub(r"[^\w\s-]", "", topic.lower()).strip()
    slug = re.sub(r"[\s_-]+", "-", slug)
    return slug[:60] or "pesquisa"


async def research(topic: str) -> None:
    """Executa uma pesquisa completa de ponta a ponta sobre `topic`.

    Monta as opções do agente coordenador (subagentes disponíveis, ferramentas
    permitidas, prompt de sistema e diretório de trabalho), dispara a query
    ao Claude Agent SDK e consome o fluxo de mensagens (`query`) em tempo
    real: eventos de início/fim de subagente, falas do coordenador,
    delegações via ferramenta Task e o resultado final (com custo e número
    de turnos). Cada evento relevante é gravado pelo `ProgressLogger` tanto
    no console quanto em `research.log`.

    Ao final, confere se o arquivo de relatório esperado (`report_path`)
    foi realmente criado e registra sucesso ou aviso de acordo.
    """
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"{_slugify(topic)}.md"

    options = ClaudeAgentOptions(
        agents=AGENTS,
        allowed_tools=["Task", "WebSearch", "WebFetch", "Read", "Write", "Grep"],
        system_prompt=COORDINATOR_SYSTEM_PROMPT,
        permission_mode="bypassPermissions",
        cwd=str(Path(__file__).parent),
    )

    prompt = (
        f"Pesquise o seguinte tópico e produza um relatório completo com "
        f"citações: {topic!r}\n\n"
        f"O relatório final deve ser salvo em: {report_path}"
    )

    logger = ProgressLogger(LOG_PATH)
    logger.log("=" * 60)
    logger.log(f"🔎 Nova pesquisa: {topic}")
    logger.log(f"   Relatório será salvo em: {report_path}")

    try:
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, TaskStartedMessage):
                logger.log(f"▶️  Subagente iniciado: {message.description}")
            elif isinstance(message, TaskNotificationMessage):
                icon = "✅" if message.status == "completed" else "⚠️"
                logger.log(
                    f"{icon} Subagente finalizado [{message.status}]: "
                    f"{message.summary}"
                )
            elif isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        logger.log(f"🗣️  Coordenador: {block.text.strip()}")
                    elif isinstance(block, ToolUseBlock) and block.name == "Task":
                        desc = block.input.get("description", "")
                        subagent = block.input.get("subagent_type", "?")
                        logger.log(
                            f"🔧 Delegando para '{subagent}': {desc}"
                        )
            elif isinstance(message, ResultMessage):
                if message.is_error:
                    logger.log(f"❌ Erro: {message.result or message.subtype}")
                else:
                    cost = (
                        f"${message.total_cost_usd:.4f}"
                        if message.total_cost_usd
                        else "N/A"
                    )
                    logger.log(
                        f"✅ Concluído em {message.num_turns} turnos "
                        f"(custo: {cost})"
                    )

        if report_path.exists():
            logger.log(f"📄 Relatório salvo em: {report_path}")
        else:
            logger.log(
                "⚠️  Não encontrei o arquivo esperado — verifique o log acima "
                "para o caminho que o report-writer realmente usou."
            )
    finally:
        logger.close()


def main() -> None:
    """Ponto de entrada da linha de comando.

    Lê o tópico de pesquisa a partir dos argumentos do terminal (juntando
    todas as palavras passadas após o nome do script), valida que pelo
    menos um argumento foi fornecido e então roda a corrotina `research`
    até sua conclusão via `asyncio.run`. Se nenhum tópico for informado,
    imprime a instrução de uso em stderr e encerra com código de erro 1.
    """
    if len(sys.argv) < 2:
        print('Uso: python research_agent.py "tópico da pesquisa"', file=sys.stderr)
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    asyncio.run(research(topic))


if __name__ == "__main__":  # pragma: no cover
    main()
