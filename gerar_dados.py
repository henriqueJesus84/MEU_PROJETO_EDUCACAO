import wbgapi as wb
import pandas as pd
import os

# Cria a pasta se não existir
if not os.path.exists('dados'):
    os.makedirs('dados')

# Indicadores: PIB per capita, Investimento em Educação e População Total (SP.POP.TOTL)
indicadores = {
    'NY.GDP.PCAP.CD': 'pib_per_capita',
    'SE.XPD.TOTL.GB.ZS': 'investimento_educacao',
    'SP.POP.TOTL': 'populacao'
}

print("Baixando dados atualizados do Banco Mundial (incluindo População)...")

# Baixa os dados
df = wb.data.DataFrame(list(indicadores.keys()),
                       mrnev=15, labels=True).reset_index()

# O Banco Mundial retorna 'Economy' (Nome do país) e 'series' (Código do indicador)
df = df.rename(columns={'Economy': 'pais', 'series': 'indicador'})

# SEPARAÇÃO SEGURA: Pega apenas as colunas de identificação e as colunas de anos (que começam com 'YR')
colunas_anos = [col for col in df.columns if col.startswith('YR')]
df = df[['pais', 'indicador'] + colunas_anos]

# Achatamento da tabela (agora 100% seguro contra textos)
df = df.melt(id_vars=['pais', 'indicador'], var_name='ano', value_name='valor')

# Limpa o texto 'YR' do ano e converte para número (Ex: 'YR2010' vira 2010)
df['ano'] = df['ano'].str.replace('YR', '').astype(int)

# Remonta a tabela cruzada
df = df.pivot_table(index=['pais', 'ano'],
                    columns='indicador', values='valor').reset_index()

# Renomeia os indicadores para os nomes finais do projeto
df = df.rename(columns={
    'NY.GDP.PCAP.CD': 'pib_per_capita',
    'SE.XPD.TOTL.GB.ZS': 'investimento_educacao',
    'SP.POP.TOTL': 'populacao'
})

# Salva o arquivo atualizado
df.to_csv('dados/dados_banco_mundial.csv', index=False)
print("Arquivo 'dados/dados_banco_mundial.csv' atualizado com sucesso e livre de erros!")
