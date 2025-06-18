import pandas as pd

def carregar_dados():
    gps = pd.read_csv("dados/dados_gps.csv", sep=";")
    faixas = pd.read_csv("dados/faixas_horarias.csv", sep=";")
    linhas = pd.read_csv("dados/linhas_e_nucleos.csv", sep=";")
    programacao = pd.read_csv("dados/programacao_partidas.csv", sep=";")
    return gps, faixas, linhas, programacao

def preparar_base(gps, faixas, linhas, programacao):
    # Renomear colunas
    gps = gps.rename(columns={"Linha": "linha"})
    linhas = linhas.rename(columns={"Linha": "linha", "Núcleo": "nucleo", "Nome_Linha": "nome_linha"})
    programacao = programacao.rename(columns={
        "Linha": "linha",
        "Viagens Programadas": "partidas_programadas",
        "Faixa": "faixa_horaria"
    })
    faixas = faixas.rename(columns={"Faixa_Horaria": "faixa_horaria"})

    # Marca se a viagem foi reconhecida
    gps["partida_executada"] = gps["Viagem Reconhecida"].notnull().astype(int)

    # Agrupa por linha
    execucoes = gps.groupby("linha").agg(partidas_executadas=("partida_executada", "sum")).reset_index()

    # Faz os merges
    base = programacao.merge(execucoes, on="linha", how="left")
    base = base.merge(linhas, on="linha", how="left")
    base = base.merge(faixas, on="faixa_horaria", how="left")

    # Garantir tipos numéricos e tratar nulos
    base["partidas_executadas"] = base["partidas_executadas"].fillna(0)
    base["partidas_programadas"] = pd.to_numeric(base["partidas_programadas"], errors="coerce").fillna(0)

    base["percentual"] = (base["partidas_executadas"] / base["partidas_programadas"]) * 100
    base["percentual"] = base["percentual"].round(2)

    return base
