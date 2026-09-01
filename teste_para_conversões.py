import pandas as pd
import json

# O array de objetos JSON que você solicitou
dados_json = [
    {"id": 1, "nome": "Ana Silva", "idade": 28, "cidade": "São Paulo", "ativo": True},
    {"id": 2, "nome": "Bruno Costa", "idade": 34, "cidade": "Rio de Janeiro", "ativo": False},
    {"id": 3, "nome": "Carla Souza", "idade": 41, "cidade": "Belo Horizonte", "ativo": True},
    {"id": 4, "nome": "Diego Lima", "idade": 23, "cidade": "Porto Alegre", "ativo": True}
]

# Convertendo o JSON para um DataFrame do Pandas
df = pd.DataFrame(dados_json)

# 1. Gerando o arquivo CSV
df.to_csv("dados_teste.csv", index=False, encoding="utf-8")

# 2. Gerando o arquivo Excel (.xlsx)
df.to_excel("dados_teste.xlsx", index=False)

# 3. Gerando o arquivo Parquet (Requer a biblioteca pyarrow ou fastparquet instalada)
df.to_parquet("dados_teste.parquet", index=False)

# 4. Gerando o arquivo JSON
df.to_json("dados_teste.json", index=False, orient="records")

print("Arquivos 'dados_teste.csv', 'dados_teste.xlsx' e 'dados_teste.parquet' gerados com sucesso!")