import random
from datetime import date, timedelta

import pandas as pd


# ============================================================
# CONFIGURAÇÕES
# ============================================================

SEED = 42
TOTAL_AGENTES = 5000

DATA_INICIO = date(2026, 1, 1)
DATA_FIM = date(2026, 12, 31)

# Garante que a geração seja reproduzível
random.seed(SEED)


# ============================================================
# LISTAS DE NOMES
# ============================================================

PRIMEIROS_NOMES = [
    "Ana", "André", "Beatriz", "Bruno", "Camila",
    "Carlos", "Daniel", "Daniela", "Diego", "Eduardo",
    "Elaine", "Felipe", "Fernanda", "Gabriel", "Gustavo",
    "Helena", "Igor", "Isabela", "João", "Júlia",
    "Juliana", "Larissa", "Laura", "Leonardo", "Lucas",
    "Luana", "Marcelo", "Mariana", "Marcos", "Mateus",
    "Mayara", "Natália", "Nicolas", "Paulo", "Pedro",
    "Rafael", "Raquel", "Renata", "Ricardo", "Roberta",
    "Rodrigo", "Samuel", "Sara", "Sérgio", "Thiago",
    "Vanessa", "Victor", "Vinícius", "Vitória", "Yasmin"
]


SOBRENOMES = [
    "Almeida", "Alves", "Barbosa", "Barros", "Carvalho",
    "Castro", "Costa", "Dias", "Duarte", "Fernandes",
    "Ferreira", "Freitas", "Gomes", "Gonçalves", "Lima",
    "Lopes", "Martins", "Mendes", "Monteiro", "Moraes",
    "Moreira", "Nascimento", "Nogueira", "Oliveira", "Pereira",
    "Ramos", "Reis", "Ribeiro", "Rocha", "Rodrigues",
    "Sampaio", "Santos", "Silva", "Soares", "Souza",
    "Teixeira", "Torres", "Vieira", "Xavier"
]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def gerar_data_admissao():
    """
    Gera uma data de admissão entre 2022 e 2026.

    A distribuição favorece admissões mais recentes,
    simulando uma operação em crescimento.
    """

    inicio = date(2022, 1, 1)
    fim = DATA_FIM

    dias_total = (fim - inicio).days

    while True:

        deslocamento = random.randint(0, dias_total)

        data = inicio + timedelta(days=deslocamento)

        peso = {
            2022: 0.50,
            2023: 0.65,
            2024: 0.80,
            2025: 1.00,
            2026: 1.20
        }[data.year]

        if random.random() <= peso / 1.20:
            return data


def gerar_status():
    """
    Define o status cadastral do agente.

    Aproximadamente:
    - 92% Ativo
    - 3% Afastado
    - 5% Desligado
    """

    sorteio = random.random()

    if sorteio < 0.92:
        return "Ativo"

    if sorteio < 0.95:
        return "Afastado"

    return "Desligado"


def gerar_tipo_vinculo():
    """
    Define o tipo de vínculo empregatício.

    Aproximadamente:
    - 90% CLT
    - 8% Temporário
    - 2% Aprendiz
    """

    sorteio = random.random()

    if sorteio < 0.90:
        return "CLT"

    if sorteio < 0.98:
        return "Temporário"

    return "Aprendiz"


def gerar_data_desligamento(data_admissao):
    """
    Gera uma data de desligamento entre a data
    de admissão e o final de 2026.
    """

    if data_admissao >= DATA_FIM:
        return None

    dias_disponiveis = (DATA_FIM - data_admissao).days

    if dias_disponiveis <= 0:
        return None

    deslocamento = random.randint(1, dias_disponiveis)

    return data_admissao + timedelta(days=deslocamento)


# ============================================================
# OBTENÇÃO DAS EQUIPES
# ============================================================

def obter_equipes():
    """
    Retorna as 220 equipes disponíveis.

    Atualmente utilizamos as chaves geradas no PostgreSQL.

    As equipes foram criadas sequencialmente:
    TEAM001 até TEAM220.

    Portanto, nesta etapa:
    team_key = 1 até 220.
    """

    return list(range(1, 221))


# ============================================================
# GERAÇÃO DOS AGENTES
# ============================================================

def gerar_agentes():
    """
    Gera os 5.000 agentes da 3C.

    Retorna um DataFrame do Pandas contendo:

    - agent_code
    - agent_name
    - agent_email
    - team_key
    - hire_date
    - termination_date
    - agent_status
    - employment_type
    - is_active
    - created_date
    """

    equipes = obter_equipes()

    agentes = []

    for numero in range(1, TOTAL_AGENTES + 1):

        # ----------------------------------------------------
        # Código do agente
        # ----------------------------------------------------

        agent_code = f"AGT{numero:05d}"


        # ----------------------------------------------------
        # Nome
        # ----------------------------------------------------

        primeiro_nome = random.choice(PRIMEIROS_NOMES)

        sobrenome = random.choice(SOBRENOMES)

        nome = f"{primeiro_nome} {sobrenome}"


        # ----------------------------------------------------
        # E-mail corporativo
        # ----------------------------------------------------

        agent_email = (
            f"{primeiro_nome.lower()}."
            f"{sobrenome.lower()}."
            f"{numero:05d}"
            f"@3ccontactcenter.com.br"
        )


        # ----------------------------------------------------
        # Distribuição entre equipes
        # ----------------------------------------------------

        team_key = equipes[
            (numero - 1) % len(equipes)
        ]


        # ----------------------------------------------------
        # Data de admissão
        # ----------------------------------------------------

        hire_date = gerar_data_admissao()


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        agent_status = gerar_status()


        # ----------------------------------------------------
        # Tipo de vínculo
        # ----------------------------------------------------

        employment_type = gerar_tipo_vinculo()


        # ----------------------------------------------------
        # Data de desligamento
        # ----------------------------------------------------

        termination_date = None

        if agent_status == "Desligado":

            termination_date = gerar_data_desligamento(
                hire_date
            )


        # ----------------------------------------------------
        # Registro do agente
        # ----------------------------------------------------

        agentes.append(
            {
                "agent_code": agent_code,
                "agent_name": nome,
                "agent_email": agent_email,
                "team_key": team_key,
                "hire_date": hire_date,
                "termination_date": termination_date,
                "agent_status": agent_status,
                "employment_type": employment_type,
                "is_active": agent_status != "Desligado",
                "created_date": date(2026, 1, 1),
            }
        )


    # --------------------------------------------------------
    # Converte para DataFrame
    # --------------------------------------------------------

    return pd.DataFrame(agentes)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    df = gerar_agentes()

    print("\n==========================================")
    print("GERAÇÃO DA DIM_AGENT")
    print("==========================================")

    print(f"\nTotal de agentes: {len(df)}")


    # --------------------------------------------------------
    # Primeiros registros
    # --------------------------------------------------------

    print("\nPrimeiros registros:")

    print(
        df.head(10).to_string(index=False)
    )


    # --------------------------------------------------------
    # Distribuição por status
    # --------------------------------------------------------

    print("\nDistribuição por status:")

    print(
        df["agent_status"].value_counts()
    )


    # --------------------------------------------------------
    # Distribuição por vínculo
    # --------------------------------------------------------

    print("\nDistribuição por vínculo:")

    print(
        df["employment_type"].value_counts()
    )


    # --------------------------------------------------------
    # Distribuição por equipe
    # --------------------------------------------------------

    print("\nDistribuição por equipe:")

    print(
        df["team_key"]
        .value_counts()
        .describe()
    )


    # --------------------------------------------------------
    # Datas de admissão
    # --------------------------------------------------------

    print("\nDatas de admissão:")

    print(
        df["hire_date"]
        .apply(lambda x: x.year)
        .value_counts()
        .sort_index()
    )


    # --------------------------------------------------------
    # Agentes desligados
    # --------------------------------------------------------

    print("\nAgentes desligados com data de desligamento:")

    print(
        df.loc[
            df["agent_status"] == "Desligado",
            [
                "agent_code",
                "hire_date",
                "termination_date"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


    # --------------------------------------------------------
    # Finalização
    # --------------------------------------------------------

    print("\n==========================================")
    print("GERAÇÃO CONCLUÍDA")
    print("==========================================")
