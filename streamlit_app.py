import streamlit as st

st.title("🎈 My new app")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
import streamlit as st
import pandas as pd
import numpy as np # Ainda útil para manipulação de dados, mesmo sem LSTM
from sklearn.preprocessing import MinMaxScaler # Ainda útil se quisermos exibir dados escalados
import yfinance as yf
import matplotlib.pyplot as plt # Import para plotagem

# --- Configuração da Página Streamlit ---
st.set_page_config(
    page_title="Visualizador de Dados de Ações",
    layout="centered",
    initial_sidebar_state="auto"
)
st.title("📊 Visualizador de Dados de Ações")
st.markdown("""
    Esta aplicação permite-lhe **descarregar e visualizar dados históricos de preço de fecho** de ações
    usando o Yahoo Finance.
""")

# --- Função para Preparar Dados (sem partes específicas do LSTM) ---
@st.cache_data(ttl=3600) # Cache data for 1 hour to avoid repeated downloads
def preparar_dados(ticker, periodo, intervalo):
    """
    Descarrega e pré-processa dados históricos de ações.

    Args:
        ticker (str): Símbolo da ação (ex: AAPL).
        periodo (str): Período dos dados (ex: '1y').
        intervalo (str): Intervalo dos dados (ex: '1d').

    Returns:
        tuple: (DataFrame original, scaler), ou (None, None) se falhar.
    """
    try:
        df = yf.download(ticker, period=periodo, interval=intervalo)
        if df.empty:
            st.warning(f"Não foram encontrados dados para o ticker '{ticker}' com o período '{periodo}' e intervalo '{intervalo}'. Tente outros parâmetros.")
            return None, None

        df = df[['Close']].copy() # Use .copy() to avoid SettingWithCopyWarning
        
        # O scaler é mantido caso se queira visualizar dados normalizados no futuro,
        # mas não é estritamente necessário para esta versão.
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Apenas fit_transform se os dados forem usados para algo mais,
        # aqui apenas fit para poder reverter caso se queira
        scaler.fit(df) 
        
        return df, scaler
    except Exception as e:
        st.error(f"Erro ao descarregar ou preparar os dados: {e}")
        return None, None

# --- Parâmetros de Entrada do Utilizador ---
st.sidebar.header("Configurações")
ticker = st.sidebar.text_input("Ticker da Ação (ex: AAPL, TSLA, SAP):", value="AAPL").upper() # Convert to uppercase
periodo = st.sidebar.selectbox("Período de Dados:", ['3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'], index=2)
intervalo = st.sidebar.selectbox("Intervalo de Dados:", ['1d', '1h', '1wk', '1mo', '3mo'], index=0)

# --- Botão para Visualizar Dados ---
if st.button("Visualizar Dados"):
    if not ticker:
        st.error("Por favor, insira um ticker de ação válido.")
    else:
        with st.spinner('A carregar dados...'):
            df_data, scaler_obj = preparar_dados(ticker, periodo, intervalo)

            if df_data is not None:
                st.subheader(f"Dados Históricos de Preço de Fecho para {ticker}")
                
                # Exibir os últimos 5 registos
                st.write("Últimos 5 registos de preço de fecho:")
                st.dataframe(df_data.tail())

                # --- Visualização dos Dados ---
                fig, ax = plt.subplots(figsize=(12, 7))
                ax.plot(df_data.index, df_data['Close'], label='Preço de Fecho Histórico', color='blue')
                
                ax.set_title(f'Preço de Fecho de {ticker} ({periodo} - {intervalo})', fontsize=16)
                ax.set_xlabel('Data', fontsize=12)
                ax.set_ylabel('Preço de Fecho ($)', fontsize=12)
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.7)
                plt.xticks(rotation=45)
                plt.tight_layout() # Adjust layout to prevent labels from overlapping
                st.pyplot(fig)

                st.info(f"Dados carregados com sucesso para {ticker}.")
            else:
                st.warning("Não foi possível carregar os dados. Verifique o ticker e os parâmetros selecionados.")