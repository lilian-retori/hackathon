from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import numpy as np

# =========================
# CONFIG BÁSICA
# =========================

st.set_page_config(
    page_title="Do Fogo ao Lucro - PID 3.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "dados_pam_pevs_dashboard_mg.csv"
IND_PATH = BASE_DIR / "industrias_biomassa_mg.csv"

possible_logos = [
    BASE_DIR / "Logo.png",
    BASE_DIR / "Logo.jpg",
    BASE_DIR / "logo.png",
    BASE_DIR / "logo.jpg",
]
LOGO_PATH = next((p for p in possible_logos if p.exists()), None)

# =========================
# ESTILO CUSTOMIZADO
# =========================

st.markdown("""
<style>
.stApp {
    background-color: #03254D;
    color: #FFFFFF;
}

section[data-testid="stSidebar"] {
    background-color: #08366A;
    padding-top: 1rem;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
    background: transparent !important;
}

h1, h2, h3, h4, h5, h6, p, li, label {
    color: #FFFFFF;
}

div[data-testid="stMetric"],
div[data-testid="stDataFrame"],
div[data-testid="stPlotlyChart"],
div[data-testid="stTable"] {
    background-color: #08366A;
    border-radius: 12px;
    padding: 0.5rem;
}

div[data-testid="column"]:nth-of-type(3) div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1FAF8B 0%, #17856A 100%);
    border: 1px solid rgba(255,255,255,0.15);
}

button[data-baseweb="tab"] {
    color: #FFFFFF !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 3px solid #1FAF8B !important;
    color: #1FAF8B !important;
}

.stButton > button {
    background-color: #1FAF8B;
    color: #FFFFFF;
    border-radius: 8px;
    border: none;
}

.stButton > button:hover {
    background-color: #17856A;
    color: #FFFFFF;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    color: #03254D !important;
    border-radius: 8px;
}

div[data-baseweb="select"] * {
    color: #03254D !important;
}

ul[role="listbox"] {
    background-color: #FFFFFF !important;
}

ul[role="listbox"] li {
    background-color: #FFFFFF !important;
    color: #03254D !important;
}

ul[role="listbox"] li:hover {
    background-color: #EAF0F6 !important;
    color: #03254D !important;
}

div[data-testid="stExpander"] details {
    background-color: rgba(255,255,255,0.04);
    border-radius: 10px;
    padding: 0.35rem 0.5rem;
    border: 1px solid rgba(255,255,255,0.08);
}
</style>
""", unsafe_allow_html=True)

# =========================
# FUNÇÕES AUXILIARES
# =========================

def fmt_num(valor):
    return f"{valor:,.0f}".replace(",", ".")

def fmt_mi(valor):
    if abs(valor) >= 1_000_000:
        return f"R$ {valor/1_000_000:.1f} Mi".replace(".", ",")
    return f"R$ {valor:,.0f}".replace(",", ".")

def classifica_distancia(km):
    if km <= 80:
        return "Perto"
    elif km <= 150:
        return "Médio"
    return "Longe"

def distancia_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return r * c

# =========================
# COORDENADAS MUNICIPAIS
# =========================

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
    if not DATA_PATH.exists():
        st.error("Arquivo de dados não encontrado: dados_pam_pevs_dashboard_mg.csv")
        st.stop()
    df = pd.read_csv(DATA_PATH)
    df["lat"] = df["municipio"].map(lambda m: coords_municipios.get(m, (None, None))[0])
    df["lon"] = df["municipio"].map(lambda m: coords_municipios.get(m, (None, None))[1])
    return df

@st.cache_data
def preparar_dados_industriais():
    if not IND_PATH.exists():
        st.error("Arquivo industrial não encontrado: industrias_biomassa_mg.csv")
        st.stop()
    df_ind = pd.read_csv(IND_PATH)
    df_ind["demanda_mensal_ton"] = pd.to_numeric(df_ind["demanda_mensal_ton"], errors="coerce").fillna(0)
    df_ind["lat"] = pd.to_numeric(df_ind["lat"], errors="coerce")
    df_ind["lon"] = pd.to_numeric(df_ind["lon"], errors="coerce")
    return df_ind

df = load_data()
df_industrias = preparar_dados_industriais()

# =========================
# SIDEBAR
# =========================

st.sidebar.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

if LOGO_PATH:
    st.sidebar.image(str(LOGO_PATH), width=220)
else:
    st.sidebar.warning("Logo não encontrada.")

st.sidebar.markdown("## Filtros")

with st.sidebar.expander("Como usar", expanded=False):
    st.markdown("""
1. Escolha o ano.
2. Escolha o tipo de lugar.
3. Veja o mapa, os gráficos e simule o frete.
""")

anos = sorted(df["ano"].dropna().unique())
ano_sel = st.sidebar.selectbox("Ano", anos, index=len(anos) - 1)

tipos_hub = ["Todos"] + sorted(df["tipo_hub"].dropna().unique())
tipo_hub_sel = st.sidebar.selectbox("Tipo de lugar", tipos_hub)

residue_type_options = ["Lenhoso", "Agro_Seco", "Agro_Umido"]
residue_type_sel = st.sidebar.selectbox(
    "Tipo de resíduo para análise",
    residue_type_options,
    index=0,
    help="Lenhoso = para siderúrgicas | Agro_Seco = para cimenteiras"
)
st.session_state["residue_type_selector"] = residue_type_sel

df_filt = df[df["ano"] == ano_sel].copy()
if tipo_hub_sel != "Todos":
    df_filt = df_filt[df_filt["tipo_hub"] == tipo_hub_sel]

if "Probabilidade_Atratividade" in df_filt.columns:
    df_filt["Radar_Biomassa"] = df_filt["Vres_Total_Ton"] * df_filt["Probabilidade_Atratividade"].fillna(0)
else:
    df_filt["Radar_Biomassa"] = df_filt["Vres_Total_Ton"]

if df_filt.empty:
    st.warning("Nenhum município encontrado com os filtros atuais.")
    st.stop()

# =========================
# HEADER
# =========================

st.title("Do Fogo ao Lucro – Mapa de Oportunidades em MG")
st.markdown("Veja **onde a biomassa hoje vira fumaça** e onde ela pode virar **dinheiro e energia limpa**.")

st.markdown("""
Cada bolinha no mapa é um município de Minas Gerais.

- **Biomassa** = resíduo de lavoura e floresta.
- **Dinheiro jogado fora** = valor do que é queimado.
- **Lucro** = quando vale a pena levar esse resíduo até a indústria.
""")

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
# TAB 1
# =========================

with tab1:
    st.subheader("Resumo rápido")
    col1, col2, col3, col4 = st.columns(4)

    total_vres = df_filt["Vres_Total_Ton"].sum()
    total_riqueza = df_filt["Riqueza_Perdida_RS"].sum()
    hubs_nat = (df_filt["tipo_hub"] == "Hub natural").sum()

    col1.metric("Biomassa total (t)", fmt_num(total_vres))
    col2.metric("Dinheiro queimado", fmt_mi(total_riqueza))
    col3.metric("Radar Biomassa total (t ponderadas)", fmt_num(df_filt["Radar_Biomassa"].sum()))
    col4.metric("Lugares bons", hubs_nat)

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
    st.dataframe(df_resumo, use_container_width=True)

# =========================
# TAB 2 – MAPA DE RADAR BIOMASSA
# =========================

with tab2:
    st.subheader("Mapa de Oportunidades: Radar Biomassa")

    df_mun = df_filt.copy()
    selected_type = st.session_state.get("residue_type_selector", "Lenhoso")

    mun_supply_col = f"Vres_{selected_type}_Mensal"
    if mun_supply_col not in df_mun.columns:
        df_mun[mun_supply_col] = 0.0

    df_mun_supply = df_mun[
        (df_mun[mun_supply_col] > 0) &
        (df_mun["lat"].notna()) &
        (df_mun["lon"].notna())
    ].copy()

    df_ind_demand = df_industrias[
        (df_industrias["tipo_residuo_exigido"] == selected_type) &
        (df_industrias["demanda_mensal_ton"] > 0) &
        (df_industrias["lat"].notna()) &
        (df_industrias["lon"].notna())
    ].copy()

    fig_map = go.Figure()

    # ===== LINHAS DE MATCH =====
    INCLINACAO_PROB = 0.1
    RAIO_MEDIO_KM = 200.0
    LIMIAR_PROB_VIABILIDADE = 0.4

    total_matched_volume = 0
    match_details = []

    for _, mun in df_mun_supply.iterrows():
        for _, ind in df_ind_demand.iterrows():
            dist_km = distancia_km(mun["lat"], mun["lon"], ind["lat"], ind["lon"])
            prob = 1 / (1 + np.exp(INCLINACAO_PROB * (dist_km - RAIO_MEDIO_KM)))

            if prob >= LIMIAR_PROB_VIABILIDADE:
                possible_match = min(mun[mun_supply_col], ind["demanda_mensal_ton"]) * prob

                if possible_match > 0.1:
                    total_matched_volume += possible_match

                    match_details.append({
                        "municipio": mun["municipio"],
                        "industria": ind["nome_empre"],
                        "dist_km": round(dist_km, 1),
                        "prob": round(prob, 3),
                        "match_t_mes": round(possible_match, 1),
                        "mun_lat": mun["lat"],
                        "mun_lon": mun["lon"],
                        "ind_lat": ind["lat"],
                        "ind_lon": ind["lon"]
                    })

                    fig_map.add_trace(go.Scattermapbox(
                        lon=[mun["lon"], ind["lon"]],
                        lat=[mun["lat"], ind["lat"]],
                        mode="lines",
                        line=dict(
                            width=1.2 + 2.8 * prob,
                            color="rgba(255,255,255,0.22)"
                        ),
                        hoverinfo="skip",
                        showlegend=False
                    ))

    # ===== MUNICÍPIOS =====
    if not df_mun_supply.empty:
        fig_map.add_trace(go.Scattermapbox(
            lat=df_mun_supply["lat"],
            lon=df_mun_supply["lon"],
            mode="markers",
            marker=dict(
                size=np.clip(df_mun_supply[mun_supply_col] / 1500, 10, 32),
                color="#F5D547",
                opacity=0.88
            ),
            text=df_mun_supply["municipio"],
            customdata=np.stack([df_mun_supply[mun_supply_col]], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Oferta disponível: %{customdata[0]:,.0f} t/mês"
                "<extra></extra>"
            ),
            name="Oferta municipal"
        ))

    # ===== INDÚSTRIAS =====
    if not df_ind_demand.empty:
        fig_map.add_trace(go.Scattermapbox(
            lat=df_ind_demand["lat"],
            lon=df_ind_demand["lon"],
            mode="markers",
            marker=dict(
                size=np.clip(df_ind_demand["demanda_mensal_ton"] / 2500, 11, 30),
                color="#27D3A2",
                opacity=0.95,
                symbol="square"
            ),
            text=df_ind_demand["nome_empre"],
            customdata=np.stack([df_ind_demand["demanda_mensal_ton"], df_ind_demand["cidade"]], axis=-1),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Cidade: %{customdata[1]}<br>"
                "Demanda: %{customdata[0]:,.0f} t/mês"
                "<extra></extra>"
            ),
            name="Demanda industrial"
        ))

    fig_map.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=-19.5, lon=-43.5),
            zoom=4.7
        ),
        paper_bgcolor="#03254D",
        plot_bgcolor="#03254D",
        font=dict(color="white"),
        title=dict(
            text=f"Radar Biomassa Territorial ({selected_type})",
            font=dict(color="white", size=20),
            x=0.01,
            xanchor="left"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white"),
            orientation="h",
            yanchor="bottom",
            y=0.01,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        height=720
    )

    st.plotly_chart(fig_map, use_container_width=True)

    col1, col2, col3 = st.columns(3)

    total_mun_supply = df_mun_supply[mun_supply_col].sum() if not df_mun_supply.empty else 0
    total_ind_demand = df_ind_demand["demanda_mensal_ton"].sum() if not df_ind_demand.empty else 0

    col1.metric(
        f"Oferta municipal ({selected_type})",
        f"{total_mun_supply:,.0f} t/mês".replace(",", ".")
    )
    col2.metric(
        f"Demanda industrial ({selected_type})",
        f"{total_ind_demand:,.0f} t/mês".replace(",", ".")
    )
    col3.metric(
        "Match esperado",
        f"{total_matched_volume:,.0f} t/mês".replace(",", "."),
        delta=f"{(total_matched_volume / max(total_ind_demand, 1) * 100):.1f}% da demanda"
    )

    st.markdown("""
- **Amarelo** = biomassa ofertada por município.  
- **Verde** = demanda industrial real.  
- **Linhas claras** = conexões com viabilidade probabilística mínima.
""")

    with st.expander("Ver matches viáveis"):
        if match_details:
            df_match = pd.DataFrame(match_details).rename(columns={
                "municipio": "Município",
                "industria": "Indústria",
                "dist_km": "Distância (km)",
                "prob": "Probabilidade",
                "match_t_mes": "Match esperado (t/mês)"
            })
            st.dataframe(
                df_match.sort_values("Match esperado (t/mês)", ascending=False),
                use_container_width=True,
                height=320
            )
        else:
            st.info("Nenhum match viável encontrado para os filtros atuais.")
# =========================
# TAB 3 – RADAR BIOMASSA ESTRATÉGICA
# =========================

with tab3:
    st.subheader("Radar Biomassa Estratégica")

    st.markdown("""
Cada bolinha mostra a força territorial da biomassa:

- **Eixo X**: distância até o destino industrial.
- **Eixo Y**: Radar Biomassa = biomassa total × atratividade logística.
- **Bolha maior**: mais biomassa disponível.
""")

    color_map = {
        "Hub natural": "#1FAF8B",
        "Hub travado": "#FA441A",
        "Oportunidade nicho": "#4DA8FF",
        "Baixa prioridade": "#BECCCC",
    }

    fig_radar = px.scatter(
        df_filt,
        x="Distancia_Km",
        y="Radar_Biomassa",
        size="Vres_Total_Ton",
        color="tipo_hub",
        color_discrete_map=color_map,
        hover_name="municipio",
        labels={
            "Distancia_Km": "Distância até a indústria (km)",
            "Radar_Biomassa": "Radar Biomassa",
            "tipo_hub": "Tipo de lugar"
        },
        title="Força Territorial da Biomassa"
    )

    fig_radar.update_traces(
        marker=dict(line=dict(width=0.6, color="rgba(255,255,255,0.35)"))
    )

    fig_radar.update_layout(
        paper_bgcolor="#03254D",
        plot_bgcolor="#08366A",
        font=dict(color="white"),
        title=dict(
            text="Força Territorial da Biomassa",
            font=dict(color="white", size=20),
            x=0.01,
            xanchor="left"
        ),
        xaxis=dict(
            title_font=dict(color="white"),
            tickfont=dict(color="white"),
            gridcolor="rgba(255,255,255,0.08)"
        ),
        yaxis=dict(
            title_font=dict(color="white"),
            tickfont=dict(color="white"),
            gridcolor="rgba(255,255,255,0.08)"
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("#### Top 10 maiores forças de biomassa")
        df_top_radar = (
            df_filt[["municipio", "Radar_Biomassa", "Vres_Total_Ton", "tipo_hub", "Polo_Destino", "Distancia_Km"]]
            .sort_values(by="Radar_Biomassa", ascending=False)
            .head(10)
            .rename(columns={
                "municipio": "Município",
                "Radar_Biomassa": "Radar Biomassa",
                "Vres_Total_Ton": "Biomassa total (t)",
                "tipo_hub": "Tipo de lugar",
                "Polo_Destino": "Indústria mais próxima",
                "Distancia_Km": "Distância (km)"
            })
        )
        st.dataframe(df_top_radar, use_container_width=True)

    with col_neg:
        st.markdown("#### Biomassa grande, tração baixa")
        vres_mediana = df_filt["Vres_Total_Ton"].median()
        radar_mediana = df_filt["Radar_Biomassa"].median()

        df_garg = df_filt[
            (df_filt["Vres_Total_Ton"] >= vres_mediana) &
            (df_filt["Radar_Biomassa"] < radar_mediana)
        ][["municipio", "Vres_Total_Ton", "Radar_Biomassa", "Polo_Destino", "Distancia_Km"]].sort_values(
            by="Radar_Biomassa"
        )

        df_garg = df_garg.rename(columns={
            "municipio": "Município",
            "Vres_Total_Ton": "Biomassa (t)",
            "Radar_Biomassa": "Radar Biomassa",
            "Polo_Destino": "Indústria mais próxima",
            "Distancia_Km": "Distância (km)",
        })

        st.dataframe(df_garg, use_container_width=True)

# =========================
# TAB 4
# =========================

with tab4:
    st.subheader("E se o frete ficasse mais barato?")

    custo_frete_novo = st.slider(
        "Custo de frete simulado (R$/km/tonelada)",
        min_value=0.50,
        max_value=2.50,
        value=1.20,
        step=0.10
    )

    df_cenario = df_filt[["municipio", "Vres_Total_Ton", "Distancia_Km"]].copy()
    margem_unitaria = 600.0 - 150.0
    df_cenario["Riqueza_Perdida_RS"] = df_cenario["Vres_Total_Ton"] * margem_unitaria
    df_cenario["Custo_Frete_RS"] = df_cenario["Distancia_Km"] * custo_frete_novo * df_cenario["Vres_Total_Ton"]
    df_cenario["Lucro_Liquido_Estimado"] = df_cenario["Riqueza_Perdida_RS"] - df_cenario["Custo_Frete_RS"]

    num_pos = (df_cenario["Lucro_Liquido_Estimado"] > 0).sum()
    st.markdown(f"### Municípios com lucro positivo neste cenário: {num_pos}")

    df_cen_show = (
        df_cenario[["municipio", "Lucro_Liquido_Estimado"]]
        .sort_values(by="Lucro_Liquido_Estimado", ascending=False)
        .head(15)
        .rename(columns={
            "municipio": "Município",
            "Lucro_Liquido_Estimado": "Lucro (R$)",
        })
    )
    st.dataframe(df_cen_show, use_container_width=True)

# =========================
# TAB 5
# =========================

with tab5:
    st.subheader("Detalhes do município")

    mun_sel = st.selectbox("Escolha um município", sorted(df_filt["municipio"].unique()))
    df_mun = df_filt[df_filt["municipio"] == mun_sel].iloc[0]

    st.markdown(f"""
    <div style="
        background-color:#08366A;
        padding:18px;
        border-radius:12px;
        margin-bottom:16px;
        border:1px solid rgba(255,255,255,0.08);
    ">
        <h3 style="margin:0; color:white;">{mun_sel}</h3>
        <p style="margin:8px 0 0 0; color:white;"><b>Tipo de lugar:</b> {df_mun['tipo_hub']}</p>
        <p style="margin:4px 0 0 0; color:white;"><b>Indústria mais próxima:</b> {df_mun['Polo_Destino']} ({df_mun['Distancia_Km']:.1f} km)</p>
        <p style="margin:4px 0 0 0; color:white;"><b>Classificação logística:</b> {classifica_distancia(df_mun['Distancia_Km'])}</p>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Biomassa (t)", fmt_num(df_mun["Vres_Total_Ton"]))
    col_b.metric("Dinheiro queimado hoje", fmt_mi(df_mun["Riqueza_Perdida_RS"]))
    col_c.metric("Lucro estimado", fmt_mi(df_mun["Lucro_Liquido_Estimado"]))
