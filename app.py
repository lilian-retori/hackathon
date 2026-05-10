from pathlib import Path

LOGO_PATH = Path("Logo.jpg")  # nome do arquivo da logo

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================
# CONFIG BÁSICA
# =========================

st.set_page_config(
    page_title="Do Fogo ao Lucro - PID 3.0",
    layout="wide"
)

LOGO_PATH = Path("Logo.jpg")  # ajuste se o nome da logo for outro

# Coordenadas aproximadas dos municípios chave de MG (lat, lon)
coords_municipios = {
    "João Pinheiro": (-17.74, -46.17),
    "Itamarandiba": (-17.85, -42.85),
    "Curvelo": (-18.75, -44.43),
    "Buritizeiro": (-17.35, -44.96),
    "Três Marias": (-18.20, -45.23),
    "Unaí": (-16.35, -46.90),
    "Paracatu": (-17.22, -46.87),
    "Uberaba": (-19.74, -47.93),
    "Patos de Minas": (-18.58, -46.52),
    "Perdizes": (-19.35, -47.29),
    "Itabira": (-19.62, -43.23),
    "Diamantina": (-18.24, -43.60),
    "Governador Valadares": (-18.85, -41.94),
    "Montes Claros": (-16.73, -43.86),
}

# =========================
# CARREGAR DADOS
# =========================

@st.cache_data
def load_data():
    df = pd.read_csv("dados_pam_pevs_dashboard_mg.csv")

    # Adiciona colunas de latitude e longitude com base no nome do município
    def get_lat(m):
        return coords_municipios.get(m, (None, None))[0]

    def get_lon(m):
        return coords_municipios.get(m, (None, None))[1]

    df["lat"] = df["municipio"].apply(get_lat)
    df["lon"] = df["municipio"].apply(get_lon)

    return df

df = load_data()

# =========================
# HEADER (LOGO + TÍTULO)
# =========================

col_logo, col_title = st.columns([1, 3])
with col_logo:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

with col_title:
    st.title("Do Fogo ao Lucro – Mapa de Oportunidades em MG")
    st.markdown(
        "Veja **onde a biomassa hoje vira fumaça** e onde ela pode virar **dinheiro e energia limpa**."
    )

st.markdown(
    """
    Cada bolinha no mapa é um município de Minas Gerais.

    - **Biomassa** = resíduo de lavoura e floresta.
    - **Dinheiro jogado fora** = valor do que é queimado.
    - **Lucro** = quando vale a pena levar esse resíduo até a indústria.
    """
)

# =========================
# SIDEBAR – FILTROS GERAIS
# =========================

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)

st.sidebar.markdown("### Como usar")
st.sidebar.markdown(
    """
    1. Escolha o ano.
    2. Escolha o tipo de lugar (todos, só bons, só travados).
    3. Veja o mapa, os gráficos e teste o frete.
    """
)

anos = sorted(df["ano"].unique())
ano_sel = st.sidebar.selectbox("Ano", anos, index=len(anos) - 1)

tipos_hub = ["Todos"] + sorted(df["tipo_hub"].unique())
tipo_hub_sel = st.sidebar.selectbox("Tipo de lugar", tipos_hub)

df_filt = df[df["ano"] == ano_sel].copy()
if tipo_hub_sel != "Todos":
    df_filt = df_filt[df_filt["tipo_hub"] == tipo_hub_sel]

if df_filt.empty:
    st.warning("Nenhum município encontrado com os filtros atuais.")
    st.stop()

# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumo",
    "Mapa de Minas",
    "Onde Vale a Pena",
    "E se o frete mudar?",
    "Detalhes do município"
])

# =========================
# TAB 1 – RESUMO
# =========================

