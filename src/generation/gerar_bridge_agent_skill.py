import random

import pandas as pd


SEED = 42

random.seed(SEED)


SKILLS_POR_OPERACAO = {
    1: {
        "principal": [1],
        "secundarias": [6, 9, 12],
    },
    2: {
        "principal": [2],
        "secundarias": [10],
    },
    3: {
        "principal": [3],
        "secundarias": [],
    },
    4: {
        "principal": [4],
        "secundarias": [7, 11],
    },
    5: {
        "principal": [5],
        "secundarias": [8],
    },
}


NIVEIS = [
    "Iniciante",
    "Intermediário",
    "Avançado",
    "Especialista",
]


def escolher_nivel():
    return random.choices(
        NIVEIS,
        weights=[0.15, 0.50, 0.30, 0.05],
        k=1
    )[0]


def preparar_agentes_com_operacao(
    df_agentes,
    df_equipes
):
    return df_agentes.merge(
        df_equipes[
            ["team_key", "operation_key"]
        ],
        on="team_key",
        how="left"
    )


def gerar_bridge_agent_skill(df_agentes):

    registros = []

    for _, agente in df_agentes.iterrows():

        agent_key = int(agente["agent_key"])
        operation_key = int(agente["operation_key"])

        configuracao = SKILLS_POR_OPERACAO[operation_key]

        # Skill principal
        skill_principal = random.choice(
            configuracao["principal"]
        )

        registros.append({
            "agent_key": agent_key,
            "skill_key": skill_principal,
            "skill_level": escolher_nivel(),
            "is_primary": True,
            "valid_from": agente["hire_date"],
            "valid_to": None,
            "is_active": True,
        })

        # Skills secundárias disponíveis
        skills_secundarias = configuracao["secundarias"].copy()

        skill_secundaria = None

        # Segunda skill
        if (
            skills_secundarias
            and random.random() < 0.60
        ):
            skill_secundaria = random.choice(
                skills_secundarias
            )

            registros.append({
                "agent_key": agent_key,
                "skill_key": skill_secundaria,
                "skill_level": escolher_nivel(),
                "is_primary": False,
                "valid_from": agente["hire_date"],
                "valid_to": None,
                "is_active": True,
            })

        # Terceira skill
        if (
            len(skills_secundarias) >= 2
            and random.random() < 0.20
        ):

            restantes = [
                skill
                for skill in skills_secundarias
                if skill != skill_secundaria
            ]

            if restantes:

                skill_terciaria = random.choice(
                    restantes
                )

                registros.append({
                    "agent_key": agent_key,
                    "skill_key": skill_terciaria,
                    "skill_level": escolher_nivel(),
                    "is_primary": False,
                    "valid_from": agente["hire_date"],
                    "valid_to": None,
                    "is_active": True,
                })

    return pd.DataFrame(registros)


if __name__ == "__main__":
    print(
        "Gerador da bridge_agent_skill"
    )