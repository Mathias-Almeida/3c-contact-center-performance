
import random
from datetime import date, datetime, time, timedelta

SEED = 42
DATA_REFERENCIA = date(2026, 1, 1)

# Probabilidades ilustrativas para o cenário sintético.
# São parâmetros de simulação, não estatísticas reais.
CONFIG_AUSENCIAS = {
    "ABS001": {
        "probabilidade": 0.012,
        "duracao": (60, 480),
    },  # Falta injustificada
    "ABS002": {
        "probabilidade": 0.025,
        "duracao": (60, 480),
    },  # Atestado médico
    "ABS004": {
        "probabilidade": 0.002,
        "duracao": (120, 480),
    },  # Licença
    "ABS008": {
        "probabilidade": 0.001,
        "duracao": (240, 480),
    },  # Afastamento
    "ABS010": {
        "probabilidade": 0.001,
        "duracao": (60, 480),
    },  # Suspensão
}


def gerar_fact_absence(
    schedules,
    absence_types,
    chunk_size=5000,
):
    """
    Gera ocorrências sintéticas de ausência.

    schedules:
        Tuplas contendo:
        schedule_key, date_key, agent_key,
        planned_start_datetime, planned_end_datetime,
        duration_minutes.

    absence_types:
        Dicionário no formato:
        {absence_type_code: absence_type_key}

    Retorna lotes de dicionários prontos para inserção.
    """
    random.seed(SEED)

    tipos_disponiveis = {
        codigo: absence_types[codigo]
        for codigo in CONFIG_AUSENCIAS
        if codigo in absence_types
    }

    ausencias = []
    agentes_com_ocorrencia = set()

    for schedule in schedules:
        (
            schedule_key,
            date_key,
            agent_key,
            planned_start,
            planned_end,
            planned_minutes,
        ) = schedule

        if random.random() >= sum(
            CONFIG_AUSENCIAS[codigo]["probabilidade"]
            for codigo in tipos_disponiveis
        ):
            continue

        # Seleciona um tipo proporcional às probabilidades configuradas.
        codigo_tipo = random.choices(
            list(tipos_disponiveis.keys()),
            weights=[
                CONFIG_AUSENCIAS[codigo]["probabilidade"]
                for codigo in tipos_disponiveis
            ],
            k=1,
        )[0]

        config = CONFIG_AUSENCIAS[codigo_tipo]
        absence_type_key = tipos_disponiveis[codigo_tipo]

        # Limita a ocorrência ao tempo efetivamente escalado.
        max_minutes = min(int(planned_minutes), 480)
        min_minutes = min(config["duracao"][0], max_minutes)

        if max_minutes <= 0:
            continue

        duration = random.randint(
            min_minutes,
            max(max_minutes, min(config["duracao"][1], max_minutes)),
        )

        latest_start = planned_end - timedelta(minutes=duration)
        if latest_start < planned_start:
            absence_start = planned_start
            absence_end = planned_end
            duration = int(
                (absence_end - absence_start).total_seconds() / 60
            )
        else:
            total_seconds = int(
                (latest_start - planned_start).total_seconds()
            )
            offset_seconds = (
                random.randint(0, total_seconds // 60) * 60
                if total_seconds >= 60
                else 0
            )
            absence_start = planned_start + timedelta(
                seconds=offset_seconds
            )
            absence_end = absence_start + timedelta(minutes=duration)

        if duration <= 0:
            continue

        ausencias.append({
            "date_key": date_key,
            "agent_key": agent_key,
            "absence_type_key": absence_type_key,
            "schedule_key": schedule_key,
            "absence_start_datetime": absence_start,
            "absence_end_datetime": absence_end,
            "absence_minutes": duration,
            "created_date": DATA_REFERENCIA,
        })

        if len(ausencias) >= chunk_size:
            yield ausencias
            ausencias = []

    if ausencias:
        yield ausencias