with tab1:
    st.subheader("Resumo rápido")

    col1, col2, col3, col4 = st.columns(4)

    total_vres = df_filt["Vres_Total_Ton"].sum()
    total_riqueza = df_filt["Riqueza_Perdida_RS"].sum()
    hubs_nat = (df_filt["tipo_hub"] == "Hub natural").sum()
    hubs_trav = (df_filt["tipo_hub"] == "Hub travado").sum()

    col1.metric("Biomassa total (t)", f"{total_vres:,.0f}".replace(",", "."))
    col2.metric("Dinheiro hoje queimado (R$)", f"{total_riqueza:,.0f}".replace(",", "."))
    col3.metric("Lugares bons (hub natural)", hubs_nat)
    col4.metric("Lugares travados", hubs_trav)

    st.markdown("#### Top 10 lugares com mais dinheiro sendo queimado hoje")
    df_resumo = (
        df_filt[["municipio", "Vres_Total_Ton", "Riqueza_Perdida_RS", "tipo_hub"]]
        .sort_values(by="Riqueza_Perdida_RS", ascending=False)
        .head(10)
        .rename(columns={
            "municipio": "Município",
            "Vres_Total_Ton": "Biomassa (t)",
            "Riqueza_Perdida_RS": "Dinheiro queimado (R$)",
            "tipo_hub": "Tipo de lugar",
        })
    )
    st.dataframe(df_resumo)

# =========================
# TAB 2 – MAPA DE MINAS
# =========================

with tab2:
    st.subheader("Mapa de oportunidades em Minas Gerais")

    st.markdown(
        """
        - **Amarelo** = lugar bom para ganhar dinheiro com biomassa.  
        - **Vermelho** = muito resíduo, mas o frete deixa o lugar travado.  
        - **Azul** = oportunidades menores / nicho.
        """
    )

    df_mapa = df_filt.dropna(subset=["lat", "lon"]).copy()

    if df_mapa.empty:
        st.info("Ainda não há coordenadas cadastradas para os municípios filtrados.")
    else:
        color_map = {
            "Hub natural": "#F5F749",        # amarelo (bom)
            "Hub travado": "#FA441A",        # vermelho/laranja (problema)
            "Oportunidade nicho": "#03254D", # azul (oportunidade menor)
            "Baixa prioridade": "#BECCCC",   # cinza
        }

        fig_map = px.scatter_mapbox(
            df_mapa,
            lat="lat",
            lon="lon",
            size="Vres_Total_Ton",
            color="tipo_hub",
            color_discrete_map=color_map,
            hover_name="municipio",
            hover_data={
                "Vres_Total_Ton": True,
                "Lucro_Liquido_Estimado": True,
                "lat": False,
                "lon": False,
            },
            zoom=5,
            center={"lat": -18.5, "lon": -44.0},
            height=500,
            title="Onde estão os resíduos e onde o negócio fecha"
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)

# =========================
# TAB 3 – ONDE VALE A PENA
# =========================

