import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import os

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Educação e Desenvolvimento Global",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CARREGAMENTO E LIMPEZA DE DADOS ---


@st.cache_data
def carregar_dados():
    caminho_arquivo = os.path.join("dados", "dados_banco_mundial.csv")

    if not os.path.exists(caminho_arquivo):
        return None

    df = pd.read_csv(caminho_arquivo)

    # Garante que as colunas essenciais existem antes de limpar os dados nulos
    colunas_obrigatorias = ["pib_per_capita", "investimento_educacao"]
    if all(col in df.columns for col in colunas_obrigatorias):
        df = df.dropna(subset=colunas_obrigatorias, how="all")

    return df


df = carregar_dados()

# Trava de segurança caso o arquivo falte
if df is None:
    st.error("Erro Crítico: Arquivo 'dados/dados_banco_mundial.csv' não encontrado. Rode o script 'gerar_dados.py' primeiro.")
    st.stop()

# Trava de segurança para a coluna de população (Fallback)
if "populacao" not in df.columns:
    st.warning("A coluna 'populacao' não foi encontrada. Usando tamanho padrão. Atualize seus dados executando 'gerar_dados.py'.")
    df["populacao"] = 1.0

# --- 3. ENGENHARIA DE RECURSOS (FEATURES) ---
# Classificação de Desenvolvimento Econômico
pib_max_por_pais = df.groupby("pais")["pib_per_capita"].max().reset_index()


def classificar_desenvolvimento(pib):
    if pib >= 30000:
        return "Desenvolvido"
    elif pib >= 4000:
        return "Em Desenvolvimento"
    else:
        return "Subdesenvolvido"


pib_max_por_pais["status_desenvolvimento"] = pib_max_por_pais["pib_per_capita"].apply(
    classificar_desenvolvimento)
mapeamento_status = dict(
    zip(pib_max_por_pais["pais"], pib_max_por_pais["status_desenvolvimento"]))
df["status_desenvolvimento"] = df["pais"].map(mapeamento_status)

# Ordenação crucial para que o Lag Temporal funcione perfeitamente
df = df.sort_values(by=["pais", "ano"])

# --- 4. INTERFACE: CABEÇALHO ---
st.title("📊 Educação, População e Desenvolvimento Global")
st.markdown(
    """
    Este dashboard analisa de forma multivariada a relação entre o **Investimento em Educação (% do PIB)** e o **PIB per capita**.
    O tamanho das esferas no gráfico de dispersão representa o **tamanho da população** do país, permitindo avaliar efeitos de escala demográfica.
    """
)

# --- 5. INTERFACE: BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Análise")

# Filtro 1: Desenvolvimento
status_disponiveis = ["Todos", "Desenvolvido",
                      "Em Desenvolvimento", "Subdesenvolvido"]
status_selecionado = st.sidebar.selectbox(
    "Nível de Desenvolvimento:", options=status_disponiveis, index=0)

df_filtrado_status = df if status_selecionado == "Todos" else df[
    df["status_desenvolvimento"] == status_selecionado]

# Filtro 2: Países
paises_disponiveis = sorted(df_filtrado_status["pais"].unique())
ano_max_dados = df_filtrado_status["ano"].max()
df_ano_recente = df_filtrado_status[df_filtrado_status["ano"] == ano_max_dados]

# Seleciona os 4 maiores PIBs do grupo por padrão
paises_padrao_validados = df_ano_recente.nlargest(
    4, "pib_per_capita")["pais"].unique().tolist()
if not paises_padrao_validados:
    paises_padrao_validados = [
        paises_disponiveis[0]] if paises_disponiveis else []

paises_selecionados = st.sidebar.multiselect(
    "Países para Comparação:", options=paises_disponiveis, default=paises_padrao_validados
)

# Filtro 3: Defasagem Temporal (Lag)
st.sidebar.subheader("Impacto Temporal")
anos_lag = st.sidebar.slider(
    "Defasagem da Educação (Anos de Lag):", min_value=0, max_value=15, value=5)

coluna_edu_x = "investimento_educacao"
if anos_lag > 0:
    df[f"investimento_educacao_lag_{anos_lag}"] = df.groupby(
        "pais")["investimento_educacao"].shift(anos_lag)
    coluna_edu_x = f"investimento_educacao_lag_{anos_lag}"

