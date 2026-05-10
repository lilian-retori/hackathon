from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# =========================
# FUNÇÃO PARA PREPARAR DADOS INDUSTRIAIS (ADICIONE AQUI)
# =========================
def preparar_dados_industriais():
    """
    Converte os dados industriais da sua mensagem inicial em DataFrame
    com: nome_empre, cidade, industria, consumo_ton_ano, lat, lon, tipo_residuo_exigido, demanda_mensal_ton
    """
    import pandas as pd  # Garante que o pandas esteja disponível aqui
    
    # DADOS DE CIMENTO (da sua primeira tabela)
    cement_data = [
        ["EMPRESA DE CIMENTOS LIZ S.A", "VESPASIANO", "Cimento", 131888.63, -43.92484785, -19.68546445],
        ["INTERCEMENT BRASIL S.A.", "IJACI", "Cimento", 125965.52, -44.94068823, -21.19281404],
        ["CSN CIMENTOS BRASIL S.A.", "PEDRO LEOPOLDO", "Cimento", 104328.31, -44.05710332, -19.60800416],
        ["VOTORANTIM CIMENTOS S.A.", "ITAÚ DE MINAS", "Cimento", 89713.37, -46.76315471, -20.76110507],
        ["COMPANHIA NACIONAL DE CIMENTO - CNC", "SETE LAGOAS", "Cimento", 85021.06, -44.27433569, -19.51343785],
        ["CSN CIMENTOS BRASIL S.A.", "BARROSO", "Cimento", 130862.98, -43.9860617, -21.1816831],
        ["CSN CIMENTOS S.A.", "ARCOS", "Cimento", 70417.63, -45.57895294, -20.31299859],
        ["CSN CIMENTOS BRASIL S.A.", "MONTES CLOROS", "Cimento", 50986.93, -43.89133274, -16.67246921],
        ["INTERCEMENT BRASIL S.A.", "SANTANA DO PARAÍSO", "Cimento", 12894.91, -42.47959725, -19.47643347],
        ["CSN CIMENTOS BRASIL S.A.", "BARBACENA", "Cimento", 709.22, -43.7684493, -21.21278304],
        ["INTERCEMENT BRASIL S.A.", "PEDRO LEOPOLDO", "Cimento", 664.33, -44.0278412, -19.62747641]
    ]
    
    # DADOS DE SIDERURGIA (da sua segunda tabela)
    steel_data = [
        ["USINAS SIDERURGICAS DE MINAS GERAIS S/A. USIMINAS", "IPATINGA", "Siderurgia", 858601.8833, -42.55697038, -19.49367598],
        ["GERDAU ACOMINAS S/A", "OURO BRANCO", "Siderurgia", 533871.0147, -43.74237377, -20.54547116],
        ["APERAM INOX AMERICA DO SUL S.A.", "TIMÓTEO", "Siderurgia", 403131.6518, -42.64340843, -19.53140653],
        ["VALLOUREC SOLUCOES TUBULARES DO BRASIL S.A.", "JECEABA", "Siderurgia", 331233.6585, -43.97277466, -20.57795847],
        ["ARCELORMITTAL BRASIL S.A.", "JUIZ DE FORA", "Siderurgia", 310532.6138, -43.46263449, -21.62762464],
        ["ARCELORMITTAL BRASIL S.A.", "JOÃO MONLEVADE", "Siderurgia", 309656.3824, -43.13013906, -19.83023777],
        ["GERDAU ACOS LONGOS S.A.", "DIVINÓPOLIS", "Siderurgia", 87530.5166, -44.87941954, -20.15452264],
        ["VALLOUREC SOLUCOES TUBULARES DO BRASIL S.A.", "BELO HORIZONTE", "Siderurgia", 78070.51652, -44.01149263, -19.97010911],
        ["GERDAU ACOS LONGOS S.A.", "BARÃO DE COCAIS", "Siderurgia", 31655.35598, -43.47902631, -19.93711487]
    ]
    
    # Combine e crie DataFrame
    all_data = cement_data + steel_data
    cols = ["nome_empre", "cidade", "industria", "consumo_ton_ano", "lat", "lon"]
    df_industrias = pd.DataFrame(all_data, columns=cols)
    
    # Mapeia tipo de indústria para tipo de resíduo exigido (suposições técnicas razoáveis)
    df_industrias["tipo_residuo_exigido"] = df_industrias["industria"].map({
        "Cimento": "Agro_Seco",      # Casca de arroz, casca de café - seco, baixo teor de cinzas
        "Siderurgia": "Lenhoso"      # Lenha de eucalipto/pinus para carvão vegetal
    })
    
    # Converte consumo anual para mensal (para facilitar comparação com oferta municipal)
    df_industrias["demanda_mensal_ton"] = df_industrias["consumo_ton_ano"] / 12
    
    return df_industrias

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

/* Destaque visual extra para o 3º card (Lucro estimado) */
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

/* Expander da sidebar */
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

# =========================
# COORDENADAS
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

    def get_lat(municipio):
        return coords_municipios.get(municipio, (None, None))[0]

    def get_lon(municipio):
        return coords_municipios.get(municipio, (None, None))[1]

    df["lat"] = df["municipio"].apply(get_lat)
    df["lon"] = df["municipio"].apply(get_lon)

    return df

df = load_data()

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
# Seletor de tipo de resíduo para o mapa de match
residue_type_options = ["Lenhoso", "Agro_Seco", "Agro_Umido"]
residue_type_sel = st.sidebar.selectbox(
"Tipo de resíduo para análise",
residue_type_options,
index=0, # Padrão: Lenhoso
help="Lenhoso = para siderúrgicas | Agro_Seco = para cimenteiras"
)
st.session_state["residue_type_selector"] = residue_type_sel

df_filt = df[df["ano"] == ano_sel].copy()
if tipo_hub_sel != "Todos":
    df_filt = df_filt[df_filt["tipo_hub"] == tipo_hub_sel]

if df_filt.empty:
    st.warning("Nenhum município encontrado com os filtros atuais.")
    st.stop()

# =========================
# HEADER
# =========================

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
    total_lucro = df_filt["Lucro_Liquido_Estimado"].sum()
    hubs_nat = (df_filt["tipo_hub"] == "Hub natural").sum()

    col1.metric("Biomassa total (t)", fmt_num(total_vres))
    col2.metric("Dinheiro queimado", fmt_mi(total_riqueza))
    col3.metric("Lucro estimado", fmt_mi(total_lucro))
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
# TAB 2 – MAPA (COM MATCH REAL INDUSTRIA-MUNICÍPIO)
# =========================
with tab2:

    st.subheader("Mapa de Oportunidades: Match Indústria - Resíduo")

    # ===== PREPARAR DADOS (MUNICÍPIOS + INDUSTRIAS) =====
    # 1. Carregar dados municipais (seu df_filt já tem Vres_*_Mensal)
    df_mun = df_filt.copy()
    
    # 2. Preparar dados industriais (da função que adicionamos acima)
    df_ind = preparar_dados_industriais()
    
    # 3. Selecionar tipo de resíduo para análise (do session_state definido na sidebar)
    selected_type = st.session_state.get("residue_type_selector", "Lenhoso")
    
    # 4. Filtrar municípios com oferta >0 do tipo selecionado
    mun_supply_col = f"Vres_{selected_type}_Mensal"
    # Verifica se a coluna existe; se não, cria com zeros (fallback seguro)
    if mun_supply_col not in df_mun.columns:
        df_mun[mun_supply_col] = 0.0
    df_mun_supply = df_mun[df_mun[mun_supply_col] > 0].copy()
    
    # 5. Filtrar indústrias com demanda >0 do tipo selecionado
    df_ind_demand = df_ind[
        (df_ind["tipo_residuo_exigido"] == selected_type) & 
        (df_ind["demanda_mensal_ton"] > 0)
    ].copy()
    
    # 6. Definir distâncias máximas por tipo de indústria (km)
    max_haul_dist = {
        "Lenhoso": 250,   # Siderurgia aceita maiores distâncias para carvão vegetal
        "Agro_Seco": 150, # Cimento tem raio menor para resíduos agrícolas secos
        "Agro_Umido": 100 # Biomass-power tem raio menor (menos comum no seu dados)
    }
    max_dist = max_haul_dist.get(selected_type, 150)
    
    # ===== CRIAR MAPA BASE =====
    fig_map = px.scatter_mapbox(
        lat=[],
        lon=[],
        zoom=4.7,
        center={"lat": -19.5, "lon": -43.5},
        height=700
    )
    
    # ===== ADICIONAR OVERLAY DAS ESTRADAS (SE EXISTIR) =====
    try:
        with open("estradas_mg.png", "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode()
        fig_map.update_layout(
            mapbox={
                "layers": [{
                    "below": "traces",
                    "source": {
                        "type": "image",
                        "url": f"data:image/png;base64,{img_b64}",
                        "coordinates": [
                            [-48.5, -14.0], [-39.5, -14.0],
                            [-39.5, -22.0], [-48.5, -22.0]
                        ]
                    }
                }]
            }
        )
    except FileNotFoundError:
        pass  # Continua sem overlay se não houver imagem
    
    # ===== ADICIONAR MUNICÍPIOS (OFERTA) =====
    if not df_mun_supply.empty:
        fig_map.add_scattermapbox(
            lat=df_mun_supply["lat"],
            lon=df_mun_supply["lon"],
            mode="markers",
            marker=dict(
                size=df_mun_supply[mun_supply_col] / 200,  # Ajuste divisor para visualização
                color="#F5F749",  # Amarelo (oferta disponível)
                opacity=0.8
            ),
            text=df_mun_supply["municipio"],
            hoverinfo="text",
            hovertemplate=
            "<b>%{text}</b><br>" +
            f"{selected_type} disponível: %{{marker.size:,.0f}} t/mês<extra></extra>",
            customdata=df_mun_supply[mun_supply_col],
            name="Oferta Municipal"
        )
    
    # ===== ADICIONAR INDÚSTRIAS (DEMANDA) =====
    if not df_ind_demand.empty:
        fig_map.add_scattermapbox(
            lat=df_ind_demand["lat"],
            lon=df_ind_demand["lon"],
            mode="markers",
            marker=dict(
                size=df_ind_demand["demanda_mensal_ton"] / 150,  # Divisor diferente para indústrias
                color="#1FAF8B",  # Verde (demanda industrial)
                symbol="square",
                opacity=0.9
            ),
            text=df_ind_demand["nome_empre"],
            hoverinfo="text",
            hovertemplate=
            "<b>%{text}</b><br>" +
            f"Demanda de {selected_type}: %{{marker.size:,.0f}} t/mês<extra></extra>",
            customdata=df_ind_demand["demanda_mensal_ton"],
            name="Demanda Industrial"
        )
    
    # ===== ADICIONAR LINHAS DE MATCH VIÁVEL =====
    match_lines = []
    total_matched_volume = 0
    
    for _, mun in df_mun_supply.iterrows():
        mun_lat, mun_lon = mun["lat"], mun["lon"]
        mun_supply_val = mun[mun_supply_col]
        
        for _, ind in df_ind_demand.iterrows():
            ind_lat, ind_lon = ind["lat"], ind["lon"]
            ind_demand_val = ind["demanda_mensal_ton"]
            
            # Calcular distância geodésica
            dist_km = geodesic((mun_lat, mun_lon), (ind_lat, ind_lon)).km
            
            # Verificar se está dentro do raio máximo permitido
            if dist_km <= max_dist:
                # Volume que poderia ser trocado = min(oferta municipal, demanda industrial)
                possible_match = min(mun_supply_val, ind_demand_val)
                
                if possible_match > 0.1:  # Só mostra matches significativos
                    match_lines.append(dict(
                        type="line",
                        lon0=mun_lon, lat0=mun_lat,
                        lon1=ind_lon, lat1=ind_lat,
                        line=dict(width=1, color="rgba(255,255,255,0.3)"),
                    ))
                    total_matched_volume += possible_match
    
    # Adicionar linhas de match ao mapa
    if match_lines:
        fig_map.update_layout(shapes=match_lines)
    
    # ===== CONFIGURAR LAYOUT FINAL =====
    fig_map.update_layout(
        mapbox_style="open-street-map",
        paper_bgcolor="#03254D",
        plot_bgcolor="#03254D",
        font=dict(color="white"),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(255,255,255,0.2)",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        title=f"Match Real: Oferta Municipal × Demanda Industrial ({selected_type})"
    )
    
    st.plotly_chart(fig_map, use_container_width=True)
    
    # ===== MÉTRICAS DE MATCH =====
    col1, col2, col3 = st.columns(3)
    
    total_mun_supply = df_mun_supply[mun_supply_col].sum() if not df_mun_supply.empty else 0
    total_ind_demand = df_ind_demand["demanda_mensal_ton"].sum() if not df_ind_demand.empty else 0
    
    col1.metric(
        f"Oferta Municipal Mensal ({selected_type})",
        f"{total_mun_supply:,.0f} t/mês".replace(",", ".")
    )
    col2.metric(
        f"Demanda Industrial Mensal ({selected_type})",
        f"{total_ind_demand:,.0f} t/mês".replace(",", ".")
    )
    col3.metric(
        "Volume Match Viável Mensal",
        f"{total_matched_volume:,.0f} t/mês".replace(",", "."),
        delta=f"{(total_matched_volume / max(total_ind_demand, 1) * 100):.1f}% da demanda atendida"
    )
    
    # ===== LEGENDA E EXPLICAÇÃO =====
    st.markdown(
        """
        - **🟡 Círculos Amarelos**: Municípios com oferta disponível do tipo selecionado  
          (tamanho = toneladas/mês disponíveis)  
        - **🟢 Quadrados Verdes**: Indústrias com demanda do tipo selecionado  
          (tamanho = toneladas/mês demandadas; quadrado = indústria)  
        - **⚪ Linhas Brancas Finas**: Conexões viáveis onde:  
          • Tipo de resíduo corresponde  
          • Distância ≤ máximo aceitável pela indústria  
          • Volume trocado = min(oferta municipal, demanda industrial)  
        """
    )
    
    # ===== TABELA DE MATCHES DETALHADOS (OPCIONAL MAS ÚTIL) =====
    with st.expander("Ver detalhes dos matches viáveis"):
        if match_lines and not df_mun_supply.empty and not df_ind_demand.empty:
            match_details = []
            for _, mun in df_mun_supply.iterrows():
                for _, ind in df_ind_demand.iterrows():
                    dist_km = geodesic((mun["lat"], mun["lon"]), (ind["lat"], ind["lon"])).km
                    if dist_km <= max_haul_dist.get(selected_type, 150):
                        possible = min(mun[mun_supply_col], ind["demanda_mensal_ton"])
                        if possible > 0.1:
                            match_details.append({
                                "Município": mun["municipio"],
                                "Indústria": ind["nome_empre"],
                                "Distância (km)": round(dist_km, 1),
                                "Volume Match (t/mês)": round(possible, 1),
                                "Oferta Município (t/mês)": round(mun[mun_supply_col], 1),
                                "Demanda Indústria (t/mês)": round(ind["demanda_mensal_ton"], 1)
                            })
            
            if match_details:
                df_match = pd.DataFrame(match_details)
                st.dataframe(
                    df_match.sort_values("Volume Match (t/mês)", ascending=False),
                    use_container_width=True,
                    height=300
                )
            else:
                st.info("Nenhum match viável encontrado para os filtros atuais.")
        else:
            st.info("Selecione um tipo de resíduo na sidebar para ver matches.")

    # Instrução para o usuário
    st.info(
        "💡 **Dica**: Use o seletor de 'Tipo de resíduo' na sidebar para alternar entre análise de lenhoso (para siderúrgicas) e agro seco (para cimenteiras). "
        "O mapa mostrará apenas onde há correspondência real de tipo E volume."
    )
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
        "Hub natural": "#1FAF8B",
        "Hub travado": "#FA441A",
        "Oportunidade nicho": "#4DA8FF",
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

    fig_lucro.update_layout(
        paper_bgcolor="#03254D",
        plot_bgcolor="#08366A",
        font=dict(color="white"),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )

    st.plotly_chart(fig_lucro, use_container_width=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("#### Top 10 lugares que já dão lucro")
        df_nat = (
            df_filt[df_filt["Lucro_Liquido_Estimado"] > 0][
                ["municipio", "Polo_Destino", "Distancia_Km", "Lucro_Liquido_Estimado", "tipo_hub"]
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
        st.dataframe(df_nat, use_container_width=True)

    with col_neg:
        st.markdown("#### Lugares com muita biomassa, mas prejuízo")
        vres_mediana = df_filt["Vres_Total_Ton"].median()
        df_garg = df_filt[
            (df_filt["Vres_Total_Ton"] >= vres_mediana) &
            (df_filt["Lucro_Liquido_Estimado"] < 0)
        ][
            ["municipio", "Vres_Total_Ton", "Polo_Destino", "Distancia_Km", "Lucro_Liquido_Estimado"]
        ].sort_values(by="Lucro_Liquido_Estimado")

        df_garg = df_garg.rename(columns={
            "municipio": "Município",
            "Vres_Total_Ton": "Biomassa (t)",
            "Polo_Destino": "Indústria mais próxima",
            "Distancia_Km": "Distância (km)",
            "Lucro_Liquido_Estimado": "Lucro (R$)",
        })

        st.dataframe(df_garg, use_container_width=True)

# =========================
# TAB 4 – E SE O FRETE MUDAR?
# =========================

with tab4:
    st.subheader("E se o frete ficasse mais barato?")

    st.markdown(
        """
Arraste a barra e veja **quantos municípios passam a dar lucro**.

- Frete caro = mais municípios travados.  
- Frete barato = mais municípios com lucro positivo.
"""
    )

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
    df_cenario["Custo_Frete_RS"] = (
        df_cenario["Distancia_Km"] * custo_frete_novo * df_cenario["Vres_Total_Ton"]
    )
    df_cenario["Lucro_Liquido_Estimado"] = (
        df_cenario["Riqueza_Perdida_RS"] - df_cenario["Custo_Frete_RS"]
    )

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
# TAB 5 – DETALHES DO MUNICÍPIO
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