with tab3:
    st.subheader("Onde o frete deixa o negócio bom ou ruim")

    st.markdown(
        """
        Cada bolinha é um município:

        - Eixo **X**: distância até a indústria.  
        - Eixo **Y**: lucro estimado com biomassa.  
        - Quanto **maior a bolinha**, mais biomassa existe ali.
        """
    )

    color_map = {
        "Hub natural": "#F5F749",
        "Hub travado": "#FA441A",
        "Oportunidade nicho": "#03254D",
        "Baixa prioridade": "#BECCCC",
    }

    fig_lucro = px.scatter(
        df_filt,
        x="Distancia_Km",
        y="Lucro_Liquido_Estimado",
        size="Vres_Total_Ton",
        color="tipo_hub",
        color_discrete_map=color_map,
        hover_name="municipio",
        labels={
            "Distancia_Km": "Distância até a indústria (km)",
            "Lucro_Liquido_Estimado": "Lucro estimado (R$)",
            "tipo_hub": "Tipo de lugar"
        },
        title="Distância x Lucro: quem ganha dinheiro e quem fica no prejuízo"
    )
    st.plotly_chart(fig_lucro, use_container_width=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("#### Top 10 lugares que já dão lucro")
        df_nat = (
            df_filt[df_filt["Lucro_Liquido_Estimado"] > 0][
                ["municipio", "Polo_Destino", "Distancia_Km",
                 "Lucro_Liquido_Estimado", "tipo_hub"]
            ]
            .sort_values(by="Lucro_Liquido_Estimado", ascending=False)
            .head(10)
            .rename(columns={
                "municipio": "Município",
                "Polo_Destino": "Indústria mais próxima",
                "Distancia_Km": "Distância (km)",
                "Lucro_Liquido_Estimado": "Lucro (R$)",
                "tipo_hub": "Tipo de lugar",
            })
        )
        st.dataframe(df_nat)

    with col_neg:
        st.markdown("#### Lugares com muita biomassa, mas prejuízo (frete pesa demais)")
        vres_mediana = df_filt["Vres_Total_Ton"].median()
        df_garg = df_filt[
            (df_filt["Vres_Total_Ton"] >= vres_mediana) &
            (df_filt["Lucro_Liquido_Estimado"] < 0)
        ]
        df_garg = df_garg[
            ["municipio", "Vres_Total_Ton", "Polo_Destino",
             "Distancia_Km", "Lucro_Liquido_Estimado"]
        ].sort_values(by="Lucro_Liquido_Estimado")

        df_garg = df_garg.rename(columns={
            "municipio": "Município",
            "Vres_Total_Ton": "Biomassa (t)",
            "Polo_Destino": "Indústria mais próxima",
            "Distancia_Km": "Distância (km)",
            "Lucro_Liquido_Estimado": "Lucro (R$)",
        })
        st.dataframe(df_garg)

# =========================
# TAB 4 – E SE O FRETE MUDAR?
# =========================

with tab4:
    st.subheader("E se o frete ficasse mais barato?")

    st.markdown(
        """
        Arraste a barrinha e veja **quantos municípios passam a dar lucro**.

        - Frete caro = muitas bolinhas vermelhas.  
        - Frete barato = mais bolinhas viram amarelas (lucro).
        """
    )

    custo_frete_novo = st.slider(
        "Custo de frete simulado (R$/km/tonelada)",
        min_value=0.50,
        max_value=2.50,
        value=1.20,
        step=0.10
    )

    df_cenario_base = df_filt[["municipio", "Vres_Total_Ton", "Distancia_Km"]].copy()

    margem_unitaria = 600.0 - 150.0  # mesma lógica do script (600 - 150)
    df_cenario = df_cenario_base.copy()
    df_cenario["Riqueza_Perdida_RS"] = df_cenario["Vres_Total_Ton"] * margem_unitaria
    df_cenario["Custo_Frete_RS"] = (
        df_cenario["Distancia_Km"] * custo_frete_novo * df_cenario["Vres_Total_Ton"]
    )
    df_cenario["Lucro_Liquido_Estimado"] = (
        df_cenario["Riqueza_Perdida_RS"] - df_cenario["Custo_Frete_RS"]
    )

    num_pos = (df_cenario["Lucro_Liquido_Estimado"] > 0).sum()
    st.markdown(f"**Municípios com lucro positivo neste cenário: {num_pos}**")

    df_cen_show = (
        df_cenario[["municipio", "Lucro_Liquido_Estimado"]]
        .sort_values(by="Lucro_Liquido_Estimado", ascending=False)
        .head(15)
        .rename(columns={
            "municipio": "Município",
            "Lucro_Liquido_Estimado": "Lucro (R$)",
        })
    )
    st.dataframe(df_cen_show)

# =========================
# TAB 5 – DETALHES DO MUNICÍPIO
# =========================

with tab5:
    st.subheader("Detalhes do município")

    mun_sel = st.selectbox("Escolha um município", sorted(df_filt["municipio"].unique()))
    df_mun = df_filt[df_filt["municipio"] == mun_sel].iloc[0]

    st.markdown(f"### {mun_sel}")
    st.write(f"Tipo de lugar: **{df_mun['tipo_hub']}**")
    st.write(f"Indústria mais próxima: **{df_mun['Polo_Destino']}** ({df_mun['Distancia_Km']:.1f} km)")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Biomassa (t)", f"{df_mun['Vres_Total_Ton']:,.0f}".replace(",", "."))
    col_b.metric("Dinheiro queimado hoje (R$)", f"{df_mun['Riqueza_Perdida_RS']:,.0f}".replace(",", "."))
=======
from pathlib import Path
LOGO_PATH = Path("Logo.jpg")  # nome do arquivo da logo

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================
# CONFIG BÁSICA
# =========================

st.set_page_config(
    page_title="Do Fogo ao Lucro",
    layout="wide"
)

# Coordenadas aproximadas dos municípios chave de MG (lat, lon)
coords_municipios = {
    "João Pinheiro": (-17.74, -46.17),
    "Itamarandiba": (-17.85, -42.85),
    "Curvelo": (-18.75, -44.43),
    "Buritizeiro": (-17.35, -44.96),
    "Três Marias": (-18.20, -45.23),
    "Unaí": (-16.35, -46.90),
    "Paracatu": (-17.22, -46.87),
    "Uberaba": (-19.74, -47.93),
    "Patos de Minas": (-18.58, -46.52),
    "Perdizes": (-19.35, -47.29),
    "Itabira": (-19.62, -43.23),
    "Diamantina": (-18.24, -43.60),
    "Governador Valadares": (-18.85, -41.94),
    "Montes Claros": (-16.73, -43.86),
}

# =========================
# CARREGAR DADOS
# =========================

@st.cache_data
def load_data():
    df = pd.read_csv("dados_pam_pevs_dashboard_mg.csv")

    # Adiciona colunas de latitude e longitude com base no nome do município
    def get_lat(m):
        return coords_municipios.get(m, (None, None))[0]

    def get_lon(m):
        return coords_municipios.get(m, (None, None))[1]

    df["lat"] = df["municipio"].apply(get_lat)
    df["lon"] = df["municipio"].apply(get_lon)

    return df

df = load_data()

# =========================
# HEADER (LOGO + TÍTULO)
# =========================

col_logo, col_title = st.columns([1, 3])
with col_logo:
    if LOGO_PATH.exists():
         st.sidebar.image(str(LOGO_PATH), use_container_width=True)

with col_title:
    st.title("Do Fogo ao Lucro")
    st.markdown(
        "Veja **onde a biomassa hoje vira fumaça** e onde ela pode virar **dinheiro e energia limpa**."
    )

st.markdown(
    """
    Cada bolinha no mapa é um município de Minas Gerais.

    - **Biomassa** = resíduo de lavoura e floresta.
    - **Dinheiro jogado fora** = valor do que é queimado.
    - **Lucro** = quando vale a pena levar esse resíduo até a indústria.
    """
)

# =========================
# SIDEBAR – FILTROS GERAIS
# =========================

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)