# Filtro 4: Janela de Tempo
ano_min, ano_max_limite = int(df["ano"].min()), int(df["ano"].max())
anos_selecionados = st.sidebar.slider(
    "Intervalo de Anos (PIB):", min_value=ano_min, max_value=ano_max_limite,
    value=(max(ano_min, 2010), min(ano_max_limite, 2023))
)

# Aplicação final dos filtros
df_final = df[
    (df["pais"].isin(paises_selecionados)) &
    (df["ano"] >= anos_selecionados[0]) &
    (df["ano"] <= anos_selecionados[1])
]

# --- 6. VISUALIZAÇÃO: KPIs ---
st.subheader("📌 Métricas Gerais no Período Selecionado")

if df_final.empty:
    st.warning("Não há dados disponíveis para os filtros selecionados.")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        pib_medio = df_final["pib_per_capita"].mean()
        st.metric(label="PIB per Capita Médio", value="Sem dados" if pd.isna(
            pib_medio) else f"${pib_medio:,.2f}")

    with col2:
        edu_media = df_final[coluna_edu_x].mean()
        texto_label = "Investimento Médio em Educação" if anos_lag == 0 else f"Inves. Médio (Lag de {anos_lag} anos)"
        st.metric(label=texto_label, value="Sem dados" if pd.isna(
            edu_media) else f"{edu_media:.2f}%")

    with col3:
        pop_media = df_final["populacao"].mean()
        st.metric(label="População Média do Grupo", value="Sem dados" if pd.isna(
            pop_media) else f"{pop_media:,.0f}")

st.write("---")

# --- 7. VISUALIZAÇÃO: GRÁFICOS ---
if not df_final.empty:
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.subheader("📈 Tendência de Investimento")
        fig_linha = px.line(
            df_final, x="ano", y="investimento_educacao", color="pais", markers=True,
            labels={"ano": "Ano",
                    "investimento_educacao": "Inves. em Educação (% do PIB)"}
        )
        st.plotly_chart(fig_linha, width='stretch')

    with col_graf2:
        st.subheader("🔍 Correlação Demográfica e Econômica")
        label_eixo_x = "Investimento em Educação (% do PIB)" if anos_lag == 0 else f"Investimento em Educação (Lag de {anos_lag} anos)"

        # Limpeza severa de nulos e zeros para o Plotly não quebrar o cálculo de tamanho e tendência
        df_plot_disp = df_final.dropna(
            subset=[coluna_edu_x, "pib_per_capita", "populacao"])
        df_plot_disp = df_plot_disp[df_plot_disp["populacao"] > 0]

        if df_plot_disp.empty:
            st.info(
                "Dados insuficientes para gerar a dispersão. Tente ajustar o Lag ou os Anos.")
        else:
            fig_disp = px.scatter(
                df_plot_disp, x=coluna_edu_x, y="pib_per_capita", color="pais",
                size="populacao", size_max=45, hover_name="ano",
                hover_data={"populacao": ":,.0f", "pib_per_capita": ":,.2f"},
                labels={coluna_edu_x: label_eixo_x,
                        "pib_per_capita": "PIB per Capita (USD)", "populacao": "População"},
                trendline="ols"
            )
            st.plotly_chart(fig_disp, width='stretch')

    # --- 8. VISUALIZAÇÃO: INSIGHTS E CONCLUSÕES ---
    st.subheader("💡 Insights Analíticos")
    df_insights = df_final.dropna(subset=[coluna_edu_x, "pib_per_capita"])

    if len(df_insights) > 5:
        correlacao = df_insights[coluna_edu_x].corr(
            df_insights["pib_per_capita"])
        if pd.isna(correlacao):
            st.info("Dados sem variação estatística suficiente.")
        else:
            st.write(
                f"A correlação de Pearson para este grupo considerando um lag de **{anos_lag} anos** é: **{correlacao:.2f}**")

            st.markdown("""
            **Guia de Interpretação (Tamanho das Esferas):**
            * **Massas Populacionais Grandes:** Alterar o PIB per capita através da educação em nações muito populosas requer um esforço fiscal gigantesco ao longo de décadas. A inércia econômica é maior.
            * **Massas Populacionais Menores:** Costumam apresentar uma resposta elástica mais rápida na economia. Ciclos de investimento geram retornos mais verticais no gráfico.
            """)
    else:
        st.info("Selecione uma base amostral maior (mais países ou anos) para o cálculo da estatística de Pearson.")
