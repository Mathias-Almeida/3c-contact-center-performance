import random
from datetime import datetime, date, time, timedelta


# ============================================================
# CONFIGURAÇÃO GERAL
# ============================================================

SEED = 42
CREATED_DATE = date(2026, 1, 1)

_SEGUNDOS_DIA = 86_400


# ============================================================
# CONFIGURAÇÃO DAS JORNADAS
# ============================================================

CONFIG_JORNADAS = {
    "6x1_6h": {
        "duracao_minutos": 360,
        "pausas": [(0.25, 10), (0.50, 20), (0.75, 10)],
    },
    "6x1_7h": {
        "duracao_minutos": 420,
        "pausas": [(0.25, 10), (0.55, 60)],
    },
    "5x2_8h": {
        "duracao_minutos": 480,
        "pausas": [(0.25, 10), (0.50, 60), (0.75, 10)],
    },
}

# Mapas de consulta O(1) para identificar a jornada.
_JORNADA_POR_DURACAO = {
    cfg["duracao_minutos"]: nome for nome, cfg in CONFIG_JORNADAS.items()
}
_JORNADA_POR_NOME = (("6h", "6x1_6h"), ("7h", "6x1_7h"), ("8h", "5x2_8h"))


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
_SHRINKAGE_ITENS = tuple(CONFIG_SHRINKAGE.items())


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
_ATIVIDADES_ITENS = tuple(CONFIG_ATIVIDADES.items())

# Campo de minutos de cada tipo de atividade planejada.
_CAMPO_ATIVIDADE = {
    "Treinamento": "training_minutes",
    "Reunião": "meeting_minutes",
    "Coaching": "coaching_minutes",
    "Administrativo": "administrative_minutes",
}


# ============================================================
# IDENTIFICAÇÃO DA JORNADA
# ============================================================

def identificar_jornada(shift_name, duration_minutes=None):
    """Identifica a jornada pela duração ou pelo nome da escala."""

    if duration_minutes is not None:
        jornada = _JORNADA_POR_DURACAO.get(int(duration_minutes))
        if jornada:
            return jornada

    if shift_name:
        nome = str(shift_name).lower()
        for sufixo, jornada in _JORNADA_POR_NOME:
            if sufixo in nome:
                return jornada

    raise ValueError(
        "Não foi possível identificar a jornada: "
        f"shift_name={shift_name!r}, "
        f"duration_minutes={duration_minutes!r}"
    )


# ============================================================
# SOBREPOSIÇÃO TEMPORAL
# ============================================================

def calcular_sobreposicao(inicio_a, fim_a, inicio_b, fim_b):
    """Calcula os minutos inteiros de sobreposição entre dois períodos."""

    inicio = max(inicio_a, inicio_b)
    fim = min(fim_a, fim_b)

    if fim <= inicio:
        return 0

    return int(round((fim - inicio).total_seconds() / 60))


def possui_sobreposicao(inicio_a, fim_a, inicio_b, fim_b):
    """Verifica se dois períodos possuem interseção positiva."""

    return inicio_a < fim_b and inicio_b < fim_a


def somar_minutos_uniao(janelas, inicio_referencia, fim_referencia):
    """
    Soma a união temporal das janelas dentro do período de referência,
    evitando contar duas vezes minutos de eventos sobrepostos.
    """

    recortes = []

    for janela in janelas:
        inicio = max(janela["inicio"], inicio_referencia)
        fim = min(janela["fim"], fim_referencia)

        if fim > inicio:
            recortes.append((inicio, fim))

    if not recortes:
        return 0

    recortes.sort(key=lambda item: item[0])

    inicio_atual, fim_atual = recortes[0]
    total_segundos = 0

    for inicio, fim in recortes[1:]:
        if inicio <= fim_atual:
            fim_atual = max(fim_atual, fim)
        else:
            total_segundos += (fim_atual - inicio_atual).total_seconds()
            inicio_atual, fim_atual = inicio, fim

    total_segundos += (fim_atual - inicio_atual).total_seconds()

    return int(round(total_segundos / 60))