st.sidebar.markdown("### Como usar")
st.sidebar.markdown(
    """
    1. Escolha o ano.
    2. Escolha o tipo de lugar (todos, só bons, só travados).
    3. Veja o mapa, os gráficos e teste o frete.
    """
)

anos = sorted(df["ano"].unique())
ano_sel = st.sidebar.selectbox("Ano", anos, index=len(anos) - 1)

tipos_hub = ["Todos"] + sorted(df["tipo_hub"].unique())
tipo_hub_sel = st.sidebar.selectbox("Tipo de lugar", tipos_hub)

df_filt = df[df["ano"] == ano_sel].copy()
if tipo_hub_sel != "Todos":
    df_filt = df_filt[df_filt["tipo_hub"] == tipo_hub_sel]

if df_filt.empty:
    st.warning("Nenhum município encontrado com os filtros atuais.")
    st.stop()

# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumo",
    "Mapa de Minas",
    "Onde Vale a Pena",
    "E se o frete mudar?",
    "Detalhes do município"
])

# =========================
# TAB 1 – RESUMO
# =========================

with tab1:
    st.subheader("Resumo rápido")

    col1, col2, col3, col4 = st.columns(4)

    total_vres = df_filt["Vres_Total_Ton"].sum()
    total_riqueza = df_filt["Riqueza_Perdida_RS"].sum()
    hubs_nat = (df_filt["tipo_hub"] == "Hub natural").sum()
    hubs_trav = (df_filt["tipo_hub"] == "Hub travado").sum()

    col1.metric("Biomassa total (t)", f"{total_vres:,.0f}".replace(",", "."))
    col2.metric("Dinheiro hoje queimado (R$)", f"{total_riqueza:,.0f}".replace(",", "."))
    col3.metric("Lugares bons (hub natural)", hubs_nat)
    col4.metric("Lugares travados", hubs_trav)

    st.markdown("#### Top 10 lugares com mais dinheiro sendo queimado hoje")
    df_resumo = (
        df_filt[["municipio", "Vres_Total_Ton", "Riqueza_Perdida_RS", "tipo_hub"]]
        .sort_values(by="Riqueza_Perdida_RS", ascending=False)
        .head(10)
        .rename(columns={
            "municipio": "Município",
            "Vres_Total_Ton": "Biomassa (t)",
            "Riqueza_Perdida_RS": "Dinheiro queimado (R$)",
            "tipo_hub": "Tipo de lugar",
        })
    )
    st.dataframe(df_resumo)

