import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import date, timedelta


# Loading Stock Price
@st.cache_data
def load_data(empresas: list):
    empresas = " ".join(empresas)
    dados_acao = yf.Tickers(empresas)
    cotacao_acao = dados_acao.history(period="1d", start="2020-01-01", end=date.today())
    cotacao_close = cotacao_acao["Close"]
    return cotacao_close


# Loading ibovespa information
@st.cache_data
def load_ibov_info():
    df_ibov = (
        pd.read_csv("./data/IBOVDia_05-02-25.csv", sep=";", thousands=".", decimal=",")
        .sort_values(by="Part. (%)", ascending=False)
        .reset_index(drop=True)
    )
    df_ibov["Codigo_yfinance"] = df_ibov["Codigo"] + ".SA"
    return df_ibov


# Loading ibovespa information
df_ibov = load_ibov_info()
# Getting all tickers
all_tickers = df_ibov.Codigo_yfinance
# Loading all ibov stock market data
stock_market_prices = load_data(all_tickers)

# Sidebar
with st.sidebar:
    st.markdown(
        "<h1 style='text-align: center;'>Filters</h1>",
        unsafe_allow_html=True,
    )

    min_data_value = stock_market_prices.index.min().to_pydatetime()
    max_data_value = stock_market_prices.index.max().to_pydatetime()
    data_range = st.slider(
        "Select Date Range",
        min_value=min_data_value,
        max_value=max_data_value,
        value=(min_data_value, max_data_value),
        step=timedelta(days=1),
    )

    # MultiSelect filter
    stock_list = st.multiselect(
        label="Choose Asset to Analyze",
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


## Main Page

# Filtering data by date
stock_market_prices = stock_market_prices.loc[data_range[0] : data_range[-1]]

# Plotting the stock market historical prices
st.markdown(
    "<h1 style='text-align: center;'>Stock Market Analysis</h1>",
    unsafe_allow_html=True,
)
st.markdown(f"### Stock Market Historical Prices")
st.line_chart(stock_market_prices, x_label="Date", y_label="Price (R$)")


# Assets Performance
st.markdown(f"### Assets Performance")

if len(stock_list) == 1:
    stock_market_prices = stock_market_prices.rename(columns={"Close": acao_unica})

stock_dict = {}
for stock_ticker in stock_list:
    # Stock prices
    ini_stock_price = stock_market_prices[stock_ticker].iloc[0]
    fin_stock_price = stock_market_prices[stock_ticker].iloc[-1]
    stock_perf = float(fin_stock_price / ini_stock_price) - 1
    stock_name = df_ibov[df_ibov["Codigo_yfinance"] == stock_ticker]["Acao"].iloc[0]

    # Markdown Text + Color
    texto_perf_ativos = (
        f":green[ $\u2191$ {stock_perf:.1%}]"
        if stock_perf > 0
        else f":red[ $\u2193$ {stock_perf:.1%}]"
    )

    stock_dict[stock_ticker] = {
        "ini_stock_price": ini_stock_price,
        "fin_stock_price": fin_stock_price,
        "stock_perf": stock_perf,
        "stock_name": stock_name,
        "stock_perf_with_color": texto_perf_ativos,
    }

# Stock performance grid
stock_items = list(stock_dict.items())

# Grid parameters
max_cols = 5  # Number of columns per row

# Loop through actions dynamically
rows = [stock_items[i : i + max_cols] for i in range(0, len(stock_items), max_cols)]

for row in rows:
    cols = st.columns(len(row), border=True)  # Criar colunas dinâmicas
    for idx, (ticker, details) in enumerate(row):
        with cols[idx]:
            st.markdown(f" :blue-background[ {ticker}]  \n **{details['stock_name']}**")
            st.write(f"**Initial Price:** R$ {details['ini_stock_price']:.2f}")
            st.write(f"**Final Price:** R$ {details['fin_stock_price']:.2f}")
            st.write(f":grey-background[{details['stock_perf_with_color']}]")
