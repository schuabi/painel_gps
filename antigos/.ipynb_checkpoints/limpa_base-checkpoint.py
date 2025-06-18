import pandas as pd
gps = pd.read_csv("C:/dashboard_onibus/dados/dados_gps.csv", sep=";")
faixas = pd.read_csv("C:/dashboard_onibus/dados/faixas_horarias.csv", sep=";")
linhas = pd.read_csv("C:/dashboard_onibus/dados/linhas_e_nucleos.csv", sep=";")
programacao = pd.read_csv("C://dashboard_onibus/dados/programacao_partidas.csv", sep=";")

del gps['Linha Informada a SMTR']
del gps['Linha Realizada pela SMTR']
del gps['Veículo Consolidado pela SMTR']
del gps ['Início da Viagem pela SMTR']
del gps ['Término da Viagem pela SMTR']
del gps ['Viagem Reconhecida']

gps.to_csv('C:/dashboard_onibus/dados_gps_base.csv', index=False)