def encontrar_segmentos_livres(inicio, fim, janelas_ocupadas):
    """Retorna os segmentos livres de um período, descontando janelas."""

    if fim <= inicio:
        return []

    ocupadas = []

    for janela in janelas_ocupadas:
        recorte_inicio = max(inicio, janela["inicio"])
        recorte_fim = min(fim, janela["fim"])

        if recorte_fim > recorte_inicio:
            ocupadas.append((recorte_inicio, recorte_fim))

    ocupadas.sort(key=lambda item: item[0])

    segmentos = []
    cursor = inicio

    for ocupado_inicio, ocupado_fim in ocupadas:
        if ocupado_inicio > cursor:
            segmentos.append((cursor, ocupado_inicio))

        cursor = max(cursor, ocupado_fim)

        if cursor >= fim:
            break

    if cursor < fim:
        segmentos.append((cursor, fim))

    return [(a, b) for a, b in segmentos if b > a]


# ============================================================
# CONSTRUÇÃO DOS DATETIMES DOS INTERVALOS
# ============================================================

def construir_intervalo_datetime(
    schedule_start,
    schedule_end,
    interval_start_time,
    interval_end_time,
):
    """
    Identifica a ocorrência do intervalo de relógio que mais se sobrepõe
    à escala (data de início da escala ou dia seguinte).
    """

    if schedule_end <= schedule_start:
        raise ValueError(
            f"Período de escala inválido: {schedule_start} - {schedule_end}"
        )

    melhor_intervalo = None
    maior_sobreposicao_segundos = -1

    data_base = schedule_start.date()

    for deslocamento_dias in (0, 1):
        data_intervalo = data_base + timedelta(days=deslocamento_dias)

        inicio = datetime.combine(data_intervalo, interval_start_time)
        fim = datetime.combine(data_intervalo, interval_end_time)

        if fim <= inicio:
            fim += timedelta(days=1)

        sobreposicao_segundos = max(
            0,
            (min(schedule_end, fim) - max(schedule_start, inicio))
            .total_seconds(),
        )

        if sobreposicao_segundos > maior_sobreposicao_segundos:
            maior_sobreposicao_segundos = sobreposicao_segundos
            melhor_intervalo = (inicio, fim)

    return melhor_intervalo


def _preparar_intervalos(intervals):
    """
    Converte start/end de cada intervalo em segundos desde 00:00,
    uma única vez, para o pré-filtro por escala.
    """

    preparados = []

    for intervalo in intervals:
        _key, inicio, fim = intervalo

        inicio_s = inicio.hour * 3600 + inicio.minute * 60 + inicio.second
        fim_s = fim.hour * 3600 + fim.minute * 60 + fim.second

        if fim_s <= inicio_s:
            fim_s += _SEGUNDOS_DIA

        preparados.append((intervalo, inicio_s, fim_s))

    return preparados


def _intervalos_da_escala(schedule_start, schedule_end, preparados):
    """
    Devolve, na ordem original, apenas os intervalos que têm interseção
    positiva com a escala (data de início ou dia seguinte).

    Substitui o teste "intervalo a intervalo" com datetimes por
    comparações de inteiros. É um superconjunto exato de
    scheduled_minutes > 0, então o resultado final não muda.
    """

    meia_noite = datetime.combine(schedule_start.date(), time.min)
    esc_inicio = (schedule_start - meia_noite).total_seconds()
    esc_fim = (schedule_end - meia_noite).total_seconds()

    for intervalo, inicio_s, fim_s in preparados:
        for deslocamento in (0, _SEGUNDOS_DIA):
            if (
                inicio_s + deslocamento < esc_fim
                and fim_s + deslocamento > esc_inicio
            ):
                yield intervalo
                break


# ============================================================
# PAUSAS PLANEJADAS — UMA VEZ POR ESCALA
# ============================================================

def gerar_janelas_pausas(planned_start, planned_end, jornada, rng):
    """Gera as pausas planejadas para toda a escala."""

    config = CONFIG_JORNADAS[jornada]

    duracao_jornada = int(
        (planned_end - planned_start).total_seconds() / 60
    )

    limite_inicio = planned_start + timedelta(minutes=5)
    limite_fim = planned_end - timedelta(minutes=5)

    pausas = []
    ultima_fim = planned_start

    for percentual, duracao in config["pausas"]:
        centro = planned_start + timedelta(
            minutes=duracao_jornada * percentual
        )

        variacao = rng.randint(-5, 5)

        inicio = centro + timedelta(minutes=variacao - duracao / 2)
        fim = inicio + timedelta(minutes=duracao)

        if inicio < limite_inicio:
            inicio = limite_inicio
            fim = inicio + timedelta(minutes=duracao)

        if fim > limite_fim:
            fim = limite_fim
            inicio = fim - timedelta(minutes=duracao)

        if inicio < ultima_fim:
            inicio = ultima_fim + timedelta(minutes=2)
            fim = inicio + timedelta(minutes=duracao)

        if inicio < planned_start or fim > planned_end:
            continue

        if fim <= inicio:
            continue

        pausas.append({"inicio": inicio, "fim": fim, "duracao": duracao})
        ultima_fim = fim

    return pausas


# ============================================================
# ATIVIDADE PLANEJADA — UMA VEZ POR ESCALA
# ============================================================

def atividade_planejada_aleatoria(planned_start, planned_end, pausas, rng):
    """
    Sorteia no máximo uma atividade planejada por escala,
    posicionada fora das pausas planejadas.
    """

    jornada_minutos = int(
        (planned_end - planned_start).total_seconds() / 60
    )

    for atividade, config in _ATIVIDADES_ITENS:
        if rng.random() > config["probabilidade"]:
            continue

        duracao_maxima = max(0, jornada_minutos - 30)

        if duracao_maxima < 15:
            return None

        duracao = min(
            rng.randint(config["duracao_min"], config["duracao_max"]),
            duracao_maxima,
        )

        inicio_min = 15
        inicio_max = jornada_minutos - duracao - 15

        if inicio_max < inicio_min:
            continue

        for _ in range(50):
            inicio = planned_start + timedelta(
                minutes=rng.randint(inicio_min, inicio_max)
            )
            fim = inicio + timedelta(minutes=duracao)

            if not any(
                possui_sobreposicao(
                    inicio, fim, pausa["inicio"], pausa["fim"]
                )
                for pausa in pausas
            ):
                return {
                    "activity_type": atividade,
                    "inicio": inicio,
                    "fim": fim,
                    "duracao": duracao,
                }

        return None

    return None


# ============================================================
# SHRINKAGE NÃO PLANEJADO — POR INTERVALO
# ============================================================

def shrinkage_nao_planejado(
    interval_start,
    interval_end,
    janelas_ocupadas,
    rng,
):
    """
    Sorteia no máximo um evento não planejado por intervalo, dentro do
    tempo escalado e fora das janelas planejadas.
    """

    atividade_escolhida = None
    config_escolhida = None

    for atividade, config in _SHRINKAGE_ITENS:
        if rng.random() <= config["probabilidade"]:
            atividade_escolhida = atividade
            config_escolhida = config
            break

    if atividade_escolhida is None:
        return None

    duracao_min_s = config_escolhida["duracao_min"] * 60

    segmentos_validos = [
        (inicio, fim)
        for inicio, fim in encontrar_segmentos_livres(
            interval_start, interval_end, janelas_ocupadas
        )
        if (fim - inicio).total_seconds() >= duracao_min_s
    ]

    if not segmentos_validos:
        return None

    inicio_segmento, fim_segmento = rng.choice(segmentos_validos)

    minutos_livres = int(
        (fim_segmento - inicio_segmento).total_seconds() / 60
    )

    duracao = min(
        rng.randint(
            config_escolhida["duracao_min"],
            config_escolhida["duracao_max"],
        ),
        minutos_livres,
    )

    deslocamento = rng.randint(0, minutos_livres - duracao)

    inicio = inicio_segmento + timedelta(minutes=deslocamento)

    return {
        "activity_type": atividade_escolhida,
        "inicio": inicio,
        "fim": inicio + timedelta(minutes=duracao),
        "duracao": duracao,
    }


# ============================================================
# CONTEXTO OPERACIONAL DA ESCALA
# ============================================================

def criar_contexto_escala(schedule, rng):
    """Prepara as pausas e atividades uma única vez por escala."""

    (
        _schedule_key,
        _date_key,
        _agent_key,
        _team_key,
        _shift_key,
        _skill_key,
        planned_start,
        planned_end,
        shift_name,
        duration_minutes,
    ) = schedule

    jornada = identificar_jornada(shift_name, duration_minutes)

    pausas = gerar_janelas_pausas(planned_start, planned_end, jornada, rng)

    atividade_planejada = atividade_planejada_aleatoria(
        planned_start, planned_end, pausas, rng
    )

    return {
        "jornada": jornada,
        "pausas": pausas,
        "atividade_planejada": atividade_planejada,
    }


# ============================================================
# GERAÇÃO DE UM INTERVALO
# ============================================================

def gerar_intervalo(schedule, intervalo, contexto=None, rng=None):
    """
    Gera um registro para a fact_agent_interval.

    As colunas *_before_absence preservam a base anterior à
    reconciliação com fact_absence.
    """

    if rng is None:
        rng = random.Random(SEED)

    (
        schedule_key,
        _date_key,
        agent_key,
        team_key,
        _shift_key,
        skill_key,
        planned_start_datetime,
        planned_end_datetime,
        _shift_name,
        _duration_minutes,
    ) = schedule

    interval_key, interval_start_time, interval_end_time = intervalo

    if contexto is None:
        contexto = criar_contexto_escala(schedule, rng)

    interval_start, interval_end = construir_intervalo_datetime(
        planned_start_datetime,
        planned_end_datetime,
        interval_start_time,
        interval_end_time,
    )

    scheduled_start = max(planned_start_datetime, interval_start)
    scheduled_end = min(planned_end_datetime, interval_end)

    scheduled_minutes = calcular_sobreposicao(
        planned_start_datetime,
        planned_end_datetime,
        interval_start,
        interval_end,
    )

    if scheduled_minutes <= 0:
        return None

    # --------------------------------------------------------
    # Pausas planejadas
    # --------------------------------------------------------

    pausas = contexto["pausas"]

    planned_pause_minutes = sum(
        calcular_sobreposicao(
            pausa["inicio"], pausa["fim"], scheduled_start, scheduled_end
        )
        for pausa in pausas
    )

    janelas_ocupadas = list(pausas)

    # --------------------------------------------------------
    # Atividade planejada
    # --------------------------------------------------------

    minutos_atividade = {
        "training_minutes": 0,
        "meeting_minutes": 0,
        "coaching_minutes": 0,
        "administrative_minutes": 0,
    }

    atividade_planejada = contexto["atividade_planejada"]

    if atividade_planejada:
        atividade_minutos = calcular_sobreposicao(
            atividade_planejada["inicio"],
            atividade_planejada["fim"],
            scheduled_start,
            scheduled_end,
        )

        if atividade_minutos > 0:
            minutos_atividade[
                _CAMPO_ATIVIDADE[atividade_planejada["activity_type"]]
            ] = atividade_minutos

            janelas_ocupadas.append({
                "inicio": atividade_planejada["inicio"],
                "fim": atividade_planejada["fim"],
            })

    training_minutes = minutos_atividade["training_minutes"]
    meeting_minutes = minutos_atividade["meeting_minutes"]
    coaching_minutes = minutos_atividade["coaching_minutes"]
    administrative_minutes = minutos_atividade["administrative_minutes"]

    # Só as janelas que tocam este intervalo importam daqui em diante.
    # Filtrar antes não altera os resultados (as funções já recortavam),
    # mas evita listas/ordenações inúteis na maioria dos intervalos.
    janelas_relevantes = [
        j for j in janelas_ocupadas
        if j["inicio"] < scheduled_end and j["fim"] > scheduled_start
    ]

    # --------------------------------------------------------
    # Shrinkage não planejado (o RNG é consumido como antes)
    # --------------------------------------------------------

    shrinkage = shrinkage_nao_planejado(
        scheduled_start,
        scheduled_end,
        janelas_relevantes,
        rng,
    )

    unplanned_pause_minutes = 0
    technical_issue_minutes = 0

    if shrinkage:
        minutos_evento = calcular_sobreposicao(
            shrinkage["inicio"],
            shrinkage["fim"],
            scheduled_start,
            scheduled_end,
        )

        if shrinkage["activity_type"] == "Pausa Particular":
            unplanned_pause_minutes = minutos_evento
        else:
            technical_issue_minutes = minutos_evento

        janelas_relevantes.append({
            "inicio": shrinkage["inicio"],
            "fim": shrinkage["fim"],
        })

    # --------------------------------------------------------
    # Disponibilidade (união das janelas: sem dupla contagem)
    # --------------------------------------------------------

    if janelas_relevantes:
        shrinkage_minutes = min(
            scheduled_minutes,
            somar_minutos_uniao(
                janelas_relevantes, scheduled_start, scheduled_end
            ),
        )
    else:
        shrinkage_minutes = 0

    available_minutes = max(0, scheduled_minutes - shrinkage_minutes)

    if available_minutes > 0:
        productive_minutes = min(
            available_minutes,
            max(0, int(round(available_minutes * rng.uniform(0.65, 0.90)))),
        )
    else:
        productive_minutes = 0

    # --------------------------------------------------------
    # Classificação operacional
    # --------------------------------------------------------

    if planned_pause_minutes > 0:
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
    else:
        activity_type = "Atendimento"

    operational_status = (
        "Indisponível" if available_minutes <= 0 else "Trabalhando"
    )

    # Data civil do início do intervalo (essencial para turnos noturnos).
    d = interval_start
    interval_date_key = d.year * 10000 + d.month * 100 + d.day

    return {
        "date_key": interval_date_key,
        "interval_key": interval_key,
        "agent_key": agent_key,
        "team_key": team_key,
        "skill_key": skill_key,
        "schedule_key": schedule_key,

        "operational_status": operational_status,
        "activity_type": activity_type,

        "scheduled_flag": True,
        "present_flag": True,
        "available_flag": available_minutes > 0,
        "productive_flag": productive_minutes > 0,

        "scheduled_minutes": scheduled_minutes,
        "planned_pause_minutes": planned_pause_minutes,
        "unplanned_pause_minutes": unplanned_pause_minutes,
        "training_minutes": training_minutes,
        "meeting_minutes": meeting_minutes,
        "coaching_minutes": coaching_minutes,
        "administrative_minutes": administrative_minutes,
        "technical_issue_minutes": technical_issue_minutes,

        "absence_minutes": 0,

        "available_minutes": available_minutes,
        "productive_minutes": productive_minutes,

        "available_minutes_before_absence": available_minutes,
        "productive_minutes_before_absence": productive_minutes,

        "handling_seconds": 0,
        "contacts_handled": 0,
        "created_date": CREATED_DATE,
    }


# ============================================================
# GERADOR PRINCIPAL
# ============================================================

def gerar_fact_agent_interval(
    schedules,
    intervals,
    chunk_size=50_000,
):
    """
    Gera registros em lotes para a fact_agent_interval.

    Usa um RNG local e determinístico (reprodutível para a mesma SEED).
    Para cada escala, só percorre os intervalos que a atravessam.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size deve ser maior que zero.")

    rng = random.Random(SEED)
    preparados = _preparar_intervalos(intervals)  # uma vez só
    lote = []

    for schedule in schedules:
        contexto = criar_contexto_escala(schedule, rng)

        planned_start, planned_end = schedule[6], schedule[7]

        for intervalo in _intervalos_da_escala(
            planned_start, planned_end, preparados
        ):
            registro = gerar_intervalo(
                schedule=schedule,
                intervalo=intervalo,
                contexto=contexto,
                rng=rng,
            )

            if registro is None:
                continue

            lote.append(registro)

            if len(lote) >= chunk_size:
                yield lote
                lote = []

    if lote:
        yield lote