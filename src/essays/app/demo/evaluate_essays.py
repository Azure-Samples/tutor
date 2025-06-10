"""
Script to read essays_source.xlsx from .data folder, process each essay image URL, run agentic interaction, and save results.
Requires: pandas, openpyxl, python-dotenv
"""

import io
import sys
import asyncio
import json
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

ROOT = Path(__file__).resolve().parents[4]
SRC = ROOT / 'src/essays'
sys.path.append(str(SRC))

from app.essays import EssayOrchestrator  # pylint: disable=import-error
from app.schemas import Essay, Resource, Evaluator, Swarm  # pylint: disable=import-error

def get_excel_path() -> Path:
    """Return the path to essays_source.xlsx in the .data folder."""
    return SRC / 'app/.data' / 'essays_source.xlsx'


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
                """Avalie detalhadamente a ortografia do texto em português compartilhado na imagem fornecida através de uma URL.
                Considere o texto transcrito da imagem, que apresenta correções de hifenização e quebras de linha.
                Considere regras ortográficas, acentuação, uso correto de letras e possíveis erros comuns.
                Explique cada erro identificado e sugira a correção adequada.
                Caso você identifique erros ortográficos na interpretação direta da imagem, use o Document Intelligence para realizar uma avaliação mais profunda no texto.
                A saída deve ser um JSON com a seguinte estrutura:
                {
                "items": [
                    {
                    "row": 0,           // integer: original row number
                    "url": "",        // string: image URL
                    "error": "",      // string: error type or summary
                    "reason": "",     // string: explanation why it's an error
                    "correction": ""  // string: suggested correction text
                    }
                ]
                }
                Não inclua resumos ou explicações adicionais, apenas erros e correções.
                """

            ),
            "json": True
        }),
        description="Avalia a ortografia do texto, considerando as regras ortográficas nativas do português."
    )
    syntax_agent = Evaluator(
        id="sintaxe",
        name="Sintaxe",
        model_id="reasoning",
        metaprompt=json.dumps({
            "text": (
                """Analise detalhadamente a sintaxe do texto em português, que pode estar presente em uma imagem.
                Considere o texto transcrito da imagem, que apresenta correções de hifenização e quebras de linha.
                Identifique e classifique precisamente cada erro de sintaxe encontrado, especificando o tipo de erro
                (por exemplo: concordância verbal, concordância nominal, regência, pontuação, estrutura de frases, etc).
                Explique cada erro identificado e sugira a correção adequada.
                Caso você identifique erros sintáticos na interpretação direta da imagem, use o Document Intelligence para realizar uma avaliação mais profunda no texto.
                
                A saída deve ser um JSON com a seguinte estrutura:
                {
                "items": [
                    {
                    "row": 0,           // integer: original row number
                    "url": "",        // string: image URL
                    "error": "",      // string: error type or summary
                    "reason": "",     // string: explanation why it's an error
                    "correction": ""  // string: suggested correction text
                    }
                ]
                }
                Não inclua resumos ou explicações adicionais, apenas erros e correções.
                """
            ),
            "json": True
        }),
        description="Avalia as regras sintáticas do texto, considerando as regras sintáticas nativas do português."
    )
    transcription_agent = Evaluator(
        id="transcricao",
        name="Transcricao",
        model_id="default",
        metaprompt=json.dumps({
            "text": (
                "Você receberá uma URL da qual deve extrair a imagem e realizar a transcrição da imagem em texto. "
                "O texto transcrito deve ser formatado de forma contínua, sem quebras de linha ou hifenizações. "
                "Você deve ser muito preciso ao identificar as quebras de linha e hifenizações. "
                "NUNCA APLIQUE CORREÇÕES GRAMATICAIS, SINTÁTICAS OU ORTOGRÁFICAS NESTE PASSO, "
                "apenas transcreva o texto da imagem, MANTENDO INTEGRALMENTE O TEOR DO TEXTO AVALIADO."
            ),
            "json": True
        }),
        description="Transcreve o texto de uma imagem, eliminando quebras de linha e hifenizações."
    )
    consolidation_agent = Evaluator(
        id="consolidacao",
        name="Consolidacao",
        model_id="reasoning",
        metaprompt=json.dumps({
            "text": (
                """Você receberá um conjunto de avaliações sobre um texto transcrito. 
                Você deve listar todos os erros identificados, assim como as melhorias propostas NOS PASSOS ANTERIORES.
                Consolide todas as sugestões DE CORREÇÃO em uma lista de trechos com as devidas correções propostas.
                Não adicione resumos, sendo bem suscinto em sua avaliação e nas propostas de melhoria.
                
                A saída deve ser um JSON com a seguinte estrutura:
                {
                "items": [
                    {
                    "row": 0,           // integer: original row number
                    "url": "",        // string: image URL
                    "error": "",      // string: error type or summary
                    "reason": "",     // string: explanation why it's an error
                    "correction": ""  // string: suggested correction text
                    }
                ]
                }
                Não inclua resumos ou explicações adicionais, apenas erros e correções.
                """
            ),
            "json": True
        }),
        description="Consolida a avaliação e as correções necessárias."
    )
    swarm = Swarm(
        id="local_sistema",
        agents=[transcription_agent, spelling_agent, syntax_agent, consolidation_agent],
        topic_name="Análise de Redação"
    )

    results = []
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

                raw_evaluation = await orchestrator.run_interaction(swarm, essay_obj, resources, 'sequential')
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
