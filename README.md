#  Dashboard: Educação, População e Desenvolvimento Global

Um painel interativo desenvolvido em Python (Streamlit) para analisar a correlação multivariada entre o **Investimento Público em Educação (% do PIB)**, o **Crescimento Econômico (PIB per capita)** e a **Estrutura Demográfica (População)** de diversos países.

Este projeto foi construído para demonstrar, através de dados reais extraídos da API do Banco Mundial, como o capital humano impacta o desenvolvimento das nações e — o mais importante — como esse retorno possui uma defasagem temporal (*Lag Temporal*).

## Principais Funcionalidades e Metodologia

* **Análise de Defasagem Temporal (Lag):** A educação não gera riqueza do dia para a noite. O painel permite deslocar o investimento em educação no tempo (ex: comparar o investimento de 2010 com o PIB de 2015), provando estatisticamente que o retorno do capital humano leva anos para se materializar.
* **Segmentação Econômica:** Classificação automática dos países em **Desenvolvidos, Em Desenvolvimento e Subdesenvolvidos**, mitigando a *Armadilha da Renda Média* e evitando que países ricos distorçam as retas de tendência dos países pobres.
* **Visualização Multivariada (3D em 2D):** Gráficos de dispersão interativos onde o tamanho da esfera representa a **População Total** do país, adicionando a escala demográfica à análise.
* **Extração Automática de Dados:** Script independente (`gerar_dados.py`) que consome a API do Banco Mundial (`wbgapi`), garantindo que o painel use sempre os dados mais recentes sem necessidade de baixar planilhas manualmente.
* **Cálculo de Correlação:** Exibição dinâmica da correlação estatística de Pearson conforme os filtros aplicados pelo usuário.

##  Tecnologias Utilizadas

* **Python 3.x**
* **Streamlit:** Construção da interface e do painel interativo.
* **Pandas & NumPy:** Limpeza, engenharia de recursos (features) e manipulação de dados.
* **Plotly Express:** Geração de gráficos dinâmicos e responsivos.
* **wbgapi:** Conexão direta com o banco de dados oficial do *World Bank Group*.

##  Como Instalar e Rodar o Projeto

Siga os passos abaixo para executar o dashboard na sua máquina local:

### 1. Clone o repositório
```bash
git clone [https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git](https://github.com/SEU_USUARIO/NOME_DO_REPOSITORIO.git)
cd NOME_DO_REPOSITORIO
