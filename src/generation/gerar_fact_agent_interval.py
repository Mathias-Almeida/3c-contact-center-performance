import random
from datetime import datetime, date, time, timedelta


# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

SEED = 42

random.seed(SEED)


# ============================================================
# CONFIGURAÇÃO DAS JORNADAS
# ============================================================
#
# As pausas são definidas como:
#
# percentual da jornada -> duração da pausa
#
# Exemplo:
#
# 6h:
# 25% -> 10 min
# 50% -> 20 min
# 75% -> 10 min
#
# 7h:
# 25% -> 10 min
# 55% -> 60 min
#
# 8h:
# 25% -> 10 min
# 50% -> 60 min
# 75% -> 10 min
#
# Observação:
# Esses valores representam uma política operacional fictícia
# adotada para o cenário do 3C.
# ============================================================

CONFIG_JORNADAS = {

    "6x1_6h": {
        "duracao_minutos": 360,
        "pausas": [
            (0.25, 10),
            (0.50, 20),
            (0.75, 10),
        ],
    },

    "6x1_7h": {
        "duracao_minutos": 420,
        "pausas": [
            (0.25, 10),
            (0.55, 60),
        ],
    },

    "5x2_8h": {
        "duracao_minutos": 480,
        "pausas": [
            (0.25, 10),
            (0.50, 60),
            (0.75, 10),
        ],
    },
}


# ============================================================
# SHRINKAGE NÃO PLANEJADO
# ============================================================

CONFIG_SHRINKAGE = {

    "Pausa Particular": {
        "probabilidade": 0.018,
        "duracao_min": 5,
        "duracao_max": 10,
    },

    "Problema Técnico": {
        "probabilidade": 0.006,
        "duracao_min": 5,
        "duracao_max": 30,
    },
}


# ============================================================
# ATIVIDADES PLANEJADAS
# ============================================================

CONFIG_ATIVIDADES = {

    "Treinamento": {
        "probabilidade": 0.0015,
        "duracao_min": 30,
        "duracao_max": 120,
    },

    "Reunião": {
        "probabilidade": 0.0010,
        "duracao_min": 30,
        "duracao_max": 60,
    },

    "Coaching": {
        "probabilidade": 0.0008,
        "duracao_min": 30,
        "duracao_max": 60,
    },

    "Administrativo": {
        "probabilidade": 0.0012,
        "duracao_min": 15,
        "duracao_max": 60,
    },
}


# ============================================================
# IDENTIFICAÇÃO DA JORNADA
# ============================================================

def identificar_jornada(
    shift_name,
    duration_minutes=None
):
    """
    Identifica a jornada operacional.

    A identificação é feita preferencialmente pela duração
    da jornada, e não pelo nome do turno.

    Isso evita dependência do padrão textual utilizado em
    dim_shift.shift_name.

    Jornadas do projeto:

        360 minutos -> 6x1_6h
        420 minutos -> 6x1_7h
        480 minutos -> 5x2_8h
    """

    if duration_minutes is not None:

        duration_minutes = int(
            duration_minutes
        )

        if duration_minutes == 360:
            return "6x1_6h"

        if duration_minutes == 420:
            return "6x1_7h"

        if duration_minutes == 480:
            return "5x2_8h"

    # --------------------------------------------------------
    # Fallback pelo nome
    # --------------------------------------------------------

    if shift_name:

        shift_name = str(
            shift_name
        ).lower()

        if "6h" in shift_name:
            return "6x1_6h"

        if "7h" in shift_name:
            return "6x1_7h"

        if "8h" in shift_name:
            return "5x2_8h"

    raise ValueError(
        "Não foi possível identificar a jornada. "
        f"shift_name={shift_name!r}, "
        f"duration_minutes={duration_minutes!r}"
    )


# ============================================================
# SOBREPOSIÇÃO ENTRE DOIS INTERVALOS DE DATETIME
# ============================================================

def calcular_sobreposicao(
    inicio_a,
    fim_a,
    inicio_b,
    fim_b
):
    """
    Retorna a quantidade de minutos de sobreposição
    entre dois intervalos de datetime.
    """

    inicio = max(
        inicio_a,
        inicio_b
    )

    fim = min(
        fim_a,
        fim_b
    )

    if fim <= inicio:
        return 0

    segundos = (
        fim - inicio
    ).total_seconds()

    return int(
        round(segundos / 60)
    )


# ============================================================
# CRIAÇÃO DAS JANELAS DE PAUSA
# ============================================================

