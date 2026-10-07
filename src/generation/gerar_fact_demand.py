import random
import math
import pandas as pd


SEED = 42


# ============================================================
# CONFIGURAÇÕES DAS SKILLS
# ============================================================

CONFIG_SKILLS = {

    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    1: {  # V001 - SAC Voice
        "volume_base": 45,
        "aht_base": 360,
        "sla_target": 0.80,
    },

    2: {  # V002 - Financeiro Voice
        "volume_base": 30,
        "aht_base": 420,
        "sla_target": 0.80,
    },

    3: {  # V003 - Retenção Voice
        "volume_base": 22,
        "aht_base": 480,
        "sla_target": 0.80,
    },

    4: {  # V004 - Suporte Técnico Voice
        "volume_base": 28,
        "aht_base": 540,
        "sla_target": 0.80,
    },

    5: {  # V005 - Vendas Voice
        "volume_base": 24,
        "aht_base": 390,
        "sla_target": 0.80,
    },

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    6: {  # C001 - SAC Chat
        "volume_base": 24,
        "aht_base": 600,
        "sla_target": 0.80,
    },

    7: {  # C002 - Suporte Chat
        "volume_base": 18,
        "aht_base": 720,
        "sla_target": 0.80,
    },

    8: {  # C003 - Vendas Chat
        "volume_base": 16,
        "aht_base": 540,
        "sla_target": 0.80,
    },

    # --------------------------------------------------------
    # WHATSAPP
    # --------------------------------------------------------

    9: {  # W001 - SAC WhatsApp
        "volume_base": 28,
        "aht_base": 480,
        "sla_target": 0.80,
    },

    10: {  # W002 - Financeiro WhatsApp
        "volume_base": 20,
        "aht_base": 540,
        "sla_target": 0.80,
    },

    11: {  # W003 - Suporte WhatsApp
        "volume_base": 18,
        "aht_base": 660,
        "sla_target": 0.80,
    },

    # --------------------------------------------------------
    # E-MAIL / BACKOFFICE
    # --------------------------------------------------------

    12: {  # E001 - E-mail / Backoffice
        "volume_base": 20,
        "aht_base": 900,
        "sla_target": 0.90,
    },
}


# ============================================================
# FUNÇÕES DE SAZONALIDADE
# ============================================================

def fator_intraday(hora):

    """
    Representa a variação da demanda ao longo do dia.
    """

    # Madrugada
    if hora < 6:
        return 0.20

    # Início da operação
    if hora < 8:
        return 0.55

    # Manhã
    if hora < 10:
        return 0.90

    # Pico da manhã
    if hora < 12:
        return 1.15

    # Horário de almoço
    if hora < 14:
        return 0.95

    # Pico da tarde
    if hora < 17:
        return 1.20

    # Final da tarde
    if hora < 19:
        return 1.05

    # Noite
    if hora < 22:
        return 0.65

    # Madrugada
    return 0.30


def fator_dia_semana(dia_semana):

    """
    Segunda = 0
    Domingo = 6
    """

    fatores = {
        0: 1.05,  # segunda
        1: 1.00,  # terça
        2: 1.00,  # quarta
        3: 1.02,  # quinta
        4: 1.05,  # sexta
        5: 0.75,  # sábado
        6: 0.45,  # domingo
    }

    return fatores[dia_semana]


def fator_mes(mes):

    fatores = {
        1: 0.95,
        2: 0.95,
        3: 1.00,
        4: 1.00,
        5: 1.02,
        6: 1.00,
        7: 0.98,
        8: 1.00,
        9: 1.02,
        10: 1.05,
        11: 1.10,
        12: 1.20,
    }

    return fatores[mes]


def fator_feriado(is_holiday):

    if is_holiday:
        return 0.60

    return 1.00


# ============================================================
# GERAÇÃO DE VOLUME
# ============================================================

def gerar_volume(
    volume_base,
    fator_intraday_value,
    fator_semana,
    fator_mes_value,
    fator_feriado_value
):

    expectativa = (
        volume_base
        * fator_intraday_value
        * fator_semana
        * fator_mes_value
        * fator_feriado_value
    )

    # Pequena variação aleatória
    ruido = random.uniform(
        0.85,
        1.15
    )

    expectativa *= ruido

    # Distribuição de Poisson aproximada
    if expectativa <= 0:
        return 0

    volume = random.gauss(
        expectativa,
        math.sqrt(expectativa)
    )

    return max(
        0,
        int(round(volume))
    )


# ============================================================
# GERAÇÃO DE AHT
# ============================================================

def gerar_aht(aht_base):

    ruido = random.gauss(
        1.0,
        0.08
    )

    aht = aht_base * ruido

    return max(
        60,
        int(round(aht))
    )


