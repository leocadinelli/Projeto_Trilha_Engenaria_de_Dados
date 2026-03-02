import os
import json
import re
from datetime import date
import requests
import pandas as pd

# ===============================
# DIRETÓRIOS
# ===============================

base_diretorio = os.path.expanduser("~/project-root/data")

json_bronze = os.path.join(base_diretorio, "bronze", "bronze_issues.json")

saida_silver = os.path.join(base_diretorio, "silver")
os.makedirs(saida_silver, exist_ok=True)

saida_parquet = os.path.join(saida_silver, "silver_issues.parquet")
CSV_OUT = os.path.join(saida_silver, "csv_silver.csv")

# ===============================
# FUNÇÃO SNAKE CASE
# ===============================

def to_snake(s: str):
    if s is None:
        return ""
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s

def load_bronze():
    with open(json_bronze, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    registros = []
    ndjson_ok = True

    for line in lines:
        if not line.strip():
            continue
        try:
            registros.append(json.loads(line))
        except json.JSONDecodeError:
            ndjson_ok = False
            registros = []
            break

    if ndjson_ok:
        return registros

    with open(json_bronze, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        if "issues" in data:
            return data["issues"]
        return [data]

    raise Exception("Formato Bronze Inválido!")


def normalizar(reg):
    df = pd.json_normalize(reg, max_level=2)
    df.columns = [to_snake(c) for c in df.columns]

    df = df.explode("assignee").explode("timestamps")

    df_assignee = pd.json_normalize(df["assignee"])
    df_assignee.columns = [f"assignee_{c}" for c in df_assignee.columns]

    df_timestamp = pd.json_normalize(df["timestamps"])
    df_timestamp.columns = [f"timestamps_{c}" for c in df_timestamp.columns]

    df.drop(columns=["assignee", "timestamps"], inplace=True)
    df = pd.concat([df, df_assignee, df_timestamp], axis=1)

    df["timestamps_created_at"] = pd.to_datetime(
        df["timestamps_created_at"], errors="coerce", utc=True
    )

    df["timestamps_resolved_at"] = pd.to_datetime(
        df["timestamps_resolved_at"], errors="coerce", utc=True
    )

    df.rename(columns={
        "timestamps_created_at": "created_at",
        "timestamps_resolved_at": "resolved_at"
    }, inplace=True)

    return df

def buscar_feriados(ano):
    url = f"https://brasilapi.com.br/api/feriados/v1/{ano}"
    response = requests.get(url)

    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df["date"] = pd.to_datetime(df["date"]).dt.date
        return df
    else:
        return pd.DataFrame(columns=["date"])


def contar_feriados(created_at, resolved_at, feriados_set):

    if pd.isna(created_at) or pd.isna(resolved_at):
        return 0

    inicio = created_at.date()
    fim = resolved_at.date()

    return sum(inicio <= f <= fim for f in feriados_set)



def main():

    reg = load_bronze()
    df_final = normalizar(reg)

    # Buscar feriados últimos 5 anos
    ano_atual = date.today().year
    lista_feriados = []

    for a in range(ano_atual - 5, ano_atual + 1):
        lista_feriados.append(buscar_feriados(a))

    df_feriados = pd.concat(lista_feriados, ignore_index=True)
    feriados_set = set(df_feriados["date"])

    df_final["created_at"] = pd.to_datetime(df_final["created_at"])
    df_final["resolved_at"] = pd.to_datetime(df_final["resolved_at"])


    df_final["feriado"] = [
        contar_feriados(c, r, feriados_set)
        for c, r in zip(df_final["created_at"], df_final["resolved_at"])
    ]


    df_final.to_parquet(saida_parquet, index=False)
    df_final.to_csv(CSV_OUT, index=False, encoding="utf-8", sep=";")

    

if __name__ == "__main__":
    main()