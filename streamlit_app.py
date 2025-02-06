import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta

st.set_page_config(
    page_title="B3 Stock Market Analysis - Felipe Parfitt",
    page_icon=":bar_chart",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_data(empresas: list):
    a = " ".join(empresas)

    dados_acao = yf.Tickers(a)
    cotacao_acao = dados_acao.history(period="1d", start="2020-01-01", end=date.today())
    cotacao_close = cotacao_acao["Close"]
    return cotacao_close


@st.cache_data
def load_ibov_tickers():
    df_ibov = (
        pd.read_csv("./data/IBOVDia_05-02-25.csv", sep=";", thousands=".", decimal=",")
        .sort_values(by="Part. (%)", ascending=False)
        .reset_index(drop=True)
    )
    all_tickers = df_ibov.Codigo.to_list()
    all_tickers = [ticker + ".SA" for ticker in all_tickers]
    return all_tickers


all_tickers = load_ibov_tickers()
stock_market_prices = load_data(all_tickers)

with st.sidebar:

    st.header("B3 Stock Market Analysis")

    st.subheader("PARAM 1 D")

    min_data_value = stock_market_prices.index.min().to_pydatetime()
    max_data_value = stock_market_prices.index.max().to_pydatetime()
    data_range = st.slider(
        "Between which dates?",
        min_value=min_data_value,
        max_value=max_data_value,
        value=(min_data_value, max_data_value),
        step=timedelta(days=1),
    )

    # MultiSelect filter
    stock_list = st.multiselect(
        label="Choose the Stock",
        options=stock_market_prices.columns,
        default=all_tickers[0:5],
    )
    if stock_list:
        stock_market_prices = stock_market_prices[stock_list]
        if len(stock_list) == 1:
            acao_unica = stock_list[0]
            stock_market_prices = stock_market_prices.rename(
                columns={acao_unica: "Close"}
            )

    st.markdown(
        """
        ___
        Created by [Felipe Parfitt](https://felipeparfitt.com)
        
        """
    )


st.title("🎈 App Name")

st.write("Hello world!")

stock_market_prices = stock_market_prices.loc[data_range[0] : data_range[-1]]

st.line_chart(stock_market_prices)


texto_perf_ativos = ""
if len(stock_list) == 1:
    stock_market_prices = stock_market_prices.rename(columns={"Close": acao_unica})

for stock in stock_list:
    perf_ativo = (
        stock_market_prices[stock].iloc[-1] / stock_market_prices[stock].iloc[0]
    ) - 1
    perf_ativo = float(perf_ativo)

    # Markdown Text + Color
    if perf_ativo > 0:
        texto_perf_ativos = texto_perf_ativos + f"  \n{stock}: :green[{perf_ativo:.1%}]"
    elif perf_ativo < 0:
        texto_perf_ativos = texto_perf_ativos + f"  \n{stock}: :red[{perf_ativo:.1%}]"
    else:
        texto_perf_ativos = texto_perf_ativos + f"  \n{stock}: {perf_ativo:.1%}"

    print(texto_perf_ativos)
st.write(
    f"""
    ### Performance dos Ativos
    Essa foi a perf. do ativos selecionados:{texto_perf_ativos}
    """
)


# with st.expander("Data Preview"):
#     st.dataframe(
#         df,
#         column_cofig={'colname: st...'}
#     )