# ============================================================
# GERAÇÃO DE ABANDONO / ATENDIMENTO
# ============================================================

def gerar_atendimento(volume_offered):

    if volume_offered == 0:
        return 0, 0

    # Abandono inicial.
    # Posteriormente poderemos substituir essa lógica
    # por uma relação com capacidade real.
    taxa_abandono = random.uniform(
        0.02,
        0.08
    )

    volume_abandoned = int(
        round(
            volume_offered
            * taxa_abandono
        )
    )

    volume_answered = (
        volume_offered
        - volume_abandoned
    )

    return (
        volume_answered,
        volume_abandoned
    )


# ============================================================
# SERVICE LEVEL
# ============================================================

def gerar_service_level(
    sla_target,
    volume_answered,
    volume_offered
):

    if volume_offered == 0:
        return 0.0

    # Variação em torno da meta
    variacao = random.gauss(
        0,
        0.07
    )

    service_level = (
        sla_target
        + variacao
    )

    return max(
        0.0,
        min(
            1.0,
            service_level
        )
    )


# ============================================================
# ASA
# ============================================================

def gerar_asa(service_level):

    """
    Quanto menor o SLA, maior tende a ser a espera.
    """

    if service_level >= 0.90:
        base = 20

    elif service_level >= 0.80:
        base = 35

    elif service_level >= 0.70:
        base = 55

    else:
        base = 90

    ruido = random.gauss(
        1.0,
        0.20
    )

    asa = base * ruido

    return max(
        5,
        int(round(asa))
    )


# ============================================================
# FUNÇÃO PRINCIPAL
# ============================================================

def gerar_fact_demand(
    df_datas,
    df_intervals,
    df_skills
):

    random.seed(SEED)

    registros = []

    # --------------------------------------------------------
    # Percorre datas
    # --------------------------------------------------------

    for data_row in df_datas.itertuples(
        index=False
    ):

        data = pd.Timestamp(
            data_row.full_date
        )

        # ----------------------------------------------------
        # Percorre intervalos
        # ----------------------------------------------------

        for intervalo in df_intervals.itertuples(
            index=False
        ):

            hora = intervalo.start_time.hour

            fator_intraday_value = (
                fator_intraday(hora)
            )

            # ------------------------------------------------
            # Percorre skills
            # ------------------------------------------------

            for skill in df_skills.itertuples(
                index=False
            ):

                skill_key = int(
                    skill.skill_key
                )

                config = CONFIG_SKILLS[
                    skill_key
                ]

                # --------------------------------------------
                # Fatores
                # --------------------------------------------

                fator_semana = (
                    fator_dia_semana(
                        data.weekday()
                    )
                )

                fator_mes_value = (
                    fator_mes(
                        data.month
                    )
                )

                fator_feriado_value = (
                    fator_feriado(
                        bool(data_row.is_holiday)
                    )
                )

                # --------------------------------------------
                # Volume
                # --------------------------------------------

                volume_offered = gerar_volume(

                    config["volume_base"],

                    fator_intraday_value,

                    fator_semana,

                    fator_mes_value,

                    fator_feriado_value
                )

                # --------------------------------------------
                # AHT
                # --------------------------------------------

                aht_seconds = gerar_aht(
                    config["aht_base"]
                )

                # --------------------------------------------
                # Atendimento
                # --------------------------------------------

                (
                    volume_answered,
                    volume_abandoned
                ) = gerar_atendimento(
                    volume_offered
                )

                # --------------------------------------------
                # Workload
                # --------------------------------------------

                workload_seconds = (
                    volume_answered
                    * aht_seconds
                )

                # --------------------------------------------
                # SLA
                # --------------------------------------------

                service_level = (
                    gerar_service_level(
                        config["sla_target"],
                        volume_answered,
                        volume_offered
                    )
                )

                # --------------------------------------------
                # ASA
                # --------------------------------------------

                asa_seconds = gerar_asa(
                    service_level
                )

                # --------------------------------------------
                # Registro
                # --------------------------------------------

                registros.append({

                    "date_key":
                        int(data_row.date_key),

                    "interval_key":
                        int(intervalo.interval_key),

                    "skill_key":
                        skill_key,

                    "volume_offered":
                        volume_offered,

                    "volume_answered":
                        volume_answered,

                    "volume_abandoned":
                        volume_abandoned,

                    "aht_seconds":
                        aht_seconds,

                    "workload_seconds":
                        workload_seconds,

                    "asa_seconds":
                        asa_seconds,

                    "sla_target":
                        config["sla_target"],

                    "service_level":
                        round(
                            service_level,
                            4
                        ),

                    "created_date":
                        pd.Timestamp(
                            "2026-01-01"
                        ).date()
                })

    return pd.DataFrame(
        registros
    )