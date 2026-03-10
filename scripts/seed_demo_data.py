"""
Seed script for Brazilian K-12 + Economics Undergraduate demo data.

Targets the tutor platform APIM endpoints to populate:
  - Questions (apps/questions)
  - Essays + Resources (apps/essays)
  - Avatar Cases (apps/avatar)

All content is in Brazilian Portuguese (PT-BR).

Brazilian education structure:
  Ensino Fundamental I  (1º ao 5º ano)
  Ensino Fundamental II (6º ao 9º ano)
  Ensino Médio          (1ª a 3ª série)
  Graduação - Ciências Econômicas

Usage:
    python scripts/seed_demo_data.py [--base-url URL] [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import asdict, dataclass, field
from urllib.request import Request, urlopen
from urllib.error import HTTPError

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_BASE_URL = "https://tutor-prod-apim.azure-api.net"


def _id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Data Classes matching the platform schemas
# ---------------------------------------------------------------------------

@dataclass
class Question:
    id: str
    topic: str
    question: str
    explanation: str | None = None


@dataclass
class Essay:
    id: str
    topic: str
    content: str
    explanation: str | None = None
    theme: str | None = None
    assembly_id: str | None = None


@dataclass
class Resource:
    id: str
    essay_id: str
    objective: list[str]
    content: str | None = None
    url: str | None = None


@dataclass
class Case:
    id: str
    name: str
    role: str
    steps: list[dict] = field(default_factory=list)
    profile: dict = field(default_factory=dict)
    history: list[dict] = field(default_factory=list)


@dataclass
class Theme:
    id: str
    name: str
    objective: str
    description: str
    criteria: list[str] = field(default_factory=list)


@dataclass
class EvaluationDataset:
    dataset_id: str
    name: str
    items: list[dict[str, str]] = field(default_factory=list)


@dataclass
class EssayAgent:
    """Agent definition for essay assembly (no id → Foundry creates new agent)."""
    name: str
    instructions: str
    role: str = "default"
    deployment: str = "gpt-5-nano"
    temperature: float | None = None


@dataclass
class EssayAssemblyDef:
    """Essay assembly — POST will provision real Foundry agents."""
    id: str
    topic_name: str
    essay_id: str
    agents: list[EssayAgent] = field(default_factory=list)


@dataclass
class QuestionGrader:
    """Grader agent for question assembly (metadata only)."""
    name: str
    deployment: str
    instructions: str
    dimension: str
    agent_id: str | None = None


@dataclass
class QuestionAssemblyDef:
    """Question assembly — pure metadata, agents created ephemerally."""
    id: str
    topic_name: str
    agents: list[QuestionGrader] = field(default_factory=list)


# ---------------------------------------------------------------------------
# QUESTIONS — Brazilian K-12 + Economics Undergrad
# ---------------------------------------------------------------------------

QUESTIONS: list[Question] = [
    # ── Ensino Fundamental I (1º ao 5º ano) ──────────────────────────────
    Question(
        id="q-fund1-mat-001",
        topic="Matemática — 2º ano — Adição e Subtração",
        question="Maria tinha 15 figurinhas e ganhou mais 8 de sua amiga. Quantas figurinhas Maria tem agora?",
        explanation="Somamos 15 + 8 = 23. Maria agora tem 23 figurinhas.",
    ),
    Question(
        id="q-fund1-mat-002",
        topic="Matemática — 3º ano — Multiplicação",
        question="Uma caixa tem 6 lápis. Se o professor comprou 4 caixas, quantos lápis ele tem no total?",
        explanation="Multiplicamos 6 × 4 = 24. O professor tem 24 lápis.",
    ),
    Question(
        id="q-fund1-port-001",
        topic="Língua Portuguesa — 4º ano — Interpretação de texto",
        question=(
            "Leia o trecho: 'O sabiá cantava alegremente no galho da mangueira enquanto o sol "
            "nascia por trás das montanhas.' Qual é o cenário descrito no trecho?"
        ),
        explanation=(
            "O cenário é uma manhã ao ar livre, com uma mangueira, montanhas ao fundo e "
            "o nascer do sol. O sabiá está no galho, indicando um ambiente natural e tranquilo."
        ),
    ),
    Question(
        id="q-fund1-cien-001",
        topic="Ciências — 5º ano — Ciclo da Água",
        question="Explique com suas palavras as três etapas principais do ciclo da água.",
        explanation=(
            "1) Evaporação: a água dos rios, mares e lagos é aquecida pelo sol e se transforma em vapor. "
            "2) Condensação: o vapor sobe, esfria e forma as nuvens. "
            "3) Precipitação: quando as nuvens ficam carregadas, a água cai em forma de chuva, "
            "voltando para rios, mares e solo."
        ),
    ),
    Question(
        id="q-fund1-geo-001",
        topic="Geografia — 3º ano — Paisagem Natural e Modificada",
        question=(
            "Observe os exemplos: uma floresta e uma cidade. "
            "Qual é a diferença entre paisagem natural e paisagem modificada?"
        ),
        explanation=(
            "A paisagem natural é aquela que não foi alterada pelo ser humano, como florestas e rios. "
            "A paisagem modificada (ou cultural) foi transformada pela ação humana, como cidades, "
            "estradas e plantações."
        ),
    ),

    # ── Ensino Fundamental II (6º ao 9º ano) ─────────────────────────────
    Question(
        id="q-fund2-mat-001",
        topic="Matemática — 7º ano — Equações de 1º Grau",
        question="Resolva a equação: 3x + 7 = 22. Qual é o valor de x?",
        explanation="3x + 7 = 22 → 3x = 22 − 7 → 3x = 15 → x = 5.",
    ),
    Question(
        id="q-fund2-mat-002",
        topic="Matemática — 8º ano — Porcentagem",
        question=(
            "Um produto custa R$ 120,00 e está com 25% de desconto. "
            "Qual é o valor final do produto?"
        ),
        explanation="Desconto = 120 × 0,25 = R$ 30,00. Valor final = 120 − 30 = R$ 90,00.",
    ),
    Question(
        id="q-fund2-hist-001",
        topic="História — 8º ano — Independência do Brasil",
        question=(
            "Quais foram os principais fatores que levaram à proclamação da independência do Brasil em 1822?"
        ),
        explanation=(
            "Os principais fatores incluem: 1) A transferência da corte portuguesa para o Brasil em 1808, "
            "que elevou o país a Reino Unido; 2) As ideias iluministas e os movimentos liberais; "
            "3) A pressão das Cortes de Lisboa para recolonizar o Brasil; 4) Os interesses econômicos "
            "das elites brasileiras que não queriam perder a autonomia adquirida."
        ),
    ),
    Question(
        id="q-fund2-cien-001",
        topic="Ciências — 9º ano — Tabela Periódica",
        question=(
            "Os elementos químicos são organizados na tabela periódica de acordo com que critério principal? "
            "O que são os períodos e as famílias (grupos)?"
        ),
        explanation=(
            "O critério principal é o número atômico crescente. "
            "Períodos são as linhas horizontais — indicam o número de camadas eletrônicas. "
            "Famílias (grupos) são as colunas verticais — agrupam elementos com propriedades "
            "químicas semelhantes por terem a mesma configuração de elétrons de valência."
        ),
    ),
    Question(
        id="q-fund2-port-001",
        topic="Língua Portuguesa — 9º ano — Figuras de Linguagem",
        question=(
            'Identifique a figura de linguagem presente na frase: "Aquele aluno é um Einstein da turma."'
        ),
        explanation=(
            "A figura de linguagem é uma metáfora. Compara-se o aluno a Einstein de forma implícita, "
            "sugerindo que ele é muito inteligente, sem usar 'como' ou 'tal qual' (o que seria comparação/símile)."
        ),
    ),

    # ── Ensino Médio (1ª a 3ª série) ─────────────────────────────────────
    Question(
        id="q-em-mat-001",
        topic="Matemática — 1ª série EM — Função Afim",
        question=(
            "Uma empresa de táxi cobra uma taxa fixa de R$ 5,00 mais R$ 2,50 por quilômetro rodado. "
            "Escreva a função que representa o custo C em função da distância d (em km). "
            "Quanto custa uma corrida de 12 km?"
        ),
        explanation=(
            "C(d) = 5 + 2,5d. Para d = 12: C(12) = 5 + 2,5 × 12 = 5 + 30 = R$ 35,00."
        ),
    ),
    Question(
        id="q-em-fis-001",
        topic="Física — 2ª série EM — Leis de Newton",
        question=(
            "Um corpo de 10 kg está sobre uma superfície horizontal sem atrito. "
            "Uma força horizontal de 30 N é aplicada. Qual é a aceleração do corpo?"
        ),
        explanation=(
            "Pela segunda lei de Newton: F = m × a → 30 = 10 × a → a = 3 m/s²."
        ),
    ),
    Question(
        id="q-em-qui-001",
        topic="Química — 2ª série EM — Estequiometria",
        question=(
            "Na reação 2H₂ + O₂ → 2H₂O, quantos mols de água são produzidos "
            "a partir de 5 mols de gás hidrogênio?"
        ),
        explanation=(
            "A proporção estequiométrica é 2 mol H₂ : 2 mol H₂O, ou seja, 1:1. "
            "Portanto, 5 mols de H₂ produzem 5 mols de H₂O."
        ),
    ),
    Question(
        id="q-em-bio-001",
        topic="Biologia — 3ª série EM — Genética Mendeliana",
        question=(
            "Em ervilhas, a cor amarela (A) é dominante sobre a verde (a). "
            "Qual a proporção fenotípica esperada no cruzamento de dois heterozigotos (Aa × Aa)?"
        ),
        explanation=(
            "Cruzamento Aa × Aa → AA, Aa, Aa, aa. "
            "Fenótipos: 3 amarelas (AA e Aa) : 1 verde (aa) → proporção 3:1."
        ),
    ),
    Question(
        id="q-em-socio-001",
        topic="Sociologia — 3ª série EM — Desigualdade Social",
        question=(
            "O Índice de Gini é utilizado para medir a desigualdade de renda em um país. "
            "Explique o que significa um Índice de Gini próximo de 0 e próximo de 1."
        ),
        explanation=(
            "Um Índice de Gini próximo de 0 indica igualdade perfeita — todos recebem a mesma renda. "
            "Próximo de 1, indica desigualdade máxima — toda a renda está concentrada em uma única pessoa. "
            "O Brasil historicamente apresenta um dos maiores índices do mundo, refletindo grande concentração de renda."
        ),
    ),

    # ── Graduação — Ciências Econômicas ───────────────────────────────────
    Question(
        id="q-econ-micro-001",
        topic="Microeconomia — Elasticidade-Preço da Demanda",
        question=(
            "Se o preço de um bem aumenta em 10% e a quantidade demandada cai 20%, "
            "qual é a elasticidade-preço da demanda? Classifique o bem."
        ),
        explanation=(
            "Epd = ΔQd% / ΔP% = −20% / 10% = −2. "
            "Como |Epd| > 1, o bem é elástico — a demanda é sensível a variações de preço."
        ),
    ),
    Question(
        id="q-econ-micro-002",
        topic="Microeconomia — Estruturas de Mercado",
        question=(
            "Diferencie concorrência perfeita de monopólio quanto ao número de firmas, "
            "tipo de produto e barreiras à entrada."
        ),
        explanation=(
            "Concorrência perfeita: muitas firmas, produto homogêneo, sem barreiras. "
            "Monopólio: uma única firma, produto sem substitutos próximos, barreiras elevadas "
            "(legais, tecnológicas ou naturais). "
            "No monopólio, a firma é formadora de preço; na concorrência perfeita, é tomadora de preço."
        ),
    ),
    Question(
        id="q-econ-macro-001",
        topic="Macroeconomia — PIB e Métodos de Cálculo",
        question=(
            "Quais são as três óticas de cálculo do PIB? "
            "Explique brevemente cada uma."
        ),
        explanation=(
            "1) Ótica da Produção: soma do valor adicionado de todos os setores. "
            "2) Ótica da Renda: soma das remunerações dos fatores de produção (salários, lucros, juros, aluguéis). "
            "3) Ótica da Despesa: C + I + G + (X − M), onde C = consumo, I = investimento, G = gastos do governo, "
            "X = exportações, M = importações."
        ),
    ),
    Question(
        id="q-econ-macro-002",
        topic="Macroeconomia — Política Monetária",
        question=(
            "Explique como o Banco Central do Brasil utiliza a taxa Selic para controlar a inflação."
        ),
        explanation=(
            "Quando a inflação está acima da meta, o COPOM (Comitê de Política Monetária) eleva a taxa Selic. "
            "Juros mais altos encarecem o crédito, desestimulam consumo e investimento, reduzindo a demanda "
            "agregada e pressionando os preços para baixo. O contrário ocorre quando a inflação está abaixo da meta."
        ),
    ),
    Question(
        id="q-econ-brasil-001",
        topic="Economia Brasileira — Plano Real",
        question=(
            "Descreva as principais fases de implementação do Plano Real (1994) e por que ele "
            "foi bem-sucedido no combate à hiperinflação."
        ),
        explanation=(
            "Fases: 1) Ajuste fiscal (Programa de Ação Imediata e Fundo Social de Emergência) "
            "para equilibrar as contas públicas. "
            "2) URV (Unidade Real de Valor) — indexador universal que alinhou preços relativos. "
            "3) Introdução da nova moeda (Real) com âncora cambial e metas de expansão monetária. "
            "O sucesso se deveu à eliminação da memória inflacionária via URV, ao ajuste fiscal "
            "e à credibilidade da equipe econômica."
        ),
    ),
    Question(
        id="q-econ-inter-001",
        topic="Economia Internacional — Balança Comercial",
        question=(
            "O que é a balança comercial? Por que o Brasil costuma apresentar superávit comercial "
            "e quais são os riscos de depender da exportação de commodities?"
        ),
        explanation=(
            "A balança comercial é a diferença entre exportações e importações de bens. "
            "O Brasil apresenta superávit porque é grande exportador de commodities agropecuárias "
            "e minerais (soja, minério de ferro, petróleo). "
            "Os riscos incluem: vulnerabilidade à oscilação de preços internacionais, "
            "dependência de poucos produtos (reprimarização), desindustrialização "
            "e deterioração dos termos de troca."
        ),
    ),
    Question(
        id="q-econ-estat-001",
        topic="Estatística Econômica — Medidas de Tendência Central",
        question=(
            "As rendas mensais (em R$) de 7 trabalhadores são: "
            "1.500, 1.800, 2.000, 2.000, 2.500, 3.200, 15.000. "
            "Calcule a média e a mediana. Qual medida é mais representativa neste caso? Justifique."
        ),
        explanation=(
            "Média = (1.500+1.800+2.000+2.000+2.500+3.200+15.000) / 7 = 28.000 / 7 ≈ R$ 4.000,00. "
            "Mediana (valor central com dados ordenados) = R$ 2.000,00. "
            "A mediana é mais representativa porque a média é distorcida pelo valor extremo (R$ 15.000). "
            "Isso ilustra como outliers afetam a média aritmética."
        ),
    ),
]


# ---------------------------------------------------------------------------
# ESSAYS + RESOURCES — Brazilian K-12 + Economics Undergrad
# ---------------------------------------------------------------------------

ESSAYS: list[Essay] = [
    # ── Ensino Fundamental I ──────────────────────────────────────────────
    Essay(
        id="essay-fund1-001",
        topic="Produção de texto — 5º ano — Minha cidade",
        content=(
            "## Texto de Apoio — Descrevendo Lugares\n\n"
            "Leia o texto abaixo como exemplo de descrição:\n\n"
            "> *Recife é uma cidade que parece abraçar o mar. Das pontes sobre o rio Capibaribe, "
            "vemos os prédios coloridos do Recife Antigo refletidos na água escura. "
            "O cheiro de tapioca mistura-se com a brisa salgada que vem da praia de Boa Viagem. "
            "Nas ruas estreitas do bairro de São José, vendedores de frutas oferecem mangas "
            "maduras e cajus vermelhos, enquanto o som do frevo ecoa de alguma loja de discos. "
            "É uma cidade quente, barulhenta e cheia de vida.*\n\n"
            "### Elementos de um bom texto descritivo:\n"
            "- **Adjetivos**: palavras que qualificam (coloridos, estreitas, quente)\n"
            "- **Detalhes sensoriais**: visão, olfato, audição, tato, paladar\n"
            "- **Organização espacial**: descrever do geral para o particular\n"
            "- **Opinião pessoal**: o que torna o lugar especial para o autor"
        ),
        explanation=(
            "## Proposta de Redação\n\n"
            "Escreva um **texto descritivo** sobre a cidade ou bairro onde você mora. "
            "Inclua características como paisagens, comércios, pessoas e o que você mais gosta do lugar.\n\n"
            "## Critérios de Avaliação\n\n"
            "| Critério | Pontos |\n"
            "|----------|--------|\n"
            "| Uso de adjetivos para descrever o lugar | 2,5 |\n"
            "| Organização em parágrafos (introdução, meio, fim) | 3,0 |\n"
            "| Ortografia e pontuação adequadas ao nível | 2,5 |\n"
            "| Criatividade e riqueza de detalhes sensoriais | 2,0 |\n"
            "| **Total** | **10,0** |"
        ),
        theme="default",
    ),

    # ── Ensino Fundamental II ─────────────────────────────────────────────
    Essay(
        id="essay-fund2-001",
        topic="Texto argumentativo — 9º ano — Uso de celulares na escola",
        content=(
            "## Textos Motivadores\n\n"
            "### Texto 1 — Opinião de uma professora\n"
            "> *O celular em sala de aula é uma fonte constante de distração. "
            "Os alunos não conseguem se concentrar por mais de cinco minutos sem verificar "
            "notificações. Pesquisas da Universidade do Texas (2017) mostram que a simples "
            "presença do celular sobre a mesa reduz a capacidade cognitiva, mesmo desligado.*\n\n"
            "### Texto 2 — Opinião de um especialista em tecnologia educacional\n"
            "> *Proibir o celular é negar uma ferramenta que os alunos já dominam. "
            "Com planejamento pedagógico, o smartphone pode ser usado para pesquisas, "
            "exercícios interativos e até produção de conteúdo. A escola precisa ensinar "
            "a usar a tecnologia de forma responsável, não bani-la.*\n\n"
            "### Dados\n"
            "- 83% dos adolescentes brasileiros de 13 a 17 anos possuem smartphone (TIC Kids Online Brasil, 2023)\n"
            "- A UNESCO recomendou em 2023 a regulação do uso de celulares em escolas, "
            "mas não a proibição total"
        ),
        explanation=(
            "## Proposta de Redação\n\n"
            "Com base nos textos motivadores, escreva um **texto argumentativo** sobre o uso "
            "de celulares em sala de aula. Apresente uma tese clara, argumentos a favor e contra, "
            "e defenda uma posição com base em evidências.\n\n"
            "## Critérios de Avaliação\n\n"
            "| Critério | Pontos |\n"
            "|----------|--------|\n"
            "| Tese clara e bem definida | 2,0 |\n"
            "| Argumentos com evidências ou exemplos | 3,0 |\n"
            "| Contra-argumento identificado e refutado | 2,0 |\n"
            "| Coerência e coesão entre parágrafos | 2,0 |\n"
            "| Conclusão que retoma a tese | 1,0 |\n"
            "| **Total** | **10,0** |"
        ),
        theme="analytical",
    ),
    Essay(
        id="essay-fund2-002",
        topic="Narrativa — 7º ano — Uma aventura inesperada",
        content=(
            "## Texto de Apoio — Elementos da Narrativa\n\n"
            "Leia o trecho abaixo e observe os elementos narrativos:\n\n"
            "> *Lucas nunca imaginaria que aquele verão mudaria tudo. Na manhã de sábado, "
            "enquanto caminhava pela trilha atrás do sítio da avó, tropeçou em algo metálico "
            "escondido entre as folhas. Era uma caixa de ferro, enferrujada, com um cadeado "
            "antigo. O coração disparou. Quem teria deixado ali? E por quê?*\n\n"
            "### Elementos narrativos a observar:\n"
            "- **Narrador**: quem conta a história (1ª ou 3ª pessoa)\n"
            "- **Personagens**: quem participa da história (protagonista, coadjuvantes)\n"
            "- **Tempo**: quando a história acontece (manhã de sábado, verão)\n"
            "- **Espaço**: onde se passa (trilha, sítio da avó)\n"
            "- **Conflito**: o problema que move a narrativa (a caixa misteriosa)\n"
            "- **Clímax**: o ponto de maior tensão\n"
            "- **Desfecho**: como a história termina"
        ),
        explanation=(
            "## Proposta de Redação\n\n"
            "Crie uma **narrativa** sobre um personagem que, durante uma viagem de férias, "
            "encontra algo misterioso que muda completamente seus planos. "
            "Use todos os elementos narrativos: narrador, personagens, tempo, espaço e conflito.\n\n"
            "## Critérios de Avaliação\n\n"
            "| Critério | Pontos |\n"
            "|----------|--------|\n"
            "| Presença dos elementos narrativos (narrador, personagens, tempo, espaço) | 3,0 |\n"
            "| Progressão do enredo (início, conflito, clímax, desfecho) | 3,0 |\n"
            "| Uso de recursos descritivos e diálogos | 2,0 |\n"
            "| Criatividade e originalidade | 2,0 |\n"
            "| **Total** | **10,0** |"
        ),
        theme="narrative",
    ),

    # ── Ensino Médio ──────────────────────────────────────────────────────
    Essay(
        id="essay-em-001",
        topic="Redação ENEM — Desigualdade no acesso à educação digital no Brasil",
        content=(
            "## Coletânea de Textos Motivadores\n\n"
            "### Texto 1\n"
            "Segundo a PNAD Contínua (IBGE, 2023), cerca de **23 milhões de brasileiros** "
            "não possuem acesso à internet. A exclusão digital atinge desproporcionalmente "
            "famílias com renda de até 1 salário mínimo e populações de áreas rurais, "
            "onde apenas 57% dos domicílios têm conexão.\n\n"
            "### Texto 2\n"
            "Durante a pandemia de COVID-19, estima-se que **5,5 milhões de estudantes** "
            "brasileiros não conseguiram acompanhar aulas remotas por falta de equipamento "
            "ou conectividade (Unicef, 2021). Nas regiões Norte e Nordeste, o índice de "
            "exclusão chegou a 40% dos alunos da rede pública.\n\n"
            "### Texto 3\n"
            "> *A educação digital não se resume a ter um computador. Envolve letramento "
            "digital, formação de professores, infraestrutura de conectividade e políticas "
            "públicas integradas. Sem esses pilares, a tecnologia na escola é apenas "
            "um adereço.* — Professora Débora Garofalo, finalista do Global Teacher Prize 2019.\n\n"
            "### Texto 4 (Imagem descrita)\n"
            "Gráfico do IBGE mostrando a evolução do acesso à internet por faixa de renda "
            "entre 2018 e 2023: classes A/B passaram de 95% para 99%; classes D/E, de 42% para 62%."
        ),
        explanation=(
            "## Proposta de Redação\n\n"
            "A partir da leitura dos textos motivadores e com base nos conhecimentos "
            "construídos ao longo de sua formação, redija um texto **dissertativo-argumentativo** "
            "sobre o tema: **\"Os desafios para garantir o acesso igualitário à educação digital no Brasil\"**. "
            "Apresente proposta de intervenção que respeite os direitos humanos.\n\n"
            "## Critérios de Avaliação — Modelo ENEM (0 a 200 por competência)\n\n"
            "| Competência | Descrição | Peso |\n"
            "|-------------|-----------|------|\n"
            "| **C1** — Domínio da norma culta | Demonstrar domínio da modalidade escrita formal da língua portuguesa | 200 |\n"
            "| **C2** — Compreensão do tema | Compreender a proposta de redação e aplicar conceitos de várias áreas para desenvolver o tema dentro dos limites estruturais do texto dissertativo-argumentativo | 200 |\n"
            "| **C3** — Argumentação | Selecionar, relacionar, organizar e interpretar informações, fatos, opiniões e argumentos em defesa de um ponto de vista | 200 |\n"
            "| **C4** — Coesão textual | Demonstrar conhecimento dos mecanismos linguísticos necessários para a construção da argumentação (conectivos, referenciação, sequenciação) | 200 |\n"
            "| **C5** — Proposta de intervenção | Elaborar proposta de intervenção para o problema abordado, respeitando os direitos humanos. Deve conter: agente, ação, modo/meio, efeito e detalhamento | 200 |\n"
            "| **Total** | | **1.000** |"
        ),
        theme="analytical",
    ),
    Essay(
        id="essay-em-002",
        topic="Redação ENEM — Saúde mental de jovens brasileiros",
        content=(
            "## Coletânea de Textos Motivadores\n\n"
            "### Texto 1\n"
            "A Organização Mundial da Saúde (OMS) estima que o **Brasil é o país mais ansioso do "
            "mundo**, com 9,3% da população sofrendo de transtornos de ansiedade. "
            "Entre jovens de 15 a 29 anos, o suicídio é a **quarta causa de morte** (2019).\n\n"
            "### Texto 2\n"
            "A pesquisa *Saúde do Adolescente* (Fiocruz, 2022) revelou que **29% dos adolescentes "
            "brasileiros** apresentaram sintomas de depressão durante e após a pandemia. "
            "O uso excessivo de redes sociais foi apontado como fator agravante em 67% dos casos.\n\n"
            "### Texto 3\n"
            "> *O estigma é a maior barreira para o tratamento. Muitos jovens não procuram ajuda "
            "porque têm medo de serem julgados por colegas, familiares ou pela própria escola. "
            "Precisamos criar ambientes seguros para falar sobre saúde mental.* "
            "— Dr. Guilherme Polanczyk, psiquiatra infantojuvenil da USP.\n\n"
            "### Texto 4\n"
            "Em 2022, o governo federal sancionou a Lei nº 14.819, que institui a Política Nacional "
            "de Atenção Psicossocial nas Comunidades Escolares, prevendo a presença de "
            "psicólogos e assistentes sociais nas escolas públicas."
        ),
        explanation=(
            "## Proposta de Redação\n\n"
            "Redija um texto **dissertativo-argumentativo** sobre o tema: "
            "**\"O estigma associado às doenças mentais entre os jovens brasileiros\"**. "
            "Considere dados sobre saúde mental no Brasil, o papel das redes sociais "
            "e proponha medidas concretas para enfrentar o problema.\n\n"
            "## Critérios de Avaliação — Modelo ENEM (0 a 200 por competência)\n\n"
            "| Competência | Descrição | Peso |\n"
            "|-------------|-----------|------|\n"
            "| **C1** — Domínio da norma culta | Modalidade escrita formal, sem desvios graves | 200 |\n"
            "| **C2** — Compreensão do tema | Uso de repertório sociocultural (dados OMS, Fiocruz, legislação) para desenvolver o tema | 200 |\n"
            "| **C3** — Argumentação | Articulação de argumentos: relação redes sociais × saúde mental, estigma × acesso ao tratamento | 200 |\n"
            "| **C4** — Coesão textual | Uso adequado de conectivos e mecanismos de referenciação | 200 |\n"
            "| **C5** — Proposta de intervenção | Proposta detalhada envolvendo governo, escolas e famílias, com agente, ação, meio e efeito | 200 |\n"
            "| **Total** | | **1.000** |"
        ),
        theme="analytical",
    ),

    # ── Graduação — Ciências Econômicas ───────────────────────────────────
    Essay(
        id="essay-econ-001",
        topic="Macroeconomia — Política fiscal expansionista e o multiplicador keynesiano",
        content=(
            "## Material de Referência\n\n"
            "### O Modelo IS-LM e o Multiplicador Keynesiano\n\n"
            "O multiplicador keynesiano simples é dado por:\n\n"
            "$$k = \\frac{1}{1 - c(1-t) + m}$$\n\n"
            "onde *c* = propensão marginal a consumir, *t* = alíquota tributária marginal "
            "e *m* = propensão marginal a importar.\n\n"
            "No modelo IS-LM, uma política fiscal expansionista (↑G ou ↓T) desloca a curva "
            "IS para a direita, elevando renda (Y) e taxa de juros (i). A elevação dos juros "
            "gera **efeito crowding out** parcial, reduzindo o multiplicador efetivo.\n\n"
            "### Contexto Brasileiro Recente\n\n"
            "| Indicador | 2022 | 2023 | 2024 |\n"
            "|-----------|------|------|------|\n"
            "| Dívida Bruta/PIB | 73,5% | 74,4% | 76,1% |\n"
            "| Resultado Primário (% PIB) | +0,5% | −1,4% | −0,6% |\n"
            "| Taxa Selic | 13,75% | 11,75% | 10,50% |\n\n"
            "O Novo Arcabouço Fiscal (Lei Complementar nº 200/2023) substituiu o "
            "Teto de Gastos e limita o crescimento real da despesa primária a 70% do "
            "crescimento real da receita.\n\n"
            "### Leitura complementar\n"
            "- BLANCHARD, O. *Macroeconomia*. 8ª ed. Cap. 5 (Mercado de bens e financeiro: o modelo IS-LM).\n"
            "- GIAMBIAGI, F.; ALÉM, A. C. *Finanças Públicas*. 6ª ed. Cap. 3 (Política Fiscal)."
        ),
        explanation=(
            "## Proposta de Ensaio Acadêmico\n\n"
            "Analise os efeitos de uma política fiscal expansionista sobre o PIB utilizando "
            "o modelo do multiplicador keynesiano. Considere o contexto brasileiro recente "
            "e discuta as limitações do modelo quando aplicado a economias emergentes.\n\n"
            "## Rubrica de Avaliação — Ensaio Acadêmico de Macroeconomia\n\n"
            "| Critério | Peso | Excelente (90-100%) | Satisfatório (60-89%) | Insuficiente (<60%) |\n"
            "|----------|------|---------------------|----------------------|---------------------|\n"
            "| Domínio conceitual (IS-LM, multiplicador) | 25% | Domínio completo e preciso | Domínio parcial com imprecisões menores | Erros conceituais graves |\n"
            "| Aplicação ao contexto brasileiro | 25% | Uso de dados reais (dívida/PIB, Selic, arcabouço fiscal) com análise crítica | Menção a dados sem análise profunda | Sem contextualização brasileira |\n"
            "| Análise crítica das limitações | 25% | Discute crowding out, expectativas racionais, vazamentos, equivalência ricardiana | Menciona limitações superficialmente | Ausência de análise crítica |\n"
            "| Clareza, referências e normas ABNT | 25% | Texto claro, bem estruturado, com referências adequadas | Estrutura razoável com poucas referências | Texto desorganizado, sem referências |"
        ),
        theme="analytical",
    ),
    Essay(
        id="essay-econ-002",
        topic="Economia Brasileira — Desindustrialização e reprimarização da pauta exportadora",
        content=(
            "## Material de Referência\n\n"
            "### Dados sobre a Indústria Brasileira\n\n"
            "A participação da **indústria de transformação no PIB** brasileiro:\n"
            "- 1985: ~21%\n"
            "- 2000: ~17%\n"
            "- 2010: ~15%\n"
            "- 2023: ~11% (IBGE/CNI)\n\n"
            "### Pauta Exportadora (2023)\n"
            "| Produto | % das Exportações |\n"
            "|---------|-------------------|\n"
            "| Soja e derivados | 14% |\n"
            "| Petróleo bruto | 13% |\n"
            "| Minério de ferro | 10% |\n"
            "| Carnes | 7% |\n"
            "| Açúcar e etanol | 4% |\n"
            "| Manufaturados | ~25% (em queda) |\n\n"
            "### Marco Teórico\n\n"
            "**Doença Holandesa** (Corden & Neary, 1982): a descoberta de recursos naturais "
            "abundantes valoriza a moeda local, tornando a indústria nacional menos "
            "competitiva e acelerando a desindustrialização.\n\n"
            "**Custo Brasil**: conjunto de fatores estruturais que encarecem a produção "
            "no país — carga tributária complexa, infraestrutura logística deficiente, "
            "burocracia, juros elevados e insegurança jurídica.\n\n"
            "### Leitura complementar\n"
            "- BRESSER-PEREIRA, L. C. *Doença Holandesa e Indústria*. Ed. FGV, 2010.\n"
            "- BONELLI, R.; PESSÔA, S. *Desindustrialização no Brasil: um resumo da evidência*. IBRE/FGV, 2010."
        ),
        explanation=(
            "## Proposta de Ensaio Acadêmico\n\n"
            "Discorra sobre o processo de desindustrialização brasileira nas últimas décadas. "
            "Analise as causas (câmbio, abertura comercial, custo Brasil), as evidências "
            "(participação da indústria no PIB) e as consequências para o desenvolvimento econômico.\n\n"
            "## Rubrica de Avaliação\n\n"
            "| Critério | Peso | Descrição |\n"
            "|----------|------|-----------|\n"
            "| Conhecimento histórico-econômico | 25% | Evolução da indústria dos anos 1980 ao presente, marcos regulatórios |\n"
            "| Uso de dados e indicadores | 25% | Participação no PIB, composição exportadora, emprego industrial |\n"
            "| Articulação teórica | 25% | Doença holandesa, cadeia de valor, termos de troca, custo Brasil |\n"
            "| Análise crítica e propositiva | 25% | Avaliação das consequências e possíveis caminhos (política industrial, inovação) |"
        ),
        theme="analytical",
    ),
    Essay(
        id="essay-econ-003",
        topic="Microeconomia — Teoria dos Jogos aplicada ao oligopólio brasileiro",
        content=(
            "## Material de Referência\n\n"
            "### Conceitos Fundamentais de Teoria dos Jogos\n\n"
            "**Equilíbrio de Nash**: combinação de estratégias em que nenhum jogador pode "
            "melhorar seu resultado alterando unilateralmente sua estratégia.\n\n"
            "**Dilema do Prisioneiro**: jogo em que a estratégia individualmente racional "
            "(trair) leva a um resultado coletivamente inferior à cooperação. "
            "Aplica-se a acordos de cartel: cada firma tem incentivo para trair o acordo "
            "e reduzir preços, mas se ambas traem, ambas perdem.\n\n"
            "### O Mercado de Telecomunicações no Brasil\n\n"
            "| Operadora | Market Share (2024) |\n"
            "|-----------|--------------------|\n"
            "| Vivo (Telefônica) | 38% |\n"
            "| Claro (América Móvil) | 33% |\n"
            "| TIM | 24% |\n"
            "| Outras | 5% |\n\n"
            "Características do mercado:\n"
            "- **Oligopólio concentrado**: 3 grandes firmas controlam 95%\n"
            "- **Altas barreiras à entrada**: licenças, espectro, infraestrutura (bilhões em investimento)\n"
            "- **Comportamento coordenado**: preços e planos muito semelhantes entre operadoras\n"
            "- **Guerras de preços esporádicas**: promoções agressivas em datas específicas\n\n"
            "### Leitura complementar\n"
            "- FIANI, R. *Teoria dos Jogos — com aplicações em economia*. 4ª ed. Elsevier.\n"
            "- VARIAN, H. *Microeconomia — uma abordagem moderna*. 9ª ed. Cap. 28 (Oligopólio)."
        ),
        explanation=(
            "## Proposta de Ensaio Acadêmico\n\n"
            "Utilize conceitos de Teoria dos Jogos (Equilíbrio de Nash, dilema do prisioneiro) "
            "para analisar o comportamento das empresas de telecomunicações no mercado brasileiro. "
            "Discuta como o cartel tácito e as guerras de preços afetam o consumidor.\n\n"
            "## Rubrica de Avaliação\n\n"
            "| Critério | Peso | Descrição |\n"
            "|----------|------|-----------|\n"
            "| Domínio conceitual de Teoria dos Jogos | 30% | Definição precisa de Nash Equilibrium, dilema do prisioneiro, estratégias dominantes |\n"
            "| Aplicação ao caso real (telecom) | 25% | Uso de dados do mercado, análise de coordenação de preços, barreiras à entrada |\n"
            "| Análise de bem-estar social | 25% | Impacto sobre preços ao consumidor, qualidade do serviço, inovação |\n"
            "| Rigor acadêmico e clareza | 20% | Estrutura do ensaio, uso de notação formal quando apropriado, referências |"
        ),
        theme="analytical",
    ),
]

RESOURCES: list[Resource] = [
    # Resources for essay-fund2-001 (argumentative text on cell phones)
    Resource(
        id="res-fund2-001-rubric",
        essay_id="essay-fund2-001",
        objective=["structure", "argumentation"],
        content=(
            "Critérios de avaliação — Texto argumentativo 9º ano:\n"
            "1. Tese clara e bem definida (2 pontos)\n"
            "2. Argumentos com evidências ou exemplos (3 pontos)\n"
            "3. Contra-argumento identificado e refutado (2 pontos)\n"
            "4. Coerência e coesão entre parágrafos (2 pontos)\n"
            "5. Conclusão que retoma a tese (1 ponto)"
        ),
    ),

    # Resources for essay-em-001 (ENEM — digital education)
    Resource(
        id="res-em-001-text1",
        essay_id="essay-em-001",
        objective=["conceptual"],
        content=(
            "Texto motivador 1: Segundo pesquisa do IBGE (PNAD Contínua 2023), "
            "cerca de 23 milhões de brasileiros não têm acesso à internet. "
            "A exclusão digital afeta desproporcionalmente famílias de baixa renda "
            "e populações rurais."
        ),
    ),
    Resource(
        id="res-em-001-text2",
        essay_id="essay-em-001",
        objective=["conceptual"],
        content=(
            "Texto motivador 2: Durante a pandemia de COVID-19, estima-se que "
            "5,5 milhões de estudantes brasileiros não conseguiram acompanhar "
            "aulas remotas por falta de equipamento ou conectividade (Unicef, 2021)."
        ),
    ),

    # Resources for essay-em-002 (ENEM — mental health)
    Resource(
        id="res-em-002-text1",
        essay_id="essay-em-002",
        objective=["conceptual"],
        content=(
            "Texto motivador: A OMS estima que o Brasil é o país mais ansioso do mundo, "
            "com 9,3% da população sofrendo de transtornos de ansiedade (2019). "
            "Entre jovens de 15 a 29 anos, o suicídio é a quarta causa de morte."
        ),
    ),

    # Resources for essay-econ-001 (Keynesian multiplier)
    Resource(
        id="res-econ-001-rubric",
        essay_id="essay-econ-001",
        objective=["conceptual", "argumentation"],
        content=(
            "Rubrica de avaliação — Ensaio acadêmico de Macroeconomia:\n"
            "1. Domínio conceitual do multiplicador keynesiano e modelo IS-LM (25%)\n"
            "2. Aplicação ao contexto brasileiro com dados/exemplos (25%)\n"
            "3. Análise crítica das limitações do modelo (25%)\n"
            "4. Clareza argumentativa, referências e normas ABNT (25%)"
        ),
    ),

    # Resources for essay-econ-002 (deindustrialization)
    Resource(
        id="res-econ-002-data",
        essay_id="essay-econ-002",
        objective=["conceptual"],
        content=(
            "Dados: A participação da indústria de transformação no PIB brasileiro caiu de "
            "cerca de 21% em 1985 para aproximadamente 11% em 2023 (IBGE/CNI). "
            "A pauta exportadora em 2023: soja (14%), petróleo (13%), minério de ferro (10%), "
            "carnes (7%), açúcar (4%)."
        ),
    ),

    # Resources for fund1 essay (descriptive text)
    Resource(
        id="res-fund1-001-rubric",
        essay_id="essay-fund1-001",
        objective=["spelling", "semantics", "structure"],
        content=(
            "Critérios de avaliação — Texto descritivo 5º ano:\n"
            "1. Uso de adjetivos para descrever o lugar (2 pontos)\n"
            "2. Organização em parágrafos (introdução, meio, fim) (3 pontos)\n"
            "3. Ortografia e pontuação adequadas ao nível (3 pontos)\n"
            "4. Criatividade e riqueza de detalhes (2 pontos)"
        ),
    ),
]


# ---------------------------------------------------------------------------
# THEMES — Configuration service (Brazilian education themes)
# ---------------------------------------------------------------------------

THEMES: list[Theme] = [
    # ── Ensino Fundamental I (1º ao 5º ano) ──────────────────────────────
    Theme(
        id="theme-fund1-descritivo",
        name="Minha Cidade — Texto Descritivo",
        objective=(
            "Desenvolver a capacidade de observação e descrição do espaço urbano ou rural "
            "em que o aluno vive, usando linguagem sensorial adequada ao Ensino Fundamental I."
        ),
        description=(
            "Tema voltado para alunos do 1º ao 5º ano. O estudante deve descrever "
            "sua cidade ou bairro utilizando adjetivos, detalhes sensoriais (visão, olfato, "
            "audição) e organização espacial (do geral para o particular). Incentiva o "
            "vínculo afetivo com o lugar e a expressão pessoal."
        ),
        criteria=[
            "Uso adequado de adjetivos para qualificar elementos do lugar",
            "Presença de detalhes sensoriais (pelo menos 3 sentidos)",
            "Organização do texto em parágrafos com introdução, meio e fim",
            "Ortografia e pontuação adequadas ao nível do 5º ano",
            "Criatividade e expressão de opinião pessoal sobre o lugar",
        ],
    ),
    Theme(
        id="theme-fund1-informativo",
        name="Animais do Brasil — Texto Informativo",
        objective=(
            "Estimular a pesquisa e a produção de textos informativos sobre a fauna "
            "brasileira, integrando Ciências e Língua Portuguesa."
        ),
        description=(
            "O aluno escolhe um animal típico do Brasil (onça-pintada, arara-azul, "
            "boto-cor-de-rosa, mico-leão-dourado etc.) e produz um texto informativo "
            "com características físicas, habitat, alimentação e curiosidades. "
            "Trabalha habilidades de leitura, pesquisa e escrita expositiva."
        ),
        criteria=[
            "Informações corretas sobre o animal escolhido",
            "Organização em tópicos ou parágrafos temáticos",
            "Linguagem clara e acessível ao público infantil",
            "Uso de vocabulário científico básico (habitat, espécie, alimentação)",
        ],
    ),

    # ── Ensino Fundamental II (6º ao 9º ano) ─────────────────────────────
    Theme(
        id="theme-fund2-argumentativo",
        name="Uso de Celulares na Escola — Texto Argumentativo",
        objective=(
            "Desenvolver a competência argumentativa do aluno, exigindo tese, "
            "argumentos com evidências, contra-argumento e conclusão."
        ),
        description=(
            "Tema polêmico e próximo da realidade dos alunos do 6º ao 9º ano. "
            "Exige leitura de textos motivadores com diferentes perspectivas "
            "(professores, especialistas, dados de pesquisa) e posicionamento "
            "fundamentado. Trabalha o gênero texto argumentativo conforme a BNCC."
        ),
        criteria=[
            "Tese clara e bem definida no parágrafo de introdução",
            "Pelo menos dois argumentos sustentados por evidências ou exemplos",
            "Identificação e refutação de contra-argumento",
            "Coerência e coesão entre parágrafos (uso de conectivos)",
            "Conclusão que retoma a tese de forma convincente",
        ],
    ),
    Theme(
        id="theme-fund2-narrativo",
        name="Uma Aventura Inesperada — Texto Narrativo",
        objective=(
            "Exercitar a criação de narrativas ficcionais com todos os elementos "
            "estruturais: narrador, personagens, tempo, espaço, conflito, clímax e desfecho."
        ),
        description=(
            "O aluno do 7º ao 9º ano cria uma narrativa a partir de um mote: "
            "durante uma viagem de férias, o personagem encontra algo misterioso "
            "que muda seus planos. O tema permite explorar suspense, aventura "
            "e criatividade, além de trabalhar diálogos e descrições."
        ),
        criteria=[
            "Presença dos elementos narrativos (narrador, personagens, tempo, espaço)",
            "Progressão do enredo: situação inicial → conflito → clímax → desfecho",
            "Uso de recursos descritivos e diálogos bem pontuados",
            "Criatividade e originalidade da trama",
        ],
    ),

    # ── Ensino Médio / ENEM ──────────────────────────────────────────────
    Theme(
        id="theme-em-educacao-digital",
        name="Educação Digital — Desigualdade no Acesso",
        objective=(
            "Preparar o aluno para a redação dissertativo-argumentativa no modelo ENEM, "
            "trabalhando as 5 competências da matriz de referência."
        ),
        description=(
            "Tema inspirado em provas do ENEM: \"Os desafios para garantir o acesso "
            "igualitário à educação digital no Brasil\". Aborda exclusão digital, "
            "desigualdade socioeconômica, impacto da pandemia nas escolas públicas "
            "e o papel das políticas públicas. Exige proposta de intervenção com agente, "
            "ação, meio, efeito e detalhamento."
        ),
        criteria=[
            "C1 — Domínio da norma culta da língua portuguesa",
            "C2 — Compreensão do tema e uso de repertório sociocultural",
            "C3 — Seleção e organização de argumentos com progressão",
            "C4 — Coesão textual (conectivos, referenciação, sequenciação)",
            "C5 — Proposta de intervenção completa e que respeite os direitos humanos",
        ],
    ),
    Theme(
        id="theme-em-saude-mental",
        name="Saúde Mental dos Jovens Brasileiros",
        objective=(
            "Abordar o estigma da saúde mental entre jovens, exigindo argumentação "
            "com dados epidemiológicos e proposta de intervenção social."
        ),
        description=(
            "O aluno analisa o estigma associado às doenças mentais entre jovens "
            "brasileiros, usando dados da OMS, Fiocruz e legislação (Lei 14.819/2022). "
            "Deve considerar o papel das redes sociais como fator agravante e propor "
            "medidas envolvendo governo, escolas e famílias."
        ),
        criteria=[
            "C1 — Adequação ao registro formal da língua",
            "C2 — Uso produtivo de repertório (dados OMS, Fiocruz, legislação)",
            "C3 — Articulação de argumentos: redes sociais × saúde mental, estigma × tratamento",
            "C4 — Mecanismos linguísticos de coesão e referenciação",
            "C5 — Proposta de intervenção detalhada com agente, ação, meio e efeito",
        ],
    ),
    Theme(
        id="theme-em-trabalho-infantil",
        name="Trabalho Infantil no Brasil — Desafios e Soluções",
        objective=(
            "Sensibilizar o aluno para a problemática do trabalho infantil, "
            "exigindo análise de dados e proposta de intervenção nos direitos humanos."
        ),
        description=(
            "O Brasil ainda possui mais de 1,8 milhão de crianças e adolescentes "
            "em situação de trabalho infantil (PNAD 2022). O tema exige que o aluno "
            "discuta causas estruturais (pobreza, desigualdade, evasão escolar), "
            "marcos legais (ECA, Convenção OIT 182) e proponha soluções que "
            "garantam o direito à infância e à educação."
        ),
        criteria=[
            "C1 — Domínio da modalidade escrita formal",
            "C2 — Compreensão do tema com repertório pertinente (ECA, OIT, dados IBGE)",
            "C3 — Argumentos consistentes sobre causas e consequências do trabalho infantil",
            "C4 — Coesão e coerência na articulação dos parágrafos",
            "C5 — Proposta de intervenção que respeite os direitos da criança e do adolescente",
        ],
    ),

    # ── Graduação — Ciências Econômicas ───────────────────────────────────
    Theme(
        id="theme-econ-politica-fiscal",
        name="Política Fiscal Expansionista e o Multiplicador Keynesiano",
        objective=(
            "Avaliar a capacidade do aluno de graduação em articular o modelo IS-LM, "
            "o multiplicador keynesiano e suas limitações no contexto brasileiro."
        ),
        description=(
            "Ensaio acadêmico sobre os efeitos de uma expansão fiscal sobre o PIB. "
            "O aluno deve dominar o multiplicador keynesiano simples (k = 1/(1-c(1-t)+m)), "
            "discutir o efeito crowding out no modelo IS-LM e contextualizar com dados "
            "brasileiros recentes (dívida/PIB, Selic, Novo Arcabouço Fiscal)."
        ),
        criteria=[
            "Domínio conceitual do multiplicador e do modelo IS-LM",
            "Aplicação ao contexto macroeconômico brasileiro com dados reais",
            "Análise crítica das limitações (crowding out, expectativas racionais, equivalência ricardiana)",
            "Clareza argumentativa, referências bibliográficas e normas ABNT",
        ],
    ),
    Theme(
        id="theme-econ-desindustrializacao",
        name="Desindustrialização e Reprimarização da Pauta Exportadora",
        objective=(
            "Analisar o processo de desindustrialização brasileira com rigor "
            "empírico e articulação teórica (doença holandesa, custo Brasil)."
        ),
        description=(
            "A participação da indústria de transformação no PIB caiu de ~21%% (1985) "
            "para ~11%% (2023). O aluno deve discutir causas (câmbio apreciado, abertura "
            "comercial, boom de commodities), evidências (indicadores de emprego e produção) "
            "e consequências para o desenvolvimento econômico de longo prazo."
        ),
        criteria=[
            "Conhecimento histórico-econômico da indústria brasileira (1980-presente)",
            "Uso correto de dados e indicadores (participação no PIB, composição exportadora)",
            "Articulação teórica: doença holandesa, cadeia de valor, custo Brasil",
            "Análise crítica e propostas (política industrial, inovação, educação)",
        ],
    ),
    Theme(
        id="theme-econ-teoria-jogos",
        name="Teoria dos Jogos Aplicada ao Oligopólio Brasileiro",
        objective=(
            "Aplicar conceitos de Teoria dos Jogos (Nash, dilema do prisioneiro) "
            "à análise de mercados oligopolísticos reais no Brasil."
        ),
        description=(
            "O aluno utiliza o ferramental de Teoria dos Jogos para analisar o "
            "comportamento das empresas de telecomunicações no Brasil (Vivo, Claro, TIM). "
            "Deve construir matrizes de payoff, identificar equilíbrios de Nash e discutir "
            "como o cartel tácito e guerras de preços afetam o bem-estar do consumidor. "
            "Espera-se referência ao papel do CADE e da Anatel na regulação."
        ),
        criteria=[
            "Domínio conceitual: Equilíbrio de Nash, dilema do prisioneiro, estratégias dominantes",
            "Aplicação ao caso real com dados de market share e barreiras à entrada",
            "Análise de bem-estar social: preços, qualidade, inovação, peso morto",
            "Rigor acadêmico: estrutura do ensaio, notação formal, referências bibliográficas",
        ],
    ),
]


# ---------------------------------------------------------------------------
# ESSAY ASSEMBLIES — Each POSTs to /api/essays/assemblies and provisions
# real Azure AI Foundry agents (agent.id omitted → auto-created).
# ---------------------------------------------------------------------------

ESSAY_ASSEMBLIES: list[EssayAssemblyDef] = [
    # ── Ensino Fundamental I ──────────────────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-fund1-001",
        topic_name="Produção de texto — 5º ano — Minha cidade",
        essay_id="essay-fund1-001",
        agents=[
            EssayAgent(
                name="Avaliador de Escrita Fund. I",
                role="default",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um avaliador de redações para alunos do 5º ano do Ensino Fundamental. "
                    "Analise o texto do aluno considerando:\n"
                    "1. Ortografia e pontuação adequadas ao nível do 5º ano\n"
                    "2. Uso correto de adjetivos e vocabulário descritivo\n"
                    "3. Organização em parágrafos (introdução, desenvolvimento, conclusão)\n\n"
                    "Seja encorajador e construtivo. Aponte erros de forma didática, "
                    "sugerindo a forma correta. Use linguagem acessível para crianças de 10-11 anos. "
                    "Responda sempre em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Avaliador de Conteúdo Fund. I",
                role="narrative",
                deployment="gpt-5-nano",
                temperature=0.4,
                instructions=(
                    "Você é um avaliador de conteúdo de redações para alunos do 5º ano. "
                    "Analise se o texto descritivo do aluno:\n"
                    "1. Apresenta detalhes sensoriais (visão, audição, olfato, tato)\n"
                    "2. Usa organização espacial coerente (do geral para o particular ou vice-versa)\n"
                    "3. Demonstra criatividade e opinião pessoal sobre o lugar descrito\n"
                    "4. Conecta as ideias de forma lógica\n\n"
                    "Valorize a criatividade e a expressão pessoal. Dê sugestões positivas "
                    "para enriquecer o texto. Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Ensino Fundamental II — Argumentativo ─────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-fund2-001",
        topic_name="Texto argumentativo — 9º ano — Uso de celulares na escola",
        essay_id="essay-fund2-001",
        agents=[
            EssayAgent(
                name="Avaliador de Argumentação",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um professor de Língua Portuguesa especializado em textos argumentativos "
                    "para alunos do 9º ano do Ensino Fundamental II. Avalie a redação nos seguintes critérios:\n"
                    "1. **Tese**: O aluno apresenta uma tese clara e defendível?\n"
                    "2. **Argumentos**: Os argumentos são sustentados por evidências ou exemplos?\n"
                    "3. **Contra-argumento**: O aluno identifica e refuta a posição contrária?\n"
                    "4. **Conclusão**: A conclusão retoma a tese de forma convincente?\n\n"
                    "Atribua uma nota de 0 a 10 e justifique cada critério. "
                    "Seja exigente mas formativo. Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Avaliador de Linguagem Fund. II",
                role="default",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um revisor linguístico para textos de alunos do 9º ano. Avalie:\n"
                    "1. **Coerência**: As ideias se conectam logicamente entre parágrafos?\n"
                    "2. **Coesão**: O aluno usa conectivos adequados (porém, além disso, portanto)?\n"
                    "3. **Gramática**: Concordância verbal e nominal, regência, ortografia\n"
                    "4. **Vocabulário**: Adequação ao gênero argumentativo\n\n"
                    "Aponte os erros com a correção sugerida. Destaque também os acertos. "
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Ensino Fundamental II — Narrativo ─────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-fund2-002",
        topic_name="Narrativa — 7º ano — Uma aventura inesperada",
        essay_id="essay-fund2-002",
        agents=[
            EssayAgent(
                name="Avaliador Narrativo Fund. II",
                role="narrative",
                deployment="gpt-5-nano",
                temperature=0.4,
                instructions=(
                    "Você é um professor de produção textual para alunos do 7º ano, "
                    "especializado em textos narrativos. Avalie a narrativa considerando:\n"
                    "1. **Elementos narrativos**: Presença de narrador, personagens, tempo, espaço e conflito\n"
                    "2. **Estrutura do enredo**: Situação inicial → conflito → clímax → desfecho\n"
                    "3. **Recursos literários**: Uso de diálogos, descrições, suspense\n"
                    "4. **Criatividade**: Originalidade da trama, surpresas no enredo\n\n"
                    "Valorize a imaginação do aluno. Sugira melhorias de forma motivadora. "
                    "Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Avaliador de Estilo Fund. II",
                role="narrative",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um revisor de estilo para narrativas de alunos do 7º ano. Avalie:\n"
                    "1. **Vocabulário**: Uso de adjetivos, advérbios e verbos expressivos\n"
                    "2. **Pontuação de diálogos**: Uso correto de travessão, aspas, pontuação\n"
                    "3. **Coesão temporal**: Uso adequado de tempos verbais e marcadores temporais\n"
                    "4. **Ortografia e gramática**: Adequação ao nível do 7º ano\n\n"
                    "Aponte erros com correções sugeridas. Elogie trechos bem escritos. "
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Ensino Médio — ENEM 1 ────────────────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-em-001",
        topic_name="Redação ENEM — Desigualdade no acesso à educação digital no Brasil",
        essay_id="essay-em-001",
        agents=[
            EssayAgent(
                name="Corretor ENEM — Linguagem",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.2,
                instructions=(
                    "Você é um corretor oficial de redações do ENEM. Avalie as competências "
                    "C1 e C4 da matriz de referência:\n\n"
                    "**C1 — Domínio da norma culta (0-200)**:\n"
                    "- Desvios gramaticais (concordância, regência, crase, pontuação)\n"
                    "- Adequação ao registro formal\n"
                    "- Convenções da escrita (ortografia, acentuação)\n\n"
                    "**C4 — Coesão textual (0-200)**:\n"
                    "- Uso de conectivos (porém, ademais, portanto, não obstante)\n"
                    "- Referenciação (pronomes, sinônimos, hiperônimos)\n"
                    "- Sequenciação lógica dos parágrafos\n\n"
                    "Atribua nota de 0 a 200 para cada competência (múltiplos de 40). "
                    "Justifique com exemplos do texto. Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Corretor ENEM — Conteúdo",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.2,
                instructions=(
                    "Você é um corretor oficial de redações do ENEM. Avalie as competências "
                    "C2 e C3 da matriz de referência:\n\n"
                    "**C2 — Compreensão do tema (0-200)**:\n"
                    "- O aluno compreendeu a proposta (educação digital no Brasil)?\n"
                    "- Usou repertório sociocultural produtivo (dados, autores, filósofos, leis)?\n"
                    "- Respeitou a tipologia dissertativo-argumentativa?\n\n"
                    "**C3 — Seleção e organização de argumentos (0-200)**:\n"
                    "- Os argumentos são consistentes e bem organizados?\n"
                    "- Há progressão argumentativa (do geral ao específico)?\n"
                    "- Os dados dos textos motivadores foram usados criticamente?\n\n"
                    "Atribua nota de 0 a 200 para cada competência (múltiplos de 40). "
                    "Indique trechos fortes e fracos. Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Corretor ENEM — Proposta",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.2,
                instructions=(
                    "Você é um corretor oficial de redações do ENEM. Avalie a competência "
                    "C5 da matriz de referência:\n\n"
                    "**C5 — Proposta de intervenção (0-200)**:\n"
                    "Para nota máxima, a proposta deve conter 5 elementos:\n"
                    "1. **Agente**: quem vai executar (governo, MEC, escolas, ONGs, etc.)\n"
                    "2. **Ação**: o que será feito (programa, política, campanha)\n"
                    "3. **Modo/Meio**: como será implementado (por meio de, através de)\n"
                    "4. **Efeito/Finalidade**: para que (a fim de, com o objetivo de)\n"
                    "5. **Detalhamento**: de um dos elementos acima\n\n"
                    "A proposta deve respeitar os direitos humanos. Propostas que violem DH zeram a C5.\n\n"
                    "Atribua nota de 0 a 200 (múltiplos de 40). Identifique quais elementos "
                    "estão presentes e ausentes. Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Ensino Médio — ENEM 2 ────────────────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-em-002",
        topic_name="Redação ENEM — Saúde mental de jovens brasileiros",
        essay_id="essay-em-002",
        agents=[
            EssayAgent(
                name="Corretor ENEM — Linguagem",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.2,
                instructions=(
                    "Você é um corretor de redações ENEM. Avalie C1 (Domínio da norma culta, 0-200) "
                    "e C4 (Coesão textual, 0-200).\n\n"
                    "C1: Analise desvios gramaticais, registro formal, ortografia e acentuação.\n"
                    "C4: Analise conectivos, referenciação, sequenciação lógica.\n\n"
                    "Atribua nota de 0 a 200 para cada (múltiplos de 40). Justifique com exemplos. "
                    "Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Corretor ENEM — Conteúdo",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.2,
                instructions=(
                    "Você é um corretor de redações ENEM. Avalie C2 (Compreensão do tema, 0-200) "
                    "e C3 (Argumentação, 0-200).\n\n"
                    "C2: O aluno compreendeu o tema do estigma da saúde mental entre jovens? "
                    "Usou repertório produtivo (dados OMS, Fiocruz, Lei 14.819, redes sociais)?\n"
                    "C3: Os argumentos são consistentes? Há progressão argumentativa?\n\n"
                    "Atribua nota de 0 a 200 para cada (múltiplos de 40). "
                    "Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Corretor ENEM — Proposta",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.2,
                instructions=(
                    "Você é um corretor de redações ENEM. Avalie C5 (Proposta de intervenção, 0-200).\n\n"
                    "A proposta deve conter: agente, ação, modo/meio, efeito e detalhamento. "
                    "Espera-se envolvimento de governo, escolas e famílias no combate ao estigma da saúde mental.\n\n"
                    "A proposta deve respeitar os direitos humanos.\n"
                    "Atribua nota de 0 a 200 (múltiplos de 40). Identifique elementos presentes e ausentes. "
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Graduação — Macroeconomia ─────────────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-econ-001",
        topic_name="Macroeconomia — Política fiscal expansionista e o multiplicador keynesiano",
        essay_id="essay-econ-001",
        agents=[
            EssayAgent(
                name="Avaliador Teórico — Macro",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um professor de Macroeconomia de uma universidade brasileira. "
                    "Avalie o ensaio acadêmico do aluno de graduação em Ciências Econômicas nos seguintes aspectos:\n\n"
                    "1. **Domínio conceitual** (25%): O aluno domina o modelo IS-LM e o multiplicador keynesiano? "
                    "Define corretamente PMgC, alíquota tributária, vazamentos, crowding out?\n"
                    "2. **Análise crítica das limitações** (25%): Discute expectativas racionais, "
                    "equivalência ricardiana, armadilha de liquidez, contexto de economia aberta?\n\n"
                    "Use rigor acadêmico. Aponte imprecisões conceituais. Sugira aprofundamentos teóricos. "
                    "Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Avaliador Empírico — Macro",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um economista especializado em economia brasileira. "
                    "Avalie o ensaio do aluno nos seguintes aspectos:\n\n"
                    "1. **Aplicação ao contexto brasileiro** (25%): O aluno utiliza dados reais "
                    "(dívida/PIB, Selic, resultado primário, Novo Arcabouço Fiscal)? "
                    "A análise do multiplicador no contexto brasileiro é coerente?\n"
                    "2. **Clareza e normas acadêmicas** (25%): Texto claro, bem estruturado, "
                    "com referências bibliográficas e respeito às normas ABNT?\n\n"
                    "Faça observações construtivas sobre o uso de dados e a qualidade da escrita acadêmica. "
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Graduação — Economia Brasileira ───────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-econ-002",
        topic_name="Economia Brasileira — Desindustrialização e reprimarização da pauta exportadora",
        essay_id="essay-econ-002",
        agents=[
            EssayAgent(
                name="Avaliador de Econ. Brasileira",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é professor de Economia Brasileira em uma universidade. "
                    "Avalie o ensaio sobre desindustrialização considerando:\n\n"
                    "1. **Conhecimento histórico** (25%): Evolução industrial dos anos 1980 ao presente, "
                    "abertura comercial (anos 90), boom de commodities (2000-2014)\n"
                    "2. **Uso de dados** (25%): Participação da indústria no PIB, composição exportadora, "
                    "emprego industrial\n\n"
                    "Exija rigor na periodização e no uso de indicadores. "
                    "Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Avaliador Acadêmico — Econ",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um revisor acadêmico de ensaios econômicos. Avalie:\n\n"
                    "1. **Articulação teórica** (25%): Uso correto dos conceitos de doença holandesa, "
                    "cadeia de valor, termos de troca, custo Brasil\n"
                    "2. **Análise crítica e propositiva** (25%): Avaliação das consequências da "
                    "desindustrialização e propostas (política industrial, inovação, educação)\n\n"
                    "Verifique coerência argumentativa e qualidade das referências. "
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Graduação — Microeconomia ─────────────────────────────────────────
    EssayAssemblyDef(
        id="asm-essay-econ-003",
        topic_name="Microeconomia — Teoria dos Jogos aplicada ao oligopólio brasileiro",
        essay_id="essay-econ-003",
        agents=[
            EssayAgent(
                name="Avaliador Teoria dos Jogos",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é professor de Microeconomia especializado em Teoria dos Jogos. "
                    "Avalie o ensaio do aluno de graduação em Economia:\n\n"
                    "1. **Domínio conceitual** (30%): Definição precisa de Equilíbrio de Nash, "
                    "dilema do prisioneiro, estratégias dominantes, jogos repetidos\n"
                    "2. **Aplicação ao caso real** (25%): Análise do oligopólio de telecomunicações "
                    "com dados de market share, barreiras à entrada, comportamento coordenado\n\n"
                    "Use rigor formal. Se o aluno usar notação de teoria dos jogos (matrizes de payoff), "
                    "verifique a correção. Responda em Português Brasileiro."
                ),
            ),
            EssayAgent(
                name="Avaliador de Bem-Estar Social",
                role="analytical",
                deployment="gpt-5-nano",
                temperature=0.3,
                instructions=(
                    "Você é um economista especializado em regulação e defesa da concorrência. "
                    "Avalie o ensaio considerando:\n\n"
                    "1. **Análise de bem-estar** (25%): Impacto do oligopólio sobre preços ao consumidor, "
                    "qualidade do serviço, inovação, peso morto\n"
                    "2. **Rigor acadêmico** (20%): Estrutura do ensaio, referências, "
                    "notação quando aplicável\n\n"
                    "Avalie se o aluno discute o papel do CADE e da Anatel na regulação. "
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# AVATAR CASES — Brazilian K-12 + Economics Undergrad
# ---------------------------------------------------------------------------

CASES: list[Case] = [
    # ── Ensino Fundamental I — Tutor de Matemática ────────────────────────
    Case(
        id="case-fund1-mat-tutor",
        name="Tutor de Matemática — Ensino Fundamental I",
        role="tutor de matemática para crianças do ensino fundamental",
        profile={
            "role": "tutor de matemática",
            "language": "Português Brasileiro",
            "tone": "paciente, encorajador e lúdico",
            "target_audience": "alunos de 1º ao 5º ano",
            "behavior": (
                "Usa linguagem simples e exemplos do cotidiano das crianças. "
                "Celebra acertos e guia erros com perguntas orientadoras."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Acolhimento",
                "objectives": ["Apresentar-se", "Descobrir o que o aluno está estudando"],
                "vocabulary": ["Olá!", "Vamos aprender juntos?", "O que você está estudando?"],
            },
            {
                "step_number": 2,
                "name": "Exploração do problema",
                "objectives": ["Apresentar um problema de forma lúdica", "Incentivar o raciocínio"],
                "vocabulary": ["Vamos pensar juntos?", "Imagina que..."],
            },
            {
                "step_number": 3,
                "name": "Resolução guiada",
                "objectives": ["Guiar passo a passo sem dar a resposta direta"],
                "vocabulary": ["Qual seria o primeiro passo?", "Muito bem! E agora?"],
            },
            {
                "step_number": 4,
                "name": "Encerramento",
                "objectives": ["Revisar o que foi aprendido", "Motivar para continuar"],
                "vocabulary": ["Parabéns!", "Você está cada vez melhor!"],
            },
        ],
    ),

    # ── Ensino Fundamental II — Tutor de Português ────────────────────────
    Case(
        id="case-fund2-port-tutor",
        name="Tutor de Português — Interpretação e Redação",
        role="professor de língua portuguesa para alunos do 6º ao 9º ano",
        profile={
            "role": "tutor de português",
            "language": "Português Brasileiro",
            "tone": "motivador, claro e exigente na medida certa",
            "target_audience": "alunos de 6º ao 9º ano",
            "behavior": (
                "Ajuda o aluno a interpretar textos, identificar figuras de linguagem, "
                "e construir textos argumentativos. Faz perguntas para estimular o pensamento crítico."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Contextualização",
                "objectives": ["Entender o tema que o aluno está trabalhando"],
            },
            {
                "step_number": 2,
                "name": "Leitura orientada",
                "objectives": ["Ler trechos juntos e discutir significados", "Identificar ideias principais"],
            },
            {
                "step_number": 3,
                "name": "Produção textual",
                "objectives": ["Ajudar o aluno a planejar e redigir seu texto", "Revisar estrutura e coerência"],
            },
            {
                "step_number": 4,
                "name": "Feedback construtivo",
                "objectives": ["Apontar pontos fortes e melhorias", "Incentivar a reescrita"],
            },
        ],
    ),

    # ── Ensino Médio — Simulação ENEM ─────────────────────────────────────
    Case(
        id="case-em-enem-simulador",
        name="Simulador de Correção ENEM",
        role="corretor de redações no modelo ENEM",
        profile={
            "role": "corretor ENEM",
            "language": "Português Brasileiro",
            "tone": "profissional, objetivo e formativo",
            "target_audience": "alunos do Ensino Médio preparando-se para o ENEM",
            "behavior": (
                "Avalia redações seguindo as 5 competências do ENEM. "
                "Fornece nota estimada por competência e sugestões detalhadas de melhoria. "
                "Não aceita fugir do tema proposto."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Receber a redação",
                "objectives": ["Solicitar o tema e o texto do aluno"],
            },
            {
                "step_number": 2,
                "name": "Avaliação por competência",
                "objectives": [
                    "Avaliar C1 — Norma culta",
                    "Avaliar C2 — Compreensão do tema",
                    "Avaliar C3 — Argumentação",
                    "Avaliar C4 — Coesão",
                    "Avaliar C5 — Proposta de intervenção",
                ],
            },
            {
                "step_number": 3,
                "name": "Devolutiva",
                "objectives": ["Apresentar nota estimada", "Dar sugestões específicas de melhoria"],
            },
        ],
    ),

    # ── Ensino Médio — Tutor de Física ────────────────────────────────────
    Case(
        id="case-em-fis-tutor",
        name="Tutor de Física — Mecânica e Termodinâmica",
        role="professor de física especializado em resolução de problemas",
        profile={
            "role": "tutor de física",
            "language": "Português Brasileiro",
            "tone": "didático, usa analogias do cotidiano",
            "target_audience": "alunos do Ensino Médio",
            "behavior": (
                "Explica conceitos de física usando situações do dia a dia. "
                "Resolve problemas passo a passo, pedindo que o aluno participe de cada etapa. "
                "Usa unidades do SI e notação apropriada."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Identificar o conceito",
                "objectives": ["Qual lei ou princípio se aplica?", "Relembrar a fórmula relevante"],
            },
            {
                "step_number": 2,
                "name": "Montar o problema",
                "objectives": ["Identificar dados e incógnita", "Desenhar diagrama se necessário"],
            },
            {
                "step_number": 3,
                "name": "Resolver juntos",
                "objectives": ["Substituir valores", "Calcular passo a passo"],
            },
            {
                "step_number": 4,
                "name": "Verificação",
                "objectives": ["O resultado faz sentido?", "Unidades estão corretas?"],
            },
        ],
    ),

    # ── Graduação — Orientador de Microeconomia ───────────────────────────
    Case(
        id="case-econ-micro-orientador",
        name="Orientador de Microeconomia",
        role="professor universitário de microeconomia",
        profile={
            "role": "professor de microeconomia",
            "language": "Português Brasileiro",
            "tone": "socrático, acadêmico, rigoroso",
            "target_audience": "alunos de graduação em Ciências Econômicas",
            "behavior": (
                "Utiliza o método socrático: faz perguntas que conduzem o aluno a descobrir "
                "os conceitos por conta própria. Espera rigor nos conceitos econômicos, "
                "uso de gráficos e terminologia técnica adequada."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Diagnóstico",
                "objectives": ["Entender o nível do aluno", "Qual tópico precisa de ajuda?"],
                "vocabulary": ["Em que disciplina você está?", "Qual conceito está difícil?"],
            },
            {
                "step_number": 2,
                "name": "Construção conceitual",
                "objectives": [
                    "Conduzir o aluno a definir o conceito com suas palavras",
                    "Corrigir imprecisões conceituais",
                ],
                "vocabulary": ["O que você entende por elasticidade?", "Como isso se relaciona com a curva de demanda?"],
            },
            {
                "step_number": 3,
                "name": "Aplicação",
                "objectives": ["Propor um exercício aplicado ao caso brasileiro"],
                "vocabulary": ["Pense no mercado de combustíveis no Brasil..."],
            },
            {
                "step_number": 4,
                "name": "Síntese",
                "objectives": ["Aluno resume o que aprendeu", "Professor valida ou complementa"],
            },
        ],
    ),

    # ── Graduação — Orientador de Macroeconomia ───────────────────────────
    Case(
        id="case-econ-macro-orientador",
        name="Orientador de Macroeconomia Brasileira",
        role="economista especializado em economia brasileira",
        profile={
            "role": "professor de macroeconomia",
            "language": "Português Brasileiro",
            "tone": "analítico, contextualizado, usa dados reais",
            "target_audience": "alunos de graduação em Ciências Econômicas",
            "behavior": (
                "Sempre contextualiza conceitos macroeconômicos com a realidade brasileira. "
                "Usa dados do IBGE, BCB, IPEA. Discute políticas do Plano Real ao presente. "
                "Incentiva pensamento crítico sobre modelos teóricos vs realidade."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Tema e contexto",
                "objectives": ["Identificar o tema macroeconômico", "Situar no contexto brasileiro"],
            },
            {
                "step_number": 2,
                "name": "Modelo teórico",
                "objectives": ["Apresentar o modelo relevante (IS-LM, OA-DA, etc.)", "Explicar pressupostos"],
            },
            {
                "step_number": 3,
                "name": "Análise empírica",
                "objectives": ["Analisar dados reais da economia brasileira", "Comparar teoria vs prática"],
                "vocabulary": ["Veja o que aconteceu com a Selic em 2015...", "Compare o multiplicador teórico com o real..."],
            },
            {
                "step_number": 4,
                "name": "Debate",
                "objectives": ["Discutir diferentes escolas de pensamento", "Avaliar trade-offs de política econômica"],
            },
        ],
    ),

    # ── Graduação — Entrevista de Estágio em Economia ─────────────────────
    Case(
        id="case-econ-entrevista",
        name="Simulação de Entrevista — Estágio em Economia",
        role="recrutador de banco de investimento ou consultoria econômica",
        profile={
            "role": "recrutador",
            "language": "Português Brasileiro",
            "tone": "profissional, direto, avaliativo",
            "target_audience": "alunos de Ciências Econômicas buscando estágio",
            "behavior": (
                "Simula uma entrevista para estágio em economia/finanças. "
                "Faz perguntas técnicas e comportamentais. Avalia clareza, "
                "domínio conceitual e capacidade analítica. Dá feedback ao final."
            ),
        },
        steps=[
            {
                "step_number": 1,
                "name": "Apresentação",
                "objectives": ["Pedir que o candidato se apresente", "Avaliar comunicação"],
                "vocabulary": ["Conte-me sobre você.", "Por que economia?"],
            },
            {
                "step_number": 2,
                "name": "Perguntas técnicas",
                "objectives": [
                    "Perguntar sobre taxa de juros e inflação",
                    "Case de valuation simples",
                    "Interpretar um indicador econômico",
                ],
            },
            {
                "step_number": 3,
                "name": "Case prático",
                "objectives": ["Apresentar um mini-case de análise econômica", "Avaliar raciocínio estruturado"],
                "vocabulary": ["Uma empresa quer investir no Nordeste. Que fatores você consideraria?"],
            },
            {
                "step_number": 4,
                "name": "Feedback",
                "objectives": ["Resumir desempenho", "Dar pontos fortes e áreas de melhoria"],
            },
        ],
    ),
]


# ---------------------------------------------------------------------------
# QUESTION ASSEMBLIES — Pure metadata (agents created ephemerally during eval).
# One assembly per education level with graders for multiple dimensions.
# ---------------------------------------------------------------------------

QUESTION_ASSEMBLIES: list[QuestionAssemblyDef] = [
    # ── Ensino Fundamental I ──────────────────────────────────────────────
    QuestionAssemblyDef(
        id="asm-quest-fund1",
        topic_name="Ensino Fundamental I — Avaliação Geral",
        agents=[
            QuestionGrader(
                name="Corretor Fund. I — Exatidão",
                deployment="gpt-5-nano",
                dimension="exatidão",
                instructions=(
                    "Você é um professor do Ensino Fundamental I (1º ao 5º ano) avaliando a resposta de um aluno. "
                    "Verifique se a resposta está **correta** considerando o nível esperado para a faixa etária (6-11 anos).\n\n"
                    "- Para questões de Matemática: verifique cálculos e raciocínio numérico\n"
                    "- Para questões de Português: verifique interpretação e compreensão textual\n"
                    "- Para questões de Ciências: verifique conceitos científicos básicos\n"
                    "- Para questões de Geografia: verifique conceitos geográficos\n\n"
                    "Seja encorajador. Reconheça acertos parciais. Explique erros de forma simples. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Corretor Fund. I — Clareza",
                deployment="gpt-5-nano",
                dimension="clareza",
                instructions=(
                    "Você é um professor do Ensino Fundamental I avaliando a **clareza** da resposta do aluno.\n\n"
                    "Considere:\n"
                    "- O aluno explicou seu raciocínio de forma compreensível?\n"
                    "- A resposta está organizada?\n"
                    "- O vocabulário é adequado ao nível?\n\n"
                    "Dê feedback positivo e construtivo. Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Ensino Fundamental II ─────────────────────────────────────────────
    QuestionAssemblyDef(
        id="asm-quest-fund2",
        topic_name="Ensino Fundamental II — Avaliação Geral",
        agents=[
            QuestionGrader(
                name="Corretor Fund. II — Exatidão",
                deployment="gpt-5-nano",
                dimension="exatidão",
                instructions=(
                    "Você é um professor do Ensino Fundamental II (6º ao 9º ano) avaliando respostas. "
                    "Verifique a **correção** da resposta considerando o nível esperado:\n\n"
                    "- Matemática: equações, porcentagem, operações com frações\n"
                    "- História: fatos históricos, relações causais, periodização\n"
                    "- Ciências: conceitos de química, física e biologia básicos\n"
                    "- Português: figuras de linguagem, interpretação avançada, gramática\n\n"
                    "Aceite diferentes formas de expressão desde que conceitualmente corretas. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Corretor Fund. II — Raciocínio",
                deployment="gpt-5-nano",
                dimension="raciocínio",
                instructions=(
                    "Você é um professor do Ensino Fundamental II avaliando o **raciocínio** do aluno.\n\n"
                    "Analise:\n"
                    "- O aluno demonstrou raciocínio lógico e coerente?\n"
                    "- Apresentou os passos da resolução (quando aplicável)?\n"
                    "- Conectou conceitos de forma adequada?\n"
                    "- Justificou suas afirmações?\n\n"
                    "Valorize tentativas de raciocínio mesmo quando a resposta final está incorreta. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Corretor Fund. II — Clareza",
                deployment="gpt-5-nano",
                dimension="clareza",
                instructions=(
                    "Você é um professor do Ensino Fundamental II avaliando a **clareza** da expressão.\n\n"
                    "Considere:\n"
                    "- A resposta está bem organizada e legível?\n"
                    "- O vocabulário é adequado ao nível (12-15 anos)?\n"
                    "- O aluno usa termos técnicos corretamente quando necessário?\n\n"
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Ensino Médio ──────────────────────────────────────────────────────
    QuestionAssemblyDef(
        id="asm-quest-em",
        topic_name="Ensino Médio — Avaliação Geral",
        agents=[
            QuestionGrader(
                name="Corretor EM — Exatidão",
                deployment="gpt-5-nano",
                dimension="exatidão",
                instructions=(
                    "Você é um professor do Ensino Médio avaliando respostas. "
                    "Verifique a **correção conceitual** rigorosamente:\n\n"
                    "- Matemática: funções, trigonometria, análise combinatória\n"
                    "- Física: leis de Newton, termodinâmica, eletricidade\n"
                    "- Química: estequiometria, equilíbrio, química orgânica\n"
                    "- Biologia: genética, ecologia, fisiologia\n"
                    "- Sociologia/Filosofia: conceitos e teorias sociais\n\n"
                    "Exija precisão conceitual própria do nível médio. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Corretor EM — Raciocínio",
                deployment="gpt-5-nano",
                dimension="raciocínio",
                instructions=(
                    "Você é um professor do Ensino Médio avaliando **raciocínio e análise**.\n\n"
                    "Analise:\n"
                    "- O aluno demonstra pensamento crítico e analítico?\n"
                    "- Para exatas: resolução passo a passo, uso correto de fórmulas\n"
                    "- Para humanas: articulação de ideias, relações causais, contexto histórico\n"
                    "- Para biológicas: relação entre conceitos, aplicação a situações-problema\n\n"
                    "Diferencie erros conceituais de erros de cálculo/digitação. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Corretor EM — Profundidade",
                deployment="gpt-5-nano",
                dimension="profundidade",
                instructions=(
                    "Você é um professor do Ensino Médio avaliando a **profundidade** da resposta.\n\n"
                    "Considere:\n"
                    "- O aluno foi além do superficial?\n"
                    "- Estabeleceu conexões com outras áreas ou com o cotidiano?\n"
                    "- Demonstrou compreensão dos porquês, não apenas do como?\n"
                    "- Para questões de humanas: posicionamento crítico?\n\n"
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),

    # ── Graduação — Ciências Econômicas ───────────────────────────────────
    QuestionAssemblyDef(
        id="asm-quest-econ",
        topic_name="Graduação em Ciências Econômicas — Avaliação",
        agents=[
            QuestionGrader(
                name="Avaliador Econ — Exatidão",
                deployment="gpt-5-nano",
                dimension="exatidão",
                instructions=(
                    "Você é um professor universitário de Ciências Econômicas. "
                    "Avalie a **correção conceitual** da resposta do aluno de graduação:\n\n"
                    "- Microeconomia: elasticidade, estruturas de mercado, equilíbrio, bem-estar\n"
                    "- Macroeconomia: PIB, política monetária/fiscal, modelos IS-LM/OA-DA\n"
                    "- Economia Brasileira: Plano Real, Selic, balança comercial, história econômica\n"
                    "- Estatística: medidas de tendência central, dispersão, inferência\n\n"
                    "Exija rigor conceitual universitário. Aponte imprecisões terminológicas. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Avaliador Econ — Raciocínio",
                deployment="gpt-5-nano",
                dimension="raciocínio",
                instructions=(
                    "Você é um professor de Economia avaliando **raciocínio econômico**.\n\n"
                    "Analise:\n"
                    "- O aluno articula relações de causa e efeito corretamente?\n"
                    "- Utiliza modelos econômicos para fundamentar respostas?\n"
                    "- Distingue entre variáveis nominais e reais quando relevante?\n"
                    "- Reconhece trade-offs e custos de oportunidade?\n\n"
                    "Valorize o pensamento econômico estruturado. "
                    "Responda em Português Brasileiro."
                ),
            ),
            QuestionGrader(
                name="Avaliador Econ — Análise Crítica",
                deployment="gpt-5-nano",
                dimension="análise crítica",
                instructions=(
                    "Você é um economista sênior avaliando a **capacidade analítica** do aluno.\n\n"
                    "Considere:\n"
                    "- O aluno contextualiza teoria com a realidade brasileira?\n"
                    "- Usa dados e indicadores para sustentar argumentos?\n"
                    "- Reconhece limitações dos modelos teóricos?\n"
                    "- Apresenta visão crítica de diferentes escolas de pensamento?\n\n"
                    "Responda em Português Brasileiro."
                ),
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# EVALUATION DATASETS — Evaluation service test data
# ---------------------------------------------------------------------------

EVALUATION_DATASETS: list[EvaluationDataset] = [
    EvaluationDataset(
        dataset_id="eval-ds-essay-quality",
        name="Qualidade de Redações — Ensino Médio",
        items=[
            {
                "input": (
                    "A desigualdade no acesso à educação digital é um problema grave no Brasil. "
                    "Segundo dados do IBGE, 23 milhões de brasileiros não possuem acesso à internet. "
                    "É necessário que o governo invista em infraestrutura de conectividade nas regiões "
                    "rurais e periféricas, por meio de parcerias público-privadas, a fim de garantir "
                    "que todos os estudantes tenham condições de acompanhar o ensino digital."
                ),
                "expected_output": (
                    "C1: 160 — Bom domínio da norma culta, poucos desvios. "
                    "C2: 160 — Compreende o tema e usa repertório (dados IBGE). "
                    "C3: 120 — Argumentação superficial, falta progressão. "
                    "C4: 160 — Boa coesão, conectivos adequados. "
                    "C5: 160 — Proposta com agente (governo), ação (investir), meio (parcerias), efeito (garantir acesso). "
                    "Total estimado: 760/1000."
                ),
            },
            {
                "input": (
                    "No brasil a educasão digital é muito importante mais nem todos tem acesso. "
                    "Muitas crianças não tem computador e nem internet. O governo deveria fazer algo."
                ),
                "expected_output": (
                    "C1: 40 — Desvios graves de ortografia (brasil, educasão, mais/mas) e pontuação. "
                    "C2: 80 — Tangencia o tema sem aprofundamento ou repertório. "
                    "C3: 40 — Sem argumentos estruturados. "
                    "C4: 40 — Ausência de conectivos e mecanismos de coesão. "
                    "C5: 40 — Proposta vaga, sem detalhamento. "
                    "Total estimado: 240/1000."
                ),
            },
            {
                "input": (
                    "Consoante o pensamento do filósofo Pierre Lévy, a cibercultura redefine as relações "
                    "sociais e educacionais. Nesse sentido, a desigualdade no acesso à educação digital no "
                    "Brasil constitui um obstáculo à democratização do conhecimento. Dados da PNAD Contínua "
                    "(IBGE, 2023) revelam que 23 milhões de brasileiros permanecem desconectados, sendo a "
                    "exclusão mais severa nas classes D/E e em áreas rurais. Ademais, durante a pandemia, "
                    "5,5 milhões de estudantes foram privados do ensino remoto (Unicef, 2021), evidenciando "
                    "a fragilidade estrutural do sistema educacional. Destarte, urge que o Ministério da "
                    "Educação, em parceria com empresas de telecomunicações, implemente um programa nacional "
                    "de conectividade escolar, por meio da instalação de pontos de acesso gratuito em escolas "
                    "públicas e da distribuição de tablets educacionais, a fim de reduzir a exclusão digital "
                    "e promover a equidade educacional."
                ),
                "expected_output": (
                    "C1: 200 — Excelente domínio da norma culta. "
                    "C2: 200 — Repertório produtivo (Pierre Lévy, IBGE, Unicef). "
                    "C3: 160 — Boa argumentação, poderia aprofundar contra-argumento. "
                    "C4: 200 — Uso exemplar de conectivos (consoante, nesse sentido, ademais, destarte). "
                    "C5: 200 — Proposta completa: agente (MEC), ação (programa de conectividade), "
                    "meio (instalação + distribuição), efeito (reduzir exclusão), detalhamento (tablets). "
                    "Total estimado: 960/1000."
                ),
            },
            {
                "input": (
                    "A saúde mental dos jovens brasileiros merece atenção. Segundo a OMS, o Brasil é o "
                    "país mais ansioso do mundo. As redes sociais agravam o problema ao criar padrões "
                    "irreais de beleza e sucesso. A Lei 14.819 prevê psicólogos nas escolas, mas a "
                    "implementação ainda é lenta. É preciso ampliar o acesso ao atendimento psicológico."
                ),
                "expected_output": (
                    "C1: 160 — Bom domínio da norma culta. "
                    "C2: 160 — Compreende o tema, usa repertório (OMS, Lei 14.819). "
                    "C3: 120 — Argumentos válidos mas pouco desenvolvidos. "
                    "C4: 120 — Coesão razoável, sequenciação simples. "
                    "C5: 80 — Proposta genérica, falta detalhamento de agente e meio. "
                    "Total estimado: 640/1000."
                ),
            },
        ],
    ),
    EvaluationDataset(
        dataset_id="eval-ds-question-accuracy",
        name="Precisão de Respostas — Multidisciplinar",
        items=[
            {
                "input": (
                    "Pergunta: Resolva a equação 3x + 7 = 22. Qual é o valor de x?\n"
                    "Resposta do aluno: x = 5"
                ),
                "expected_output": (
                    "Correto. 3x + 7 = 22 → 3x = 15 → x = 5. "
                    "O aluno demonstrou domínio na resolução de equações de 1º grau. "
                    "Nota de exatidão: 10/10."
                ),
            },
            {
                "input": (
                    "Pergunta: Quais são as três etapas principais do ciclo da água?\n"
                    "Resposta do aluno: Evaporação e chuva."
                ),
                "expected_output": (
                    "Parcialmente correto. O aluno mencionou evaporação e precipitação (chuva), "
                    "mas omitiu a condensação, que é a etapa intermediária em que o vapor forma "
                    "as nuvens. Nota de exatidão: 6/10."
                ),
            },
            {
                "input": (
                    "Pergunta: Se o preço de um bem aumenta 10%% e a quantidade demandada cai 20%%, "
                    "qual é a elasticidade-preço da demanda?\n"
                    "Resposta do aluno: A elasticidade é 2, o bem é inelástico."
                ),
                "expected_output": (
                    "Parcialmente correto. O cálculo está correto: |Epd| = 20%%/10%% = 2. "
                    "Porém a classificação está errada: como |Epd| > 1, o bem é elástico, "
                    "não inelástico. Nota de exatidão: 5/10."
                ),
            },
            {
                "input": (
                    "Pergunta: Na reação 2H₂ + O₂ → 2H₂O, quantos mols de água são "
                    "produzidos a partir de 5 mols de H₂?\n"
                    "Resposta do aluno: 5 mols de água, pois a proporção é 1:1."
                ),
                "expected_output": (
                    "Correto. A proporção estequiométrica é 2 mol H₂ : 2 mol H₂O = 1:1. "
                    "Portanto, 5 mols de H₂ produzem 5 mols de H₂O. "
                    "O aluno demonstrou bom domínio de estequiometria. Nota de exatidão: 10/10."
                ),
            },
        ],
    ),
    EvaluationDataset(
        dataset_id="eval-ds-enem-competencias",
        name="Competências ENEM — Avaliação por Competência",
        items=[
            {
                "input": (
                    "Competência avaliada: C5 (Proposta de intervenção)\n"
                    "Trecho da redação: 'O governo deve investir mais em educação digital.'"
                ),
                "expected_output": (
                    "C5: 40/200. A proposta é extremamente vaga. Contém apenas agente (governo) "
                    "e ação genérica (investir). Faltam: modo/meio de implementação, efeito/finalidade "
                    "esperado e detalhamento de qualquer elemento. Para melhorar, o aluno deve "
                    "especificar qual órgão, que tipo de investimento, como será implementado "
                    "e qual resultado se espera alcançar."
                ),
            },
            {
                "input": (
                    "Competência avaliada: C5 (Proposta de intervenção)\n"
                    "Trecho da redação: 'Destarte, é imprescindível que o Ministério da Educação, "
                    "em parceria com operadoras de telecomunicação, crie o Programa Escola Conectada, "
                    "por meio da instalação de antenas de internet em escolas rurais e da capacitação "
                    "digital de professores, com o fito de garantir que alunos de regiões remotas "
                    "tenham acesso equitativo ao ensino digital.'"
                ),
                "expected_output": (
                    "C5: 200/200. Proposta completa com todos os 5 elementos: "
                    "1) Agente: MEC + operadoras de telecomunicação. "
                    "2) Ação: criar o Programa Escola Conectada. "
                    "3) Meio: instalação de antenas + capacitação de professores. "
                    "4) Efeito: acesso equitativo ao ensino digital. "
                    "5) Detalhamento: escolas rurais, regiões remotas. "
                    "A proposta respeita os direitos humanos."
                ),
            },
            {
                "input": (
                    "Competência avaliada: C1 (Domínio da norma culta)\n"
                    "Trecho: 'A desigualdade no acesso a educação digital constitue um "
                    "obstaculo significativo para o desenvolvimento do pais. Muitos jovens, "
                    "sobre tudo nas regiões mais pobres, não conseguem acompanhar as aulas.'"
                ),
                "expected_output": (
                    "C1: 120/200. Desvios identificados: "
                    "1) 'a educação' → crase obrigatória: 'à educação'. "
                    "2) 'constitue' → forma correta: 'constitui'. "
                    "3) 'obstaculo' → falta acento: 'obstáculo'. "
                    "4) 'pais' → falta acento: 'país'. "
                    "5) 'sobre tudo' → junto: 'sobretudo'. "
                    "O texto demonstra domínio parcial, com desvios frequentes de acentuação "
                    "e crase, mas estrutura sintática adequada."
                ),
            },
        ],
    ),
]


# ---------------------------------------------------------------------------
# Upskilling Plans
# ---------------------------------------------------------------------------

@dataclass
class UpskillingPlan:
    title: str
    timeframe: str
    topic: str
    class_id: str
    paragraphs: list[dict[str, str]] = field(default_factory=list)
    performance_history: list[dict] = field(default_factory=list)


UPSKILLING_PLANS: list[UpskillingPlan] = [
    UpskillingPlan(
        title="Plano Semanal — Cinemática 3A",
        timeframe="week",
        topic="Física — Cinemática",
        class_id="class-3A",
        paragraphs=[
            {"title": "Conceitos Fundamentais", "content": "Introduzir posição, deslocamento e referencial com exemplos do cotidiano dos alunos."},
            {"title": "MRU — Teoria e Prática", "content": "Apresentar equação horária da posição para MRU e resolver 3 exercícios progressivos."},
            {"title": "MRUV — Aceleração", "content": "Conectar MRU ao MRUV, demonstrar queda livre com vídeo e calcular tempo de queda de objetos."},
        ],
        performance_history=[
            {"period": "2025-05", "topic": "Física — Cinemática", "proficiency": 0.68, "highlights": ["MRU bem compreendido"], "gaps": ["Gráficos de MRUV"]},
            {"period": "2025-06", "topic": "Física — Cinemática", "proficiency": 0.72, "highlights": ["Melhoria em exercícios"], "gaps": ["Queda livre"]},
        ],
    ),
    UpskillingPlan(
        title="Plano Mensal — Redação ENEM",
        timeframe="month",
        topic="Língua Portuguesa — Redação",
        class_id="class-EM3",
        paragraphs=[
            {"title": "Estrutura da Redação ENEM", "content": "Explicar modelo introdução-desenvolvimento-conclusão com ênfase nas 5 competências."},
            {"title": "Repertório Sociocultural", "content": "Workshop de leitura e fichamento de artigos para construção de repertório legitimado."},
            {"title": "Proposta de Intervenção", "content": "Exercitar propostas de intervenção detalhadas com agente, meio, modo, efeito e detalhamento."},
            {"title": "Simulado e Correção Coletiva", "content": "Aplicar simulado e corrigir coletivamente com rubrica das 5 competências do ENEM."},
        ],
    ),
    UpskillingPlan(
        title="Plano Semestral — Microeconomia",
        timeframe="semester",
        topic="Economia — Microeconomia",
        class_id="class-ECON-101",
        paragraphs=[
            {"title": "Oferta e Demanda", "content": "Construir curvas de oferta e demanda a partir de dados reais do mercado brasileiro."},
            {"title": "Elasticidade", "content": "Calcular elasticidade-preço da demanda para commodities e bens de luxo, comparando resultados."},
            {"title": "Estruturas de Mercado", "content": "Analisar concorrência perfeita, monopólio e oligopólio com estudos de caso de empresas brasileiras."},
        ],
        performance_history=[
            {"period": "2025-03", "topic": "Economia — Microeconomia", "proficiency": 0.55, "highlights": ["Conceito de oferta e demanda"], "gaps": ["Cálculo de elasticidade"]},
        ],
    ),
    UpskillingPlan(
        title="Plano Semanal — Termodinâmica 2B",
        timeframe="week",
        topic="Física — Termodinâmica",
        class_id="class-2B",
        paragraphs=[
            {"title": "Temperatura e Calor", "content": "Diferenciar temperatura, calor e sensação térmica com experimentos simples em sala."},
            {"title": "Leis da Termodinâmica", "content": "Apresentar a 1ª e 2ª leis com analogias do dia a dia: geladeira, motor de carro."},
        ],
    ),
    UpskillingPlan(
        title="Plano Mensal — Geometria Analítica",
        timeframe="month",
        topic="Matemática — Geometria Analítica",
        class_id="class-3A",
        paragraphs=[
            {"title": "Ponto e Reta", "content": "Revisar distância entre pontos, ponto médio e equação da reta com GeoGebra."},
            {"title": "Circunferência", "content": "Derivar equação da circunferência e resolver problemas de posição relativa ponto-circunferência."},
            {"title": "Cônicas", "content": "Introduzir elipse, hipérbole e parábola como seções cônicas e conectar a aplicações em astronomia."},
        ],
    ),
]


# ---------------------------------------------------------------------------
# HTTP Helper
# ---------------------------------------------------------------------------

def _post(
    base_url: str,
    path: str,
    payload: dict,
    *,
    dry_run: bool,
    extra_headers: dict[str, str] | None = None,
) -> bool:
    """POST JSON to APIM. Returns True on success."""
    url = f"{base_url}{path}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if dry_run:
        print(f"  [DRY-RUN] POST {url}")
        print(f"    {json.dumps(payload, ensure_ascii=False, indent=2)[:300]}...")
        return True
    req = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(req, timeout=120) as resp:
            status = resp.status
            print(f"  ✓ POST {path} → {status}")
            return True
    except HTTPError as exc:
        # 409 = already exists — acceptable for idempotent seed
        if exc.code == 409:
            print(f"  ⚠ POST {path} → 409 (already exists, skipping)")
            return True
        error_body = exc.read().decode("utf-8", errors="replace")[:500]
        print(f"  ✗ POST {path} → {exc.code}: {error_body}")
        return False


def _put(
    base_url: str,
    path: str,
    payload: dict,
    *,
    dry_run: bool,
    extra_headers: dict[str, str] | None = None,
) -> bool:
    """PUT JSON to APIM. Returns True on success."""
    url = f"{base_url}{path}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    if dry_run:
        print(f"  [DRY-RUN] PUT {url}")
        return True
    req = Request(url, data=body, headers=headers, method="PUT")
    try:
        with urlopen(req, timeout=30) as resp:
            print(f"  ✓ PUT {path} → {resp.status}")
            return True
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:500]
        print(f"  ✗ PUT {path} → {exc.code}: {error_body}")
        return False


# ---------------------------------------------------------------------------
# Seed Functions
# ---------------------------------------------------------------------------

def seed_questions(base_url: str, *, dry_run: bool) -> int:
    print("\n═══ Seeding Questions ═══")
    ok = 0
    for q in QUESTIONS:
        payload = asdict(q)
        if _post(base_url, "/api/questions/questions", payload, dry_run=dry_run):
            ok += 1
    print(f"Questions: {ok}/{len(QUESTIONS)} seeded.")
    return ok


def seed_essays(base_url: str, *, dry_run: bool) -> int:
    print("\n═══ Seeding Essays ═══")
    ok = 0
    for e in ESSAYS:
        payload = {k: v for k, v in asdict(e).items() if v is not None}
        if _post(base_url, "/api/essays/essays", payload, dry_run=dry_run):
            ok += 1
    print(f"Essays: {ok}/{len(ESSAYS)} seeded.")
    return ok


def seed_resources(base_url: str, *, dry_run: bool) -> int:
    print("\n═══ Seeding Resources ═══")
    ok = 0
    for r in RESOURCES:
        payload = {k: v for k, v in asdict(r).items() if v is not None}
        if _post(base_url, "/api/essays/resources", payload, dry_run=dry_run):
            ok += 1
    print(f"Resources: {ok}/{len(RESOURCES)} seeded.")
    return ok


def seed_cases(base_url: str, *, dry_run: bool) -> int:
    print("\n═══ Seeding Avatar Cases ═══")
    ok = 0
    for c in CASES:
        payload = asdict(c)
        if _post(base_url, "/api/avatar/create-case", payload, dry_run=dry_run):
            ok += 1
    print(f"Cases: {ok}/{len(CASES)} seeded.")
    return ok


def update_essays(base_url: str, *, dry_run: bool) -> int:
    """PUT-update existing essays with enriched content and explanation."""
    print("\n═══ Updating Essays (PUT) ═══")
    ok = 0
    for e in ESSAYS:
        payload = {k: v for k, v in asdict(e).items() if v is not None and k != "assembly_id"}
        if _put(base_url, f"/api/essays/essays/{e.id}", payload, dry_run=dry_run):
            ok += 1
    print(f"Essays updated: {ok}/{len(ESSAYS)}.")
    return ok


def seed_essay_assemblies(base_url: str, *, dry_run: bool) -> int:
    """POST essay assemblies — will provision real Foundry agents."""
    print("\n═══ Seeding Essay Assemblies (provisions Foundry agents) ═══")
    ok = 0
    for asm in ESSAY_ASSEMBLIES:
        payload = {
            "id": asm.id,
            "topic_name": asm.topic_name,
            "essay_id": asm.essay_id,
            "agents": [
                {k: v for k, v in asdict(a).items() if v is not None}
                for a in asm.agents
            ],
        }
        if _post(base_url, "/api/essays/assemblies", payload, dry_run=dry_run):
            ok += 1
    print(f"Essay assemblies: {ok}/{len(ESSAY_ASSEMBLIES)} seeded.")
    return ok


def _patch(
    base_url: str,
    path: str,
    payload: dict,
    *,
    dry_run: bool,
) -> bool:
    """PATCH JSON to APIM. Returns True on success."""
    url = f"{base_url}{path}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if dry_run:
        print(f"  [DRY-RUN] PATCH {url}")
        return True
    req = Request(url, data=body, headers=headers, method="PATCH")
    try:
        with urlopen(req, timeout=30) as resp:
            print(f"  ✓ PATCH {path} → {resp.status}")
            return True
    except HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")[:500]
        print(f"  ✗ PATCH {path} → {exc.code}: {error_body}")
        return False


def link_essays_to_assemblies(base_url: str, *, dry_run: bool) -> int:
    """Ensure every essay with a matching assembly has assembly_id set."""
    print("\n═══ Linking Essays ↔ Assemblies ═══")
    ok = 0
    for asm in ESSAY_ASSEMBLIES:
        payload = {"assembly_id": asm.id}
        if _patch(base_url, f"/api/essays/essays/{asm.essay_id}", payload, dry_run=dry_run):
            ok += 1
    print(f"Essay↔Assembly links: {ok}/{len(ESSAY_ASSEMBLIES)} applied.")
    return ok


def seed_question_assemblies(base_url: str, *, dry_run: bool) -> int:
    """POST question assemblies — pure metadata storage."""
    print("\n═══ Seeding Question Assemblies ═══")
    ok = 0
    for asm in QUESTION_ASSEMBLIES:
        payload = {
            "id": asm.id,
            "topic_name": asm.topic_name,
            "agents": [asdict(g) for g in asm.agents],
        }
        if _post(base_url, "/api/questions/assemblies", payload, dry_run=dry_run):
            ok += 1
    print(f"Question assemblies: {ok}/{len(QUESTION_ASSEMBLIES)} seeded.")
    return ok


_CONFIG_AUTH_HEADERS = {"X-User-Id": "seed-script", "X-User-Roles": "admin"}


def seed_themes(base_url: str, *, dry_run: bool) -> int:
    """POST themes to configuration service (requires auth headers)."""
    print("\n═══ Seeding Themes ═══")
    ok = 0
    for t in THEMES:
        payload = asdict(t)
        if _post(
            base_url,
            "/api/configuration/themes",
            payload,
            dry_run=dry_run,
            extra_headers=_CONFIG_AUTH_HEADERS,
        ):
            ok += 1
    print(f"Themes: {ok}/{len(THEMES)} seeded.")
    return ok


def seed_evaluation_datasets(base_url: str, *, dry_run: bool) -> int:
    """POST evaluation datasets to evaluation service."""
    print("\n═══ Seeding Evaluation Datasets ═══")
    ok = 0
    for ds in EVALUATION_DATASETS:
        payload = asdict(ds)
        if _post(base_url, "/api/evaluation/datasets", payload, dry_run=dry_run):
            ok += 1
    print(f"Evaluation datasets: {ok}/{len(EVALUATION_DATASETS)} seeded.")
    return ok


_UPSKILLING_AUTH_HEADERS = {"X-User-Id": "seed-script", "X-User-Roles": "professor"}


def seed_upskilling_plans(base_url: str, *, dry_run: bool) -> int:
    """POST upskilling plans to upskilling service (requires auth headers)."""
    print("\n═══ Seeding Upskilling Plans ═══")
    ok = 0
    for plan in UPSKILLING_PLANS:
        payload = asdict(plan)
        if _post(
            base_url,
            "/api/upskilling/plans",
            payload,
            dry_run=dry_run,
            extra_headers=_UPSKILLING_AUTH_HEADERS,
        ):
            ok += 1
    print(f"Upskilling plans: {ok}/{len(UPSKILLING_PLANS)} seeded.")
    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Brazilian demo data into the tutor platform.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="APIM base URL")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without sending")
    args = parser.parse_args()

    print(f"Target: {args.base_url}")
    print(f"Mode:   {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Content: {len(QUESTIONS)} questions, {len(ESSAYS)} essays, "
          f"{len(RESOURCES)} resources, {len(CASES)} cases, "
          f"{len(ESSAY_ASSEMBLIES)} essay assemblies, "
          f"{len(QUESTION_ASSEMBLIES)} question assemblies, "
          f"{len(THEMES)} themes, "
          f"{len(EVALUATION_DATASETS)} evaluation datasets, "
          f"{len(UPSKILLING_PLANS)} upskilling plans")

    totals = {}
    totals["questions"] = seed_questions(args.base_url, dry_run=args.dry_run)
    totals["essays"] = seed_essays(args.base_url, dry_run=args.dry_run)
    totals["resources"] = seed_resources(args.base_url, dry_run=args.dry_run)
    totals["cases"] = seed_cases(args.base_url, dry_run=args.dry_run)
    totals["essays_updated"] = update_essays(args.base_url, dry_run=args.dry_run)
    totals["essay_assemblies"] = seed_essay_assemblies(args.base_url, dry_run=args.dry_run)
    totals["essay_links"] = link_essays_to_assemblies(args.base_url, dry_run=args.dry_run)
    totals["question_assemblies"] = seed_question_assemblies(args.base_url, dry_run=args.dry_run)
    totals["themes"] = seed_themes(args.base_url, dry_run=args.dry_run)
    totals["evaluation_datasets"] = seed_evaluation_datasets(args.base_url, dry_run=args.dry_run)
    totals["upskilling_plans"] = seed_upskilling_plans(args.base_url, dry_run=args.dry_run)

    print("\n═══ Summary ═══")
    total_items = (len(QUESTIONS) + len(ESSAYS) + len(RESOURCES) + len(CASES)
                   + len(ESSAYS) + len(ESSAY_ASSEMBLIES) + len(ESSAY_ASSEMBLIES)
                   + len(QUESTION_ASSEMBLIES)
                   + len(THEMES) + len(EVALUATION_DATASETS) + len(UPSKILLING_PLANS))
    for k, v in totals.items():
        print(f"  {k}: {v}")
    total_ok = sum(totals.values())
    print(f"  TOTAL: {total_ok}/{total_items}")

    if total_ok < total_items:
        print("\n⚠ Some items failed. Check output above.")
        sys.exit(1)
    else:
        print("\n✓ All demo data seeded successfully!")


if __name__ == "__main__":
    main()