def gerar_janelas_pausas(
    planned_start,
    planned_end,
    jornada
):

    """
    Gera as janelas de pausa planejada dentro da jornada.

    A posição da pausa é baseada em um percentual da jornada,
    com pequena variação aleatória para evitar que todos os
    agentes façam a pausa exatamente no mesmo minuto.

    As pausas são ordenadas e ajustadas para não se sobrepor.
    """

    config = CONFIG_JORNADAS[jornada]

    duracao_jornada = (
        planned_end - planned_start
    ).total_seconds() / 60

    pausas = []

    ultima_fim = planned_start

    for percentual, duracao in config["pausas"]:

        centro = (
            planned_start
            + timedelta(
                minutes=duracao_jornada * percentual
            )
        )

        variacao = random.randint(
            -5,
            5
        )

        inicio = (
            centro
            + timedelta(
                minutes=variacao
            )
            - timedelta(
                minutes=duracao / 2
            )
        )

        fim = (
            inicio
            + timedelta(
                minutes=duracao
            )
        )

        # ----------------------------------------------------
        # Limites da jornada
        # ----------------------------------------------------

        limite_inicio = (
            planned_start
            + timedelta(minutes=5)
        )

        limite_fim = (
            planned_end
            - timedelta(minutes=5)
        )

        if inicio < limite_inicio:
            inicio = limite_inicio
            fim = (
                inicio
                + timedelta(minutes=duracao)
            )

        if fim > limite_fim:
            fim = limite_fim
            inicio = (
                fim
                - timedelta(minutes=duracao)
            )

        # ----------------------------------------------------
        # Evitar sobreposição
        # ----------------------------------------------------

        if inicio < ultima_fim:

            inicio = (
                ultima_fim
                + timedelta(minutes=2)
            )

            fim = (
                inicio
                + timedelta(minutes=duracao)
            )

        # Se não houver espaço suficiente, ignora a pausa.
        if fim > planned_end:

            continue

        pausas.append(
            {
                "inicio": inicio,
                "fim": fim,
                "duracao": duracao,
            }
        )

        ultima_fim = fim

    return pausas


# ============================================================
# ATIVIDADE PLANEJADA
# ============================================================

def atividade_planejada_aleatoria(
    planned_start,
    planned_end
):

    """
    Determina se o agente terá uma atividade planejada.

    A atividade é criada apenas se a probabilidade aleatória
    for atingida.
    """

    for atividade, config in CONFIG_ATIVIDADES.items():

        if random.random() <= config["probabilidade"]:

            duracao = random.randint(
                config["duracao_min"],
                config["duracao_max"]
            )

            jornada_minutos = int(
                (
                    planned_end - planned_start
                ).total_seconds() / 60
            )

            # Mantém a atividade dentro da jornada.
            duracao = min(
                duracao,
                max(15, jornada_minutos - 30)
            )

            inicio_min = 15
            inicio_max = max(
                inicio_min,
                jornada_minutos - duracao - 15
            )

            inicio_offset = random.randint(
                inicio_min,
                inicio_max
            )

            inicio = (
                planned_start
                + timedelta(
                    minutes=inicio_offset
                )
            )

            fim = (
                inicio
                + timedelta(
                    minutes=duracao
                )
            )

            return {
                "activity_type": atividade,
                "inicio": inicio,
                "fim": fim,
                "duracao": duracao,
            }

    return None


# ============================================================
# SHRINKAGE NÃO PLANEJADO
# ============================================================

def shrinkage_nao_planejado(
    interval_start,
    interval_end
):

    """
    Determina se ocorre uma indisponibilidade não planejada
    dentro do intervalo.
    """

    for atividade, config in CONFIG_SHRINKAGE.items():

        if random.random() <= config["probabilidade"]:

            duracao = random.randint(
                config["duracao_min"],
                config["duracao_max"]
            )

            duracao_intervalo = int(
                (
                    interval_end - interval_start
                ).total_seconds() / 60
            )

            duracao = min(
                duracao,
                duracao_intervalo
            )

            if duracao <= 0:
                return None

            if duracao >= duracao_intervalo:

                inicio = interval_start

            else:

                inicio_max = (
                    duracao_intervalo
                    - duracao
                )

                deslocamento = random.randint(
                    0,
                    inicio_max
                )

                inicio = (
                    interval_start
                    + timedelta(
                        minutes=deslocamento
                    )
                )

            fim = (
                inicio
                + timedelta(
                    minutes=duracao
                )
            )

            return {
                "activity_type": atividade,
                "inicio": inicio,
                "fim": fim,
                "duracao": duracao,
            }

    return None


# ============================================================
# IDENTIFICAÇÃO DA DATA DO INTERVALO
# ============================================================

def construir_intervalo_datetime(
    schedule_start,
    schedule_end,
    interval_start_time,
    interval_end_time
):

    """
    Constrói os datetimes reais de um intervalo de 30 minutos.

    Para jornadas que atravessam meia-noite, os intervalos
    posteriores à meia-noite são posicionados no dia seguinte.
    """

    data_inicio = schedule_start.date()

    interval_start = datetime.combine(
        data_inicio,
        interval_start_time
    )

    interval_end = datetime.combine(
        data_inicio,
        interval_end_time
    )

    # Intervalo que atravessa meia-noite.
    if interval_end <= interval_start:

        interval_end += timedelta(
            days=1
        )

    # --------------------------------------------------------
    # Jornada que atravessa meia-noite
    # --------------------------------------------------------

    if schedule_end.date() > schedule_start.date():

        # Intervalos cujo horário é anterior ao início da
        # jornada pertencem ao dia seguinte.
        if interval_start_time < schedule_start.time():

            interval_start += timedelta(
                days=1
            )

            interval_end += timedelta(
                days=1
            )

    return (
        interval_start,
        interval_end
    )


# ============================================================
# GERAÇÃO DE UM INTERVALO
# ============================================================

def gerar_intervalo(
    schedule,
    intervalo
):

    """
    Gera uma linha da fact_agent_interval.

    Grain:

        1 agente
        1 data
        1 intervalo de 30 minutos
    """

    (
        schedule_key,
        date_key,
        agent_key,
        team_key,
        shift_key,
        skill_key,
        planned_start_datetime,
        planned_end_datetime,
        shift_name,
        duration_minutes
    ) = schedule


    (
        interval_key,
        interval_start_time,
        interval_end_time
    ) = intervalo

    # ========================================================
    # JORNADA
    # ========================================================

    jornada = identificar_jornada(
        shift_name,
        duration_minutes
    )

    # ========================================================
    # DATETIME DO INTERVALO
    # ========================================================

    interval_start, interval_end = (
        construir_intervalo_datetime(
            planned_start_datetime,
            planned_end_datetime,
            interval_start_time,
            interval_end_time
        )
    )

    # ========================================================
    # MINUTOS ESCALADOS
    # ========================================================

    scheduled_minutes = calcular_sobreposicao(
        planned_start_datetime,
        planned_end_datetime,
        interval_start,
        interval_end
    )

    # Intervalo fora da jornada.
    if scheduled_minutes <= 0:

        return None

    # ========================================================
    # PAUSAS PLANEJADAS
    # ========================================================

    pausas = gerar_janelas_pausas(
        planned_start_datetime,
        planned_end_datetime,
        jornada
    )

    planned_pause_minutes = 0

    for pausa in pausas:

        planned_pause_minutes += (
            calcular_sobreposicao(
                pausa["inicio"],
                pausa["fim"],
                interval_start,
                interval_end
            )
        )

    # ========================================================
    # ATIVIDADE PLANEJADA
    # ========================================================

    atividade_planejada = (
        atividade_planejada_aleatoria(
            planned_start_datetime,
            planned_end_datetime
        )
    )

    training_minutes = 0
    meeting_minutes = 0
    coaching_minutes = 0
    administrative_minutes = 0

    atividade_planejada_minutes = 0

    if atividade_planejada:

        atividade_planejada_minutes = (
            calcular_sobreposicao(
                atividade_planejada["inicio"],
                atividade_planejada["fim"],
                interval_start,
                interval_end
            )
        )

        if atividade_planejada["activity_type"] == "Treinamento":

            training_minutes = (
                atividade_planejada_minutes
            )

        elif atividade_planejada["activity_type"] == "Reunião":

            meeting_minutes = (
                atividade_planejada_minutes
            )

        elif atividade_planejada["activity_type"] == "Coaching":

            coaching_minutes = (
                atividade_planejada_minutes
            )

        elif atividade_planejada["activity_type"] == "Administrativo":

            administrative_minutes = (
                atividade_planejada_minutes
            )

    # ========================================================
    # SHRINKAGE NÃO PLANEJADO
    # ========================================================

    shrinkage = shrinkage_nao_planejado(
        interval_start,
        interval_end
    )

    unplanned_pause_minutes = 0
    technical_issue_minutes = 0

    if shrinkage:

        shrinkage_minutes = calcular_sobreposicao(
            shrinkage["inicio"],
            shrinkage["fim"],
            interval_start,
            interval_end
        )

        if shrinkage["activity_type"] == "Pausa Particular":

            unplanned_pause_minutes = (
                shrinkage_minutes
            )

        elif shrinkage["activity_type"] == "Problema Técnico":

            technical_issue_minutes = (
                shrinkage_minutes
            )

    # ========================================================
    # SHRINKAGE TOTAL
    # ========================================================

    shrinkage_minutes = (
        planned_pause_minutes
        + unplanned_pause_minutes
        + training_minutes
        + meeting_minutes
        + coaching_minutes
        + administrative_minutes
        + technical_issue_minutes
    )

    # ========================================================
    # LIMITAÇÃO DO SHRINKAGE
    # ========================================================

    shrinkage_minutes = min(
        shrinkage_minutes,
        scheduled_minutes
    )

    # ========================================================
    # DISPONIBILIDADE
    # ========================================================

    available_minutes = max(
        0,
        scheduled_minutes
        - shrinkage_minutes
    )

    # ========================================================
    # PRODUTIVIDADE
    # ========================================================
    #
    # Neste estágio ainda não estamos alocando a demanda
    # diretamente aos agentes.
    #
    # Portanto a produtividade representa apenas uma fração
    # do tempo disponível.
    #
    # A produção real será reconciliada posteriormente com
    # fact_demand.
    # ========================================================

    if available_minutes > 0:

        produtividade = random.uniform(
            0.65,
            0.90
        )

        productive_minutes = int(
            round(
                available_minutes
                * produtividade
            )
        )

    else:

        productive_minutes = 0

    # ========================================================
    # ATIVIDADE DOMINANTE
    # ========================================================

    activity_type = "Atendimento"

    if scheduled_minutes <= 0:

        activity_type = "Folga"

    elif planned_pause_minutes > 0:

        activity_type = "Pausa Planejada"

    elif training_minutes > 0:

        activity_type = "Treinamento"

    elif meeting_minutes > 0:

        activity_type = "Reunião"

    elif coaching_minutes > 0:

        activity_type = "Coaching"

    elif administrative_minutes > 0:

        activity_type = "Administrativo"

    elif unplanned_pause_minutes > 0:

        activity_type = "Pausa Particular"

    elif technical_issue_minutes > 0:

        activity_type = "Problema Técnico"

    # ========================================================
    # STATUS OPERACIONAL
    # ========================================================

    if scheduled_minutes <= 0:

        operational_status = "Folga"

    elif available_minutes <= 0:

        operational_status = "Indisponível"

    else:

        operational_status = "Trabalhando"

    # ========================================================
    # FLAGS
    # ========================================================

    scheduled_flag = True

    present_flag = True

    available_flag = (
        available_minutes > 0
    )

    productive_flag = (
        productive_minutes > 0
    )

    # ========================================================
    # PRODUÇÃO
    # ========================================================
    #
    # Ainda não vinculamos os contatos da demanda aos agentes.
    #
    # Portanto:
    #
    # handling_seconds = 0
    # contacts_handled = 0
    #
    # Essa etapa será tratada posteriormente.
    # ========================================================

    handling_seconds = 0

    contacts_handled = 0

    # ========================================================
    # DATA DE CRIAÇÃO
    # ========================================================

    created_date = date(2026, 1, 1)

    # ========================================================
    # RESULTADO
    # ========================================================

    return {

        "date_key": date_key,

        "interval_key": interval_key,

        "agent_key": agent_key,

        "team_key": team_key,

        "skill_key": skill_key,

        "schedule_key": schedule_key,

        "operational_status": operational_status,

        "activity_type": activity_type,

        "scheduled_flag": scheduled_flag,

        "present_flag": present_flag,

        "available_flag": available_flag,

        "productive_flag": productive_flag,

        "scheduled_minutes": scheduled_minutes,

        "planned_pause_minutes": planned_pause_minutes,

        "unplanned_pause_minutes": unplanned_pause_minutes,

        "training_minutes": training_minutes,

        "meeting_minutes": meeting_minutes,

        "coaching_minutes": coaching_minutes,

        "administrative_minutes": administrative_minutes,

        "technical_issue_minutes": technical_issue_minutes,

        "available_minutes": available_minutes,

        "productive_minutes": productive_minutes,

        "handling_seconds": handling_seconds,

        "contacts_handled": contacts_handled,

        "created_date": created_date,
    }


# ============================================================
# GERADOR PRINCIPAL
# ============================================================

def gerar_fact_agent_interval(
    schedules,
    intervals,
    chunk_size=50_000
):

    """
    Gera a fact_agent_interval em lotes.

    Não mantém todos os registros em memória.

    Parameters
    ----------
    schedules:
        Lista de escalas provenientes da fact_schedule.

    intervals:
        Lista de intervalos provenientes da dim_interval.

    chunk_size:
        Quantidade máxima de registros por lote.
    """

    lote = []

    total_processado = 0

    for schedule in schedules:

        for intervalo in intervals:

            registro = gerar_intervalo(
                schedule,
                intervalo
            )

            if registro is None:

                continue

            lote.append(
                registro
            )

            total_processado += 1

            if len(lote) >= chunk_size:

                yield lote

                lote = []

    # ========================================================
    # ÚLTIMO LOTE
    # ========================================================

    if lote:

        yield lote