from pathlib import Path


# Pasta raiz do projeto
raiz = Path(__file__).parent


# Estrutura de pastas do projeto
pastas = [
    "docs",

    "data",
    "data/raw",
    "data/processed",
    "data/samples",

    "src",
    "src/generation",
    "src/transformation",
    "src/validation",
    "src/analytics",

    "sql",
    "sql/ddl",
    "sql/dimensions",
    "sql/facts",
    "sql/views",
    "sql/kpis",

    "notebooks",

    "powerbi",

    "tests",
]


# Criação das pastas
for pasta in pastas:
    caminho = raiz / pasta
    caminho.mkdir(parents=True, exist_ok=True)


print("Estrutura do projeto criada com sucesso!")
print()
print(f"Projeto: {raiz}")
print()

for pasta in pastas:
    print(f"✓ {pasta}")