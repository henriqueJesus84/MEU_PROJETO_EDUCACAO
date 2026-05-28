import wbgapi as wb
import pandas as pd
import os

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
pasta_dados = os.path.join(diretorio_atual, 'dados')

if not os.path.exists(pasta_dados):
    os.makedirs(pasta_dados)

print("Conectando ao Banco Mundial...")

try:
    print("Baixando dados de PIB per capita...")
    pib_df = wb.data.DataFrame(
        'NY.GDP.PCAP.CD', mrnev=15, labels=True).reset_index()

    print("Baixando dados de Investimento em Educação...")
    edu_df = wb.data.DataFrame(
        'SE.XPD.TOTL.GB.ZS', mrnev=15, labels=True).reset_index()

    print("Baixando dados de População Total...")
    pop_df = wb.data.DataFrame(
        'SP.POP.TOTL', mrnev=15, labels=True).reset_index()

    def estruturar_tabela(df, nome_coluna_final):
        col_codigo = 'economy'
        col_nome = 'Economy'
        colunas_anos = [col for col in df.columns if col.startswith('YR')]

        df_filtrado = df[[col_codigo, col_nome] + colunas_anos]
        df_melted = df_filtrado.melt(
            id_vars=[col_codigo, col_nome], var_name='ano', value_name=nome_coluna_final)
        df_melted['ano'] = df_melted['ano'].str.replace('YR', '').astype(int)

        df_melted = df_melted.rename(
            columns={col_codigo: 'codigo', col_nome: 'pais'})
        return df_melted

    pib = estruturar_tabela(pib_df, 'pib_per_capita')
    edu = estruturar_tabela(edu_df, 'investimento_educacao')
    pop = estruturar_tabela(pop_df, 'populacao')

    print("Combinando as bases de dados...")
    df_final = pd.merge(pib, edu, on=['codigo', 'pais', 'ano'], how='outer')
    df_final = pd.merge(df_final, pop, on=[
                        'codigo', 'pais', 'ano'], how='outer')

    df_final = df_final.dropna(
        subset=['pib_per_capita', 'investimento_educacao', 'populacao'], how='all')

    df_final['pib_per_capita'] = pd.to_numeric(
        df_final['pib_per_capita'], errors='coerce')
    df_final['investimento_educacao'] = pd.to_numeric(
        df_final['investimento_educacao'], errors='coerce')
    df_final['populacao'] = pd.to_numeric(
        df_final['populacao'], errors='coerce')

    caminho_salvar = os.path.join(pasta_dados, 'dados_banco_mundial.csv')
    df_final.to_csv(caminho_salvar, index=False)

    print("Sucesso! Dados numéricos e textuais gravados com sucesso.")

except Exception as e:
    print(f"Erro durante a execução: {e}")
