import random
import pandas as pd
from datetime import datetime, timedelta


SEED = 42

# ============================================================
# CONFIGURAÇÕES DAS JORNADAS
# ============================================================

CONFIG_JORNADAS = {
    1: {  # SAC
        "6x1_6h": 0.35,
        "6x1_7h": 0.45,
        "5x2_8h": 0.20,
    },

    2: {  # Financeiro
        "6x1_6h": 0.30,
        "6x1_7h": 0.40,
        "5x2_8h": 0.30,
    },

    3: {  # Retenção
        "6x1_6h": 0.30,
        "6x1_7h": 0.50,
        "5x2_8h": 0.20,
    },

    4: {  # Suporte Técnico
        "6x1_6h": 0.30,
        "6x1_7h": 0.45,
        "5x2_8h": 0.25,
    },

    5: {  # Vendas
        "6x1_6h": 0.40,
        "6x1_7h": 0.40,
        "5x2_8h": 0.20,
    },
}


COBERTURA_DOMINGO = {
    1: 0.40,
    2: 0.25,
    3: 0.30,
    4: 0.50,
    5: 0.35,
}


COBERTURA_FERIADO = {
    1: 0.50,
    2: 0.30,
    3: 0.40,
    4: 0.50,
    5: 0.40,
}


PADROES_JORNADA = {
    "6x1_6h": {
        "dias_trabalho": 6,
        "horas": 6,
    },

    "6x1_7h": {
        "dias_trabalho": 6,
        "horas": 7,
    },

    "5x2_8h": {
        "dias_trabalho": 5,
        "horas": 8,
    },
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def escolher_tipo_jornada(operation_key):
    configuracao = CONFIG_JORNADAS[operation_key]

    tipos = list(configuracao.keys())
    probabilidades = list(configuracao.values())

    return random.choices(
        tipos,
        weights=probabilidades,
        k=1
    )[0]


def gerar_folgas_5x2():
    dias = list(range(7))

    folgas = random.sample(
        dias,
        2
    )

    return set(folgas)


def deve_ser_escalado_domingo(operation_key):
    probabilidade = COBERTURA_DOMINGO[operation_key]

    return random.random() < probabilidade


def deve_ser_escalado_feriado(operation_key):
    probabilidade = COBERTURA_FERIADO[operation_key]

    return random.random() < probabilidade


def selecionar_shift(df_shifts, horas):
    candidatos = df_shifts[
        df_shifts["shift_hours"] == horas
    ]

    if candidatos.empty:
        raise ValueError(
            f"Nenhum shift encontrado para {horas} horas."
        )

    indice = random.randrange(
        len(candidatos)
    )

    return candidatos.iloc[indice]


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def gerar_fact_schedule(
    df_agentes,
    df_equipes,
    df_shifts,
    df_skills,
    df_bridge,
    df_datas
):

    random.seed(SEED)

    registros = []

    # --------------------------------------------------------
    # 1. Agentes ativos
    # --------------------------------------------------------

    agentes = df_agentes[
        df_agentes["agent_status"] == "Ativo"
    ].copy()

    # --------------------------------------------------------
    # 2. Adiciona operação da equipe
    # --------------------------------------------------------

    agentes = agentes.merge(
        df_equipes[
            ["team_key", "operation_key"]
        ],
        on="team_key",
        how="left"
    )

    # --------------------------------------------------------
    # 3. Adiciona skill primária
    # --------------------------------------------------------

    bridge_primaria = df_bridge[
        df_bridge["is_primary"] == True
    ][
        ["agent_key", "skill_key"]
    ].copy()

    agentes = agentes.merge(
        bridge_primaria,
        on="agent_key",
        how="left"
    )

    # --------------------------------------------------------
    # 4. Validações estruturais
    # --------------------------------------------------------

    if agentes["operation_key"].isna().any():
        raise ValueError(
            "Existem agentes sem operation_key."
        )

    if agentes["skill_key"].isna().any():
        raise ValueError(
            "Existem agentes sem skill primária."
        )

    # --------------------------------------------------------
    # 5. Gera escala por agente
    # --------------------------------------------------------

    for _, agente in agentes.iterrows():

        agent_key = int(
            agente["agent_key"]
        )

        team_key = int(
            agente["team_key"]
        )

        operation_key = int(
            agente["operation_key"]
        )

        skill_key = int(
            agente["skill_key"]
        )

        hire_date = pd.Timestamp(
            agente["hire_date"]
        ).date()

        termination_date = None

        if pd.notna(
            agente["termination_date"]
        ):
            termination_date = pd.Timestamp(
                agente["termination_date"]
            ).date()

        # ----------------------------------------------------
        # Define jornada do agente
        # ----------------------------------------------------

        tipo_jornada = escolher_tipo_jornada(
            operation_key
        )

        config = PADROES_JORNADA[
            tipo_jornada
        ]

        horas = config["horas"]

        # ----------------------------------------------------
        # Define folgas
        # ----------------------------------------------------

        if tipo_jornada.startswith("6x1"):

            dia_folga = random.randint(
                0,
                6
            )

            folgas = {dia_folga}

        else:

            folgas = gerar_folgas_5x2()

        # ----------------------------------------------------
        # Define shift
        # ----------------------------------------------------

        shift = selecionar_shift(
            df_shifts,
            horas
        )

        shift_key = int(
            shift["shift_key"]
        )

        start_time = shift["start_time"]
        end_time = shift["end_time"]

        # ----------------------------------------------------
        # Percorre calendário
        # ----------------------------------------------------

        for _, data_row in df_datas.iterrows():

            data = pd.Timestamp(
                data_row["full_date"]
            ).date()

            # Antes da admissão
            if data < hire_date:
                continue

            # Depois do desligamento
            if (
                termination_date is not None
                and data > termination_date
            ):
                continue

            # Folga
            if data.weekday() in folgas:
                continue

            # Domingo
            if data.weekday() == 6:

                if not deve_ser_escalado_domingo(
                    operation_key
                ):
                    continue

            # Feriado
            if bool(
                data_row["is_holiday"]
            ):

                if not deve_ser_escalado_feriado(
                    operation_key
                ):
                    continue

            # ------------------------------------------------
            # Calcula horário
            # ------------------------------------------------

            planned_start = datetime.combine(
                data,
                start_time
            )

            planned_end = datetime.combine(
                data,
                end_time
            )

            # Jornada atravessando meia-noite
            if planned_end <= planned_start:

                planned_end += timedelta(
                    days=1
                )

            planned_minutes = int(
                (
                    planned_end - planned_start
                ).total_seconds() / 60
            )

            scheduled_hours = round(
                planned_minutes / 60,
                2
            )

            # ------------------------------------------------
            # Registro
            # ------------------------------------------------

            registros.append({

                "date_key": int(
                    data_row["date_key"]
                ),

                "agent_key": agent_key,

                "team_key": team_key,

                "shift_key": shift_key,

                "skill_key": skill_key,

                "schedule_status": "Escalado",

                "planned_start_datetime":
                    planned_start,

                "planned_end_datetime":
                    planned_end,

                "planned_minutes":
                    planned_minutes,

                "scheduled_hours":
                    scheduled_hours,

                "created_date":
                    datetime.now().date()
            })

    return pd.DataFrame(
        registros
    )