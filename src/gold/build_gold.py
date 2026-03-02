import pandas as pd
from sla_calculation import calcular_metricas_sla
import os 

SILVER_PATH = os.path.expanduser("~/project-root/data/silver/silver_issues.parquet")

GOLD_FACT_PATH = os.path.expanduser("~/project-root/data/gold/gold_sla_fact.parquet")
GOLD_STATUS_PATH = os.path.expanduser("~/project-root/data/gold/gold_sla_status.parquet")

GOLD_STATUS_CSV = os.path.expanduser("~/project-root/data/gold/gold_sla_status.csv")
RELATORIO1_PATH = os.path.expanduser("~/project-root/data/gold/relatorio_sla_medio_por_analista.csv")
RELATORIO2_PATH = os.path.expanduser("~/project-root/data/gold/relatorio_sla_medio_por_tipo_chamado.csv")



df = pd.read_parquet(SILVER_PATH)

# Cálculo SLA

df[['tempo_resolucao_horas_uteis',
    'sla_esperado_horas',
    'sla_status']] = df.apply(

    lambda row: calcular_metricas_sla(
        row['created_at'],
        row['resolved_at'],
        row['priority'],
        row['feriado']
    ),
    axis=1,
    result_type='expand'
)

gold_sla = df.rename(columns={
    'id': 'id_chamado',
    'issue_type': 'tipo_chamado',
    'assignee_name': 'analista_responsavel',
    'priority': 'prioridade',
    'created_at': 'data_abertura',
    'resolved_at': 'data_resolucao'
})


gold_sla = gold_sla[[
    'id_chamado',
    'tipo_chamado',
    'analista_responsavel',
    'prioridade',
    'data_abertura',
    'data_resolucao',
    'tempo_resolucao_horas_uteis',
    'sla_esperado_horas',
    'sla_status'
]]



gold_sla.to_parquet(
    GOLD_FACT_PATH,
    engine='pyarrow',
    index=False
)

gold_sla.to_csv(GOLD_STATUS_CSV)


# SLA Médio por Analista

df_resolvidos = gold_sla[
    gold_sla["tempo_resolucao_horas_uteis"].notna()
]

relatorio1 = (
    df_resolvidos
    .groupby("analista_responsavel")
    .agg(
        quantidade_chamados=("id_chamado", "count"),
        sla_medio_horas=("tempo_resolucao_horas_uteis", "mean")
    )
    .reset_index()
)

relatorio1["sla_medio_horas"] = relatorio1["sla_medio_horas"].round(2)

relatorio1 = relatorio1.rename(columns={
    "analista_responsavel": "Analista",
    "quantidade_chamados": "Quantidade de chamados",
    "sla_medio_horas": "SLA médio (horas)"
})

relatorio1.to_csv(
    RELATORIO1_PATH,
    sep=";",
    index=False
)

# SLA Médio por Tipo de Chamado

relatorio2 = df_resolvidos.groupby("tipo_chamado").agg(
                                                        quantidade_chamados=("id_chamado", "count"),
                                                        sla_medio_horas=("tempo_resolucao_horas_uteis", "mean")
                                                        ).reset_index()

relatorio2.to_csv(
    RELATORIO2_PATH,
    sep=";",
    index=False
)

print("Gold SLA MART gerado com sucesso!")