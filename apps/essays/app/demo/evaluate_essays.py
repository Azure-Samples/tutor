"""
Script to read essays_source.xlsx from .data folder, process each essay image URL, run agentic interaction, and save results.
Requires: pandas, openpyxl, python-dotenv
"""

import io
import sys
import json
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from semantic_kernel.agents import GroupChatManager, BooleanResult, MessageResult, StringResult  # pylint: disable=no-name-in-module
from semantic_kernel.contents import ChatMessageContent, ChatHistory, AuthorRole

from app.essays import EssayOrchestrator  # pylint: disable=import-error
from app.schemas import Essay, Resource, Evaluator, Swarm  # pylint: disable=import-error

import pandas as pd


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'src/essays'
sys.path.append(str(SRC))


def get_excel_path() -> Path:
    """Return the path to essays_source.xlsx in the .data folder."""
    return SRC / 'app/.data' / 'essays_source.xlsx'


class TransliterationChatManager(GroupChatManager):
    """
    Manages the group chat flow for the transliteration and review process.
    This custom manager coordinates the interaction between translation and review agents,
    determines when to terminate the chat, and selects the next agent to act based on the chat history.
    """

    async def filter_results(self, chat_history: ChatHistory) -> MessageResult:
        """
        Extracts the latest transliteration and review results from the chat history and composes a combined response.

        Args:
            chat_history (ChatHistory): The chat history containing all messages exchanged.
        Returns:
            MessageResult: A result object containing the composed transliteration and review as JSON.
        """
        # Extrai transliteração e avaliação do histórico
        translit = None
        review = None
        for msg in reversed(chat_history.messages):
            content = getattr(msg, 'content', '')
            last_agent = getattr(msg, 'name', '')
            if last_agent and "TranslationReviewerAgent" in last_agent and review is None:
                try:
                    review = json.loads(content)
                except Exception:
                    continue
            elif last_agent and "TermExtractorTranslatorAgent" in last_agent and translit is None:
                try:
                    translit = json.loads(content)
                except Exception:
                    continue
            if translit and review:
                break
        response = {
            "transliteration": translit,
            "review": review
        }
        return MessageResult(
            result=ChatMessageContent(
                role=AuthorRole.ASSISTANT,
                content=json.dumps(response, ensure_ascii=False, indent=2)
            ),
            reason="Composed transliteration and review."
        )

    async def should_terminate(self, chat_history: ChatHistory) -> BooleanResult:
        """
        Determines whether the group chat should terminate based on the latest review score or approval status.

        Args:
            chat_history (ChatHistory): The chat history containing all messages exchanged.
        Returns:
            BooleanResult: True if the process should terminate, False otherwise.
        """

        for msg in reversed(chat_history.messages):
            content = getattr(msg, 'content', '')
            last_agent = getattr(msg, 'name', 'User')
            if last_agent and "TranslationReviewerAgent" in last_agent:
                try:
                    review = json.loads(content)
                    score = review.get("score_global", 0)
                    acao = review.get("acao_recomendada", "")
                    if score >= 80 or acao == "aprovado":
                        return BooleanResult(result=True, reason=f"Score {score} e aprovado.")
                except Exception:
                    continue
        return BooleanResult(result=False, reason="Score ou aprovação ainda não atingidos.")

    async def should_request_user_input(self, chat_history: ChatHistory) -> BooleanResult:
        """
        Indicates whether user input is required during the automatic cycle (always False for this pipeline).

        Args:
            chat_history (ChatHistory): The chat history containing all messages exchanged.
        Returns:
            BooleanResult: Always False for this implementation.
        """
        # Nunca solicita input do usuário durante o ciclo automático
        return BooleanResult(result=False, reason="Ciclo automático, sem input do usuário.")

    async def select_next_agent(self, chat_history: ChatHistory, participant_descriptions: dict[str, str]) -> StringResult:
        """
        Selects the next agent to act in the group chat based on the last message and review status.

        Args:
            chat_history (ChatHistory): The chat history containing all messages exchanged.
            participant_descriptions (dict): Mapping of agent names to their descriptions.
        Returns:
            StringResult: The name of the next agent to act.
        """
        agents = list(participant_descriptions.keys())
        if not chat_history.messages or (
            len(chat_history.messages) == 1 and chat_history.messages[0].role == AuthorRole.USER
        ):
            return StringResult(result=agents[0], reason="Primeira rodada: transliteração.")
        last_msg = chat_history.messages[-1]
        last_agent = getattr(last_msg, 'name', '')
        is_reviewer = False
        if "TranslationReviewerAgent" in last_agent:
            is_reviewer = True
        score = None
        aprovacao = "reexecutar"
        if is_reviewer:
            try:
                review = json.loads(last_msg.content)
                aprovacao = review.get("acao_recomendada", "reexecutar")
                score = review.get("score_global", 0)
            except Exception:
                pass
            if score is not None and score < 90 or aprovacao == "reexecutar":
                return StringResult(result=agents[0], reason=last_msg.content)
            return StringResult(result=agents[0], reason="Score suficiente, transliteração final.")
        # Se não foi reviewer, alterna para o avaliador
        return StringResult(result=agents[1], reason="Alterna para avaliador.")


async def main():
    load_dotenv(SRC / '.env')

    excel_file = get_excel_path()
    if not excel_file.exists():
        print(f"Excel file not found at {excel_file}")
        return

    df = pd.read_excel(excel_file, sheet_name="Exemplos Categorizados")
    df = df.drop_duplicates(subset="id_redacao").head(5)
    orchestrator = EssayOrchestrator()
    spelling_agent = Evaluator(
        id="ortografia",
        name="Ortografia",
        model_id="reasoning",
        metaprompt=json.dumps({
            "text": (
                """
                Avalie detalhadamente a FORMA GRÁFICA da escrita no texto em português compartilhado na imagem fornecida através de uma URL.\n"
                "NÃO avalie ortografia, semântica ou qualidade linguística.\n"
                "Descreva padrões de escrita, legibilidade, espaçamento, consistência de letras, alinhamento e outros aspectos gráficos relevantes.\n"
                "Não faça sugestões de correção ortográfica ou gramatical.\n"
                "A saída deve ser um JSON com a seguinte estrutura:\n"
                "{\n"
                "  'items': [\n"
                "    {\n"
                "      'row': 0,\n"
                "      'url': '',\n"
                "      'aspecto_grafico': '', // descrição do aspecto gráfico avaliado\n"
                "      'observacao': '' // observação sobre a forma da escrita\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Não inclua resumos ou explicações adicionais, apenas os aspectos gráficos observados.\n"
                """
            ),
            "json": True
        }),
        description="Avalia apenas a forma gráfica da escrita, sem considerar ortografia ou semântica."
    )
    syntax_agent = Evaluator(
        id="sintaxe",
        name="Sintaxe",
        model_id="reasoning",
        metaprompt=json.dumps({
            "text": (
                """
                Avalie exclusivamente a FORMA GRÁFICA da escrita no texto em português, presente na imagem.\n"
                "NÃO avalie sintaxe, ortografia, semântica ou qualidade linguística.\n"
                "Descreva padrões de escrita, legibilidade, espaçamento, consistência de letras, alinhamento e outros aspectos gráficos relevantes.\n"
                "Não faça sugestões de correção sintática, ortográfica ou gramatical.\n"
                "A saída deve ser um JSON com a seguinte estrutura:\n"
                "{\n"
                "  'items': [\n"
                "    {\n"
                "      'row': 0,\n"
                "      'url': '',\n"
                "      'aspecto_grafico': '', // descrição do aspecto gráfico avaliado\n"
                "      'observacao': '' // observação sobre a forma da escrita\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Não inclua resumos ou explicações adicionais, apenas os aspectos gráficos observados.\n"
                """
            ),
            "json": True
        }),
        description="Avalia apenas a forma gráfica da escrita, sem considerar sintaxe, ortografia ou semântica."
    )
    transcription_agent = Evaluator(
        id="transcricao",
        name="Transcricao",
        model_id="reasoning",
        metaprompt=json.dumps({
            "text": (
                "Você receberá uma URL da qual deve extrair a imagem e realizar a transcrição fiel do texto manuscrito.\n"
                "NÃO faça nenhuma correção ortográfica, sintática ou semântica.\n"
                "Transcreva exatamente o que está escrito, mesmo que haja erros ou incoerências.\n"
                "Não avalie qualidade linguística.\n"
                "A transcrição deve ser contínua, sem quebras de linha ou hifenizações, mas mantendo integralmente o teor do texto avaliado.\n"
            ),
            "json": True
        }),
        description="Transcreve fielmente o texto manuscrito da imagem, sem qualquer correção."
    )
    consolidation_agent = Evaluator(
        id="consolidacao",
        name="Consolidacao",
        model_id="reasoning",
        metaprompt=json.dumps({
            "text": (
                "Você receberá um conjunto de avaliações sobre a FORMA GRÁFICA da escrita e transcrições fiéis.\n"
                "Consolide as observações sobre a forma da escrita e a fidelidade da transcrição.\n"
                "NÃO faça avaliações ou sugestões de correção ortográfica, sintática ou semântica.\n"
                "Só produza o texto final se houver 99% de certeza na fidelidade da transcrição.\n"
                "A saída deve ser um JSON com a seguinte estrutura:\n"
                "{\n"
                "  'itens': [\n"
                "    {\n"
                "      'row': 0,\n"
                "      'url': '',\n"
                "      'aspecto_grafico': '',\n"
                "      'observacao': '',\n"
                "      'transcricao_final': ''\n"
                "    }\n"
                "  ]\n"
                "}\n"
                "Não inclua resumos ou explicações adicionais, apenas as observações e a transcrição final se aplicável.\n"
            ),
            "json": True
        }),
        description="Consolida apenas observações sobre a forma gráfica e a fidelidade da transcrição."
    )
    swarm = Swarm(
        id="local_sistema",
        agents=[transcription_agent, spelling_agent, syntax_agent, consolidation_agent],
        topic_name="Análise de Redação"
    )

    results = []
    chat_manager = TransliterationChatManager()
    max_rounds = 8
    for idx, row in df.iterrows():
        url = row.get('url_redacao')
        essay_id = row.get('id_redacao')
        if not isinstance(url, str):
            continue
        print(f"Processing row {idx}, URL: {url}")

        essay_obj = Essay(
            id=str(idx),
            topic=row.get('Tema', ''),
            content='',
            explanation=None,
            content_file_location=None,
            theme=None,
            file_url=url
        )
        resources: list[Resource] = []
        try:
            async with orchestrator:
                raw_evaluation = await orchestrator.invoke(
                    swarm,
                    essay_obj,
                    resources,
                    strategy="group",
                    manager=chat_manager,
                    max_rounds=max_rounds
                )
            evaluation = raw_evaluation if isinstance(raw_evaluation, str) else str(raw_evaluation)
            print(f"Result for row {idx}: {evaluation}\n")
            results.append({
                'row': idx,
                'id_redacao': essay_id,
                'url': url,
                'evaluation': evaluation
            })
        except Exception as e:
            print(f"Error processing row {idx}: {e}")

    # Save and sort by 'id_redacao'
    out_file = SRC / 'app/.data' / 'evaluation_results.xlsx'
    df_results = pd.DataFrame(results)
    df_results.sort_values(by='id_redacao', inplace=True)
    df_results.to_excel(out_file, index=False)
    print(f"Saved results to {out_file}")

if __name__ == '__main__':
    asyncio.run(main())
