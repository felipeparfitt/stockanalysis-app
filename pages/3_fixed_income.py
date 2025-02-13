import streamlit as st
import pandas as pd
import requests
from datetime import date
from streamlit_extras.metric_cards import style_metric_cards
from functools import reduce
import numpy as np

###########################
######## Functions ########
###########################


@st.cache_data
def bcb_expec_data(indicador: str, tipoCalculo: str = "L") -> pd.DataFrame:
    """
    This function returns the expected data from the bcb API for the given indicator.

    Useful links:
        https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/aplicacao#!/recursos
        https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/documentacao

    Parameters
    ----------
    indicador : str
        'IPCA' - Indicador de inflação
        'Selic' - Taxa basica de juros
    tipoCalculo : str
        'C' - Short term
        'M' - Medium term
        'L' - Long term

    """
    # Requesting the data from the bcb API
    url = f"https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/odata/ExpectativasMercadoTop5Anuais?$top=5&$filter=Indicador%20eq%20'{indicador}'%20and%20tipoCalculo%20eq%20'{tipoCalculo}'&$orderby=Data%20desc&$format=json"
    response = requests.get(url)
    data = response.json()["value"]

    # Creating a DataFrame with the data collected
    df = pd.DataFrame(data)

    return df


def get_text_indicator(indicador: str, df_ref: pd.DataFrame) -> str:
    """
    This function returns the text indicator for the given indicator.
    """

    list_expec = [
        f"- In {year}: {df_ref.loc[df_ref['DataReferencia'] == year, 'Media'].values[0]:.2f}".replace(
            ".", ","
        )
        + "% p.a.  \n"
        for year in dataRef
    ]

    add_text_last_year = "".join(list_expec[-1]).replace("In", "After")
    text_expec = f'**{indicador}** \n{"".join(list_expec)}' + add_text_last_year
    return text_expec


@st.cache_data
def bcb_hist_data(
    series_code: str, start_date: str, end_date: str = date.today().strftime("%d/%m/%Y")
) -> pd.DataFrame:
    """
    This function returns the historical data
    from the bcb API for the given indicator.

    Parameters
    ----------
    series_code : str
        '432' - Accumulated Selic Rate (Annual) %a.a.
        '13522' - Accumulated IPCA (12 months) %a.a.
        '4389' - Accumulated CDI (Annual) %a.a.
    """
    # Requesting the data from the bcb API
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_code}/dados?formato=json&dataInicial={start_date}&dataFinal={end_date}"
    response = requests.get(url)
    data = response.json()

    # Creating a DataFrame with the data collected
    df = pd.DataFrame(data)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = df["valor"].astype(np.float32)
    df.set_index("data", inplace=True)

    return df


##############################
######## Loading Data ########
##############################

df_ipca_expec = bcb_expec_data(indicador="IPCA")
df_selic_expec = bcb_expec_data(indicador="Selic")
df_cdi_expec = df_selic_expec.copy()
df_cdi_expec["Indicador"] = "CDI"
df_cdi_expec["Media"] = df_cdi_expec["Media"] - 0.1
# Creating a list with the dataRef
dataRef = df_ipca_expec["DataReferencia"].to_list()

# BCB Codes
start_date = "01/01/2010"
selic_code = 432  # Accumulated Selic Rate (Annual)
ipca_code = 13522  # Accumulated IPCA (12 months)
cdi_code = 4389  # Accumulated CDI (Annual)

# Getting historical data
df_cdi_hist = bcb_hist_data(cdi_code, start_date).rename(columns={"valor": "CDI"})
df_selic_hist = bcb_hist_data(selic_code, start_date).rename(columns={"valor": "SELIC"})
df_ipca_hist = bcb_hist_data(ipca_code, start_date).rename(columns={"valor": "IPCA"})


# Sidebar
with st.sidebar:
    st.markdown(
        "<h1 style='text-align: center;'>Filters</h1>",
        unsafe_allow_html=True,
    )

    st.date_input(label="Maturity date", value="today")
    st.number_input(
        label="Rentabilidade LCI / LCA",
        min_value=0.0,
        value=85.0,
        step=0.1,
        format="%0.1f",
    )
    st.number_input(
        label="Rentabilidade fundo DI",
        min_value=0.0,
        value=100.0,
        step=0.1,
        format="%0.1f",
    )
    st.number_input(
        label="Rentabilidade CDB",
        min_value=0.0,
        value=100.0,
        step=0.1,
        format="%0.1f",
    )

## Main Page

# Title
st.markdown(
    "<h1 style='text-align: center;'>Fixed Income Investment Analysis</h1>",
    unsafe_allow_html=True,
)

# Metric Cards
col_selic, col_ipca, col_cdi = st.columns(3, gap="large")
style_metric_cards(
    background_color="#272731", border_left_color="#253951", border_color="#253951"
)

with col_selic:
    # Getting last selic value
    last_selic = df_selic_hist.iloc[-1]
    last_selic_date = last_selic.name.strftime("%d/%m/%Y")
    last_selic_value = last_selic.values[0]
    # Getting selic expected values
    text_selic_expec = get_text_indicator(indicador="Selic", df_ref=df_selic_expec)
    # Selic Metric Card
    st.metric(
        label=f"**Selic** - {last_selic_date}",
        value=f"{last_selic_value:.2f}% a.a.",
        label_visibility="visible",
        help=text_selic_expec,
    )

with col_ipca:
    # Getting last IPCA value
    last_ipca = df_ipca_hist.iloc[-1]
    last_ipca_date = last_ipca.name.strftime("%d/%m/%Y")
    last_ipca_value = last_ipca.values[0]
    # Getting IPCA expected values
    text_ipca_expec = get_text_indicator(indicador="IPCA", df_ref=df_ipca_expec)
    # IPCA Metric Card
    st.metric(
        label=f"**IPCA** - {last_ipca_date}",
        value=f"{last_ipca_value:.2f}% a.a.",
        label_visibility="visible",
        help=text_ipca_expec,
    )

with col_cdi:
    # Getting last CDI value
    last_cdi = df_cdi_hist.iloc[-1]
    last_cdi_date = last_cdi.name.strftime("%d/%m/%Y")
    last_cdi_value = last_cdi.values[0]
    # Getting CDI expected values
    text_cdi_expec = get_text_indicator(indicador="CDI", df_ref=df_cdi_expec)
    # CDI Metric Card
    st.metric(
        label=f"**CDI** - {last_cdi_date}",
        value=f"{last_cdi_value:.2f}% a.a.",
        label_visibility="visible",
        help=text_cdi_expec,
    )

tab_hist, tab_barras, tab_dataframe, tab_hist_taxes = st.tabs(
    ["Hist", "Barras", "DataFrame", "Historical Rates"]
)

with tab_hist:
    st.markdown("### a")


with tab_barras:
    st.markdown("### b")

with tab_dataframe:
    st.markdown("### c")

with tab_hist_taxes:

    # Getting data by month
    selic_hist_mes = df_selic_hist[df_selic_hist.index.day == 1]
    cdi_hist_mes = df_cdi_hist[df_cdi_hist.index.day == 1]
    ipca_hist_mes = df_ipca_hist[df_ipca_hist.index.day == 1]

    # Merging the dataframes
    df_merged = reduce(
        lambda left, right: pd.merge(left, right, on="data", how="outer"),
        [selic_hist_mes, ipca_hist_mes, cdi_hist_mes],
    )

    # List with the dates that have NaN values in the CDI column
    data_cdi_nan = df_merged[df_merged["CDI"].isna()].index.to_list()
    # Dataframe with CDI values from the closest date
    df_cdi_with_nan = df_cdi_hist.loc[
        [
            df_cdi_hist.index.to_series().sub(target).abs().idxmin()
            for target in data_cdi_nan
        ]
    ]
    df_merged.loc[df_merged[df_merged["CDI"].isna()].index, "CDI"] = df_cdi_with_nan[
        "CDI"
    ].values

    # Plotting the data
    st.markdown(f"### Historical Rates - Selic, IPCA and CDI")
    st.line_chart(
        data=df_merged,
        x_label="Date",
        y_label="Rates (%a.a.)",
        color=["#0000FF", "#00FF00", "#ff0f0f"],
    )

    st.markdown("TEXT ANALYSINNG THE DATA")


# col4, col5 = st.columns([2 / 3, 1 / 3], border=True, gap="large")