# =========================
# TAB 2 – MAPA DE MINAS
# =========================

with tab2:
    st.subheader("Mapa de oportunidades em Minas Gerais")

    st.markdown(
        """
        - **Amarelo** = lugar bom para ganhar dinheiro com biomassa.  
        - **Vermelho** = muito resíduo, mas o frete deixa o lugar travado.  
        - **Azul** = oportunidades menores / nicho.
        """
    )

    df_mapa = df_filt.dropna(subset=["lat", "lon"]).copy()

    if df_mapa.empty:
        st.info("Ainda não há coordenadas cadastradas para os municípios filtrados.")
    else:
        color_map = {
            "Hub natural": "#F5F749",        # amarelo (bom)
            "Hub travado": "#FA441A",        # vermelho/laranja (problema)
            "Oportunidade nicho": "#03254D", # azul (oportunidade menor)
            "Baixa prioridade": "#BECCCC",   # cinza
        }

        fig_map = px.scatter_mapbox(
            df_mapa,
            lat="lat",
            lon="lon",
            size="Vres_Total_Ton",
            color="tipo_hub",
            color_discrete_map=color_map,
            hover_name="municipio",
            hover_data={
                "Vres_Total_Ton": True,
                "Lucro_Liquido_Estimado": True,
                "lat": False,
                "lon": False,
            },
            zoom=5,
            center={"lat": -18.5, "lon": -44.0},
            height=500,
            title="Onde estão os resíduos e onde o negócio fecha"
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)

# =========================
# TAB 3 – ONDE VALE A PENA
# =========================

with tab3:
    st.subheader("Onde o frete deixa o negócio bom ou ruim")

    st.markdown(
        """
        Cada bolinha é um município:

        - Eixo **X**: distância até a indústria.  
        - Eixo **Y**: lucro estimado com biomassa.  
        - Quanto **maior a bolinha**, mais biomassa existe ali.
        """
    )

    color_map = {
        "Hub natural": "#F5F749",
        "Hub travado": "#FA441A",
        "Oportunidade nicho": "#03254D",
        "Baixa prioridade": "#BECCCC",
    }

    fig_lucro = px.scatter(
        df_filt,
        x="Distancia_Km",
        y="Lucro_Liquido_Estimado",
        size="Vres_Total_Ton",
        color="tipo_hub",
        color_discrete_map=color_map,
        hover_name="municipio",
        labels={
            "Distancia_Km": "Distância até a indústria (km)",
            "Lucro_Liquido_Estimado": "Lucro estimado (R$)",
            "tipo_hub": "Tipo de lugar"
        },
        title="Distância x Lucro: quem ganha dinheiro e quem fica no prejuízo"
    )
    st.plotly_chart(fig_lucro, use_container_width=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("#### Top 10 lugares que já dão lucro")
        df_nat = (
            df_filt[df_filt["Lucro_Liquido_Estimado"] > 0][
                ["municipio", "Polo_Destino", "Distancia_Km",
                 "Lucro_Liquido_Estimado", "tipo_hub"]
            ]
            .sort_values(by="Lucro_Liquido_Estimado", ascending=False)
            .head(10)
            .rename(columns={
                "municipio": "Município",
                "Polo_Destino": "Indústria mais próxima",
                "Distancia_Km": "Distância (km)",
                "Lucro_Liquido_Estimado": "Lucro (R$)",
                "tipo_hub": "Tipo de lugar",
            })
        )
        st.dataframe(df_nat)

    with col_neg:
        st.markdown("#### Lugares com muita biomassa, mas prejuízo (frete pesa demais)")
        vres_mediana = df_filt["Vres_Total_Ton"].median()
        df_garg = df_filt[
            (df_filt["Vres_Total_Ton"] >= vres_mediana) &
            (df_filt["Lucro_Liquido_Estimado"] < 0)
        ]
        df_garg = df_garg[
            ["municipio", "Vres_Total_Ton", "Polo_Destino",
             "Distancia_Km", "Lucro_Liquido_Estimado"]
        ].sort_values(by="Lucro_Liquido_Estimado")

        df_garg = df_garg.rename(columns={
            "municipio": "Município",
            "Vres_Total_Ton": "Biomassa (t)",
            "Polo_Destino": "Indústria mais próxima",
            "Distancia_Km": "Distância (km)",
            "Lucro_Liquido_Estimado": "Lucro (R$)",
        })
        st.dataframe(df_garg)

# =========================
# TAB 4 – E SE O FRETE MUDAR?
# =========================

with tab4:
    st.subheader("E se o frete ficasse mais barato?")

    st.markdown(
        """
        Arraste a barrinha e veja **quantos municípios passam a dar lucro**.

        - Frete caro = muitas bolinhas vermelhas.  
        - Frete barato = mais bolinhas viram amarelas (lucro).
        """
    )

    custo_frete_novo = st.slider(
        "Custo de frete simulado (R$/km/tonelada)",
        min_value=0.50,
        max_value=2.50,
        value=1.20,
        step=0.10
    )

    df_cenario_base = df_filt[["municipio", "Vres_Total_Ton", "Distancia_Km"]].copy()

    margem_unitaria = 600.0 - 150.0  # mesma lógica do script (600 - 150)
    df_cenario = df_cenario_base.copy()
    df_cenario["Riqueza_Perdida_RS"] = df_cenario["Vres_Total_Ton"] * margem_unitaria
    df_cenario["Custo_Frete_RS"] = (
        df_cenario["Distancia_Km"] * custo_frete_novo * df_cenario["Vres_Total_Ton"]
    )
    df_cenario["Lucro_Liquido_Estimado"] = (
        df_cenario["Riqueza_Perdida_RS"] - df_cenario["Custo_Frete_RS"]
    )

    num_pos = (df_cenario["Lucro_Liquido_Estimado"] > 0).sum()
    st.markdown(f"**Municípios com lucro positivo neste cenário: {num_pos}**")

    df_cen_show = (
        df_cenario[["municipio", "Lucro_Liquido_Estimado"]]
        .sort_values(by="Lucro_Liquido_Estimado", ascending=False)
        .head(15)
        .rename(columns={
            "municipio": "Município",
            "Lucro_Liquido_Estimado": "Lucro (R$)",
        })
    )
    st.dataframe(df_cen_show)

# =========================
# TAB 5 – DETALHES DO MUNICÍPIO
# =========================

with tab5:
    st.subheader("Detalhes do município")

    mun_sel = st.selectbox("Escolha um município", sorted(df_filt["municipio"].unique()))
    df_mun = df_filt[df_filt["municipio"] == mun_sel].iloc[0]

    st.markdown(f"### {mun_sel}")
    st.write(f"Tipo de lugar: **{df_mun['tipo_hub']}**")
    st.write(f"Indústria mais próxima: **{df_mun['Polo_Destino']}** ({df_mun['Distancia_Km']:.1f} km)")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Biomassa (t)", f"{df_mun['Vres_Total_Ton']:,.0f}".replace(",", "."))
    col_b.metric("Dinheiro queimado hoje (R$)", f"{df_mun['Riqueza_Perdida_RS']:,.0f}".replace(",", "."))
>>>>>>> f4cbdb7 (Primeiro commit do app PID)
    col_c.metric("Lucro estimado (R$)", f"{df_mun['Lucro_Liquido_Estimado']:,.0f}".replace(",", "."))
