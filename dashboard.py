"""
Dashboard interactivo – Elecciones Colombia 2026
Ejecutar: .venv/bin/streamlit run dashboard.py
"""

import json
import unicodedata
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Análisis Electoral – Primera Vuelta Colombia 2026",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilos – tema oscuro editorial
st.markdown("""
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:;
               style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
               font-src 'self' https://fonts.gstatic.com data:;
               img-src 'self' data: blob:;
               connect-src 'self' wss: ws:;
               frame-ancestors 'none';">
<meta http-equiv="X-Content-Type-Options" content="nosniff">
<meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ─── Base app ───────────────────────────────────────────────── */
body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0A0A0A !important;
    color: #F0EDE8 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}

/* ─── Títulos ────────────────────────────────────────────────── */
h1, h2 {
    font-family: Georgia, serif !important;
    color: #F0EDE8 !important;
    font-weight: 400 !important;
    letter-spacing: 0.02em !important;
    border-bottom: 1px solid #2A2A2A !important;
    padding-bottom: 10px !important;
}
h3, h4 {
    font-family: 'IBM Plex Sans', sans-serif !important;
    text-transform: uppercase !important;
    letter-spacing: 0.15em !important;
    font-size: 0.72rem !important;
    color: #C8A96E !important;
    font-weight: 500 !important;
}

/* ─── Métricas ────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #111111 !important;
    border-left: 3px solid #C8A96E !important;
    padding: 14px 18px !important;
    border-radius: 2px !important;
}
[data-testid="stMetricLabel"] {
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    font-size: 0.68rem !important;
    color: #9A9A90 !important;
}
[data-testid="stMetricValue"] {
    font-family: 'IBM Plex Mono', monospace !important;
    color: #F0EDE8 !important;
    font-size: 1.7rem !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
}
[data-testid="stMetricDelta"] svg {
    display: none !important;
}

/* ─── Caption / info ─────────────────────────────────────────── */
.stCaption, [data-testid="stCaptionContainer"] {
    color: #9A9A90 !important;
    font-style: italic !important;
    font-size: 0.78rem !important;
}
.stAlert {
    background-color: #111111 !important;
    border: 1px solid #2A2A2A !important;
    border-left: 3px solid #C8A96E !important;
    border-radius: 2px !important;
    color: #F0EDE8 !important;
}

/* ─── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0D0D0D !important;
    border-right: 1px solid #1E1E1E !important;
}

/* ─── Selectbox / widgets ────────────────────────────────────── */
.stSelectbox > div > div,
.stSlider > div,
.stRadio > div {
    background: #111111 !important;
    border-color: #2A2A2A !important;
    border-radius: 2px !important;
    color: #F0EDE8 !important;
}

/* ─── Dataframe / tables ─────────────────────────────────────── */
[data-testid="stDataFrame"] {
    background: #111111 !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 2px !important;
}

/* ─── Divisores ──────────────────────────────────────────────── */
hr {
    border-color: #2A2A2A !important;
    margin: 36px 0 !important;
}

/* ─── Barra de título fija ───────────────────────────────────── */
#page-title-bar {
    position: fixed;
    top: 3.25rem;
    left: 0;
    right: 0;
    z-index: 999992;
    background-color: #0A0A0A !important;
    backdrop-filter: none !important;
    text-align: center;
    padding: 6px 16px;
    font-size: 1.05rem;
    font-weight: 400;
    font-family: Georgia, serif;
    color: #C8A96E;
    letter-spacing: 0.08em;
    border-bottom: 1px solid #2A2A2A;
    line-height: 1.4;
}

/* ─── Pestañas fijas ─────────────────────────────────────────── */
div[data-testid="stTabs"] div[role="tablist"] {
    position: fixed !important;
    top: 5.7rem !important;
    left: 0 !important;
    right: 0 !important;
    z-index: 999990 !important;
    background-color: #0A0A0A !important;
    backdrop-filter: none !important;
    padding: 4px 16px !important;
    border-bottom: 1px solid #2A2A2A !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.5) !important;
    overflow-x: auto !important;
    white-space: nowrap !important;
}
div[data-testid="stTabs"] button[role="tab"] {
    color: #9A9A90 !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #C8A96E !important;
    border-bottom-color: #C8A96E !important;
}

/* ─── Contenido de pestañas ──────────────────────────────────── */
div[data-testid="stTabsContent"] {
    padding-top: 175px !important;
    margin-top: 0 !important;
}
div[data-testid="stTabsContent"] h1,
div[data-testid="stTabsContent"] h2,
div[data-testid="stTabsContent"] h3 {
    position: relative;
    z-index: 1;
    background-color: #0A0A0A !important;
    padding-top: 8px !important;
    padding-bottom: 4px !important;
    margin-top: 0 !important;
}

/* ─── Mobile ─────────────────────────────────────────────────── */
@media (max-width: 768px) {

    /* Título fijo: justo debajo del chrome de Streamlit en móvil */
    #page-title-bar {
        top: 3.0rem;
        font-size: 0.82rem;
        padding: 4px 10px;
        letter-spacing: 0.04em;
    }

    /* Pestañas: debajo del título */
    div[data-testid="stTabs"] div[role="tablist"] {
        top: 5.2rem !important;
        padding: 2px 6px !important;
        font-size: 0.72rem !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        font-size: 0.7rem !important;
        padding: 6px 10px !important;
        min-width: 0 !important;
    }

    /* Contenido: reducir padding superior */
    div[data-testid="stTabsContent"] {
        padding-top: 148px !important;
    }
    div[data-testid="stTabsContent"] h1 {
        font-size: 1.2rem !important;
    }
    div[data-testid="stTabsContent"] h2 {
        font-size: 1rem !important;
    }

    /* Columnas: apilar en vertical */
    [data-testid="column"] {
        min-width: 100% !important;
        width: 100% !important;
    }
    [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
    }

    /* Métricas: valor más compacto */
    [data-testid="stMetricValue"] {
        font-size: 1.25rem !important;
    }
    [data-testid="stMetric"] {
        padding: 10px 12px !important;
    }

    /* Gráficos: ancho completo, sin desborde */
    .stPlotlyChart {
        width: 100% !important;
        overflow-x: hidden !important;
    }
    .stPlotlyChart > div {
        max-width: 100% !important;
    }

    /* Ocultar barra de herramientas de Plotly en móvil */
    .modebar { display: none !important; }

    /* Sliders y widgets más cómodos al tacto */
    .stSlider > div { padding: 8px 0 !important; }
    .stRadio > div > label { padding: 6px 0 !important; }

    /* Sidebar: ocultar automáticamente */
    [data-testid="stSidebar"][aria-expanded="false"] { display: none !important; }
}
</style>
<div id="page-title-bar">Análisis Electoral &ndash; Primera Vuelta Colombia 2026</div>
""", unsafe_allow_html=True)

# ── Constantes ────────────────────────────────────────────────────────────────
TOP_CANDS = [
    "ABELARDO DE LA ESPRIELLA",
    "IVÁN CEPEDA CASTRO",
    "PALOMA VALENCIA LASERNA",
    "SERGIO FAJARDO VALDERRAMA",
]

COLORS = {
    "ABELARDO DE LA ESPRIELLA":          "#1f77b4",
    "IVÁN CEPEDA CASTRO":                "#CC0000",
    "PALOMA VALENCIA LASERNA":           "#2ca02c",
    "SERGIO FAJARDO VALDERRAMA":         "#ff7f0e",
    "CLAUDIA LÓPEZ":                     "#9467bd",
    "RAÚL SANTIAGO BOTERO JARAMILLO":    "#8c564b",
    "ÓSCAR MAURICIO LIZCANO ARANGO":     "#e377c2",
    "MIGUEL URIBE LONDOÑO":              "#7f7f7f",
    "SONDRA MACOLLINS GARVIN PINTO":     "#bcbd22",
    "ROY LEONARDO BARRERAS MONTEALEGRE": "#17becf",
    "LUIS GILBERTO MURILLO URRUTIA":     "#aec7e8",
    "CARLOS EDUARDO CAICEDO OMAR":       "#ffbb78",
    "GUSTAVO MATAMOROS CAMACHO":         "#98df8a",
    "OTROS":                             "#aaaaaa",
}

# Colores para la columna `ganador` (valores cortos del CSV)
GANADOR_COLORS = {
    "ABELARDO": "#1f77b4",
    "CEPEDA":   "#CC0000",
}

# Registraduría dept_co (int) → DIVIPOLA 2-char code
REG_TO_DIVIPOLA = {
    1: "05", 3: "08", 5: "13", 7: "15", 9: "17",
    11: "19", 12: "20", 13: "23", 15: "25", 16: "11",
    17: "27", 19: "41", 21: "47", 23: "52", 24: "66",
    25: "54", 26: "63", 27: "68", 28: "70", 29: "73",
    31: "76", 40: "81", 44: "18", 46: "85", 48: "44",
    50: "94", 52: "50", 54: "95", 56: "88", 60: "91",
    64: "86", 68: "97", 72: "99",
}

# dept_nombre (nuestros datos) → DIVIPOLA 2-char code
DEPT_TO_DIVIPOLA = {
    "ANTIOQUIA": "05", "ATLANTICO": "08", "BOLIVAR": "13",
    "BOYACA": "15", "CALDAS": "17", "CAQUETA": "18",
    "CAUCA": "19", "CESAR": "20", "CORDOBA": "23",
    "CUNDINAMARCA": "25", "BOGOTA D.C.": "11", "CHOCO": "27",
    "HUILA": "41", "LA GUAJIRA": "44", "MAGDALENA": "47",
    "META": "50", "NARIÑO": "52", "NORTE DE SAN": "54",
    "QUINDIO": "63", "RISARALDA": "66", "SANTANDER": "68",
    "SUCRE": "70", "TOLIMA": "73", "VALLE": "76",
    "ARAUCA": "81", "CASANARE": "85", "PUTUMAYO": "86",
    "SAN ANDRES": "88", "AMAZONAS": "91", "GUAINIA": "94",
    "GUAVIARE": "95", "VAUPES": "97", "VICHADA": "99",
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s))
    return "".join(c for c in s if not unicodedata.combining(c)).upper().strip()


def build_geo_lookup(geo_munis: dict) -> dict:
    """(DIVIPOLA_dept, normalized_muni_name) → MPIO_CCNCT
    Stores multiple alternative keys per municipality to maximise match rate.
    """
    lookup: dict = {}
    ARTICLES = ("EL ", "LA ", "LOS ", "LAS ", "SAN ", "SANTA ", "SANTO ")

    def _add(dpto: str, raw: str, code: str) -> None:
        lookup.setdefault((dpto, raw), code)
        # Without leading article
        for art in ARTICLES:
            if raw.startswith(art):
                lookup.setdefault((dpto, raw[len(art):]), code)
                break
        # Without parenthetical / district suffixes
        stripped = raw.split(" (")[0].split(",")[0].strip()
        if stripped != raw:
            lookup.setdefault((dpto, stripped), code)
            for art in ARTICLES:
                if stripped.startswith(art):
                    lookup.setdefault((dpto, stripped[len(art):]), code)
                    break

    for feat in geo_munis["features"]:
        p = feat["properties"]
        code = p["MPIO_CCNCT"]
        dpto = p["DPTO_CCDGO"]
        _add(dpto, _norm(p["MPIO_CNMBR"]), code)

    return lookup


def _fix_colombia_geo(fig: go.Figure, height: int = 420) -> go.Figure:
    """Aplica bounds explícitos de Colombia y ajustes mobile-friendly a un choropleth."""
    fig.update_geos(
        visible=False,
        lataxis_range=[-4.5, 13.0],
        lonaxis_range=[-82.0, -66.5],
        projection_type="mercator",
    )
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        geo=dict(bgcolor="rgba(0,0,0,0)"),
        dragmode=False,
        autosize=True,
    )
    return fig


def group_otros(df: pd.DataFrame, col: str = "candidato_presidente") -> pd.DataFrame:
    df = df.copy()
    df[col] = df[col].where(df[col].isin(TOP_CANDS), "OTROS")
    return df


def add_trend(fig: go.Figure, x_data, y_data,
              color: str = "black", name: str = "Tendencia") -> None:
    x = np.asarray(x_data, dtype=float)
    y = np.asarray(y_data, dtype=float)
    valid = ~(np.isnan(x) | np.isnan(y))
    x, y = x[valid], y[valid]
    if len(x) < 5:
        return
    m, b = np.polyfit(x, y, 1)
    x_range = np.linspace(x.min(), x.max(), 200)
    fig.add_trace(go.Scatter(
        x=x_range, y=m * x_range + b,
        mode="lines", name=name,
        line=dict(color=color, width=2, dash="dash"),
        showlegend=True,
    ))


@st.cache_data
def load_data():
    df  = pd.read_csv("resultados/resultados_presidenciales_2026_municipios.csv")
    mun = pd.read_csv("resultados/municipios_analisis.csv")
    pre = pd.read_csv("resultados/prediccion_segunda_vuelta.csv")
    with open("resultados/colombia_depts.json", encoding="utf-8") as f:
        geo_depts = json.load(f)
    with open("resultados/colombia_munis.json", encoding="utf-8") as f:
        geo_munis = json.load(f)

    # DIVIPOLA dept code (para coropletas departamentales)
    mun["divipola_dept"] = mun["dept_co"].map(REG_TO_DIVIPOLA)
    df["divipola_dept"]  = df["dept_co"].map(REG_TO_DIVIPOLA)

    # DIVIPOLA municipality code via nombre normalizado (92 %+ cobertura)
    geo_lookup = build_geo_lookup(geo_munis)

    # Manual corrections: (reg_dept_co_int, _norm(reg_muni_nombre)) → DIVIPOLA_muni_code
    MANUAL_CODES: dict[tuple, str] = {
        # Antioquia (05)
        (1,  "ANTIOQUIA"):                   "05042",  # Santa Fe de Antioquia
        (1,  "BOLIVAR"):                     "05093",  # Ciudad Bolívar
        (1,  "DON MATIAS"):                  "05237",  # Donmatías
        (1,  "PUERTO NARE-LA MAGDALENA"):    "05585",
        (1,  "YONDO-CASABE"):                "05895",
        # Bogotá
        (16, "BOGOTA. D.C."):                "11001",
        (16, "BOGOTA, D.C."):                "11001",
        # Bolívar dept (13)
        (5,  "ARROYO HONDO"):                "13042",  # Arroyohondo
        (5,  "RIOVIEJO"):                    "13600",  # Río Viejo
        (5,  "TIQUISIO (PTO. RICO)"):        "13780",
        # Boyacá (15)
        (7,  "AQUITANIA (PUEBLOVIEJO)"):     "15022",
        (7,  "VILLA DE LEIVA"):              "15407",  # Villa de Leyva (spelling)
        # Cauca (19)
        (11, "LOPEZ (MICAY)"):               "19364",  # López de Micay
        (11, "PAEZ (BELALCAZAR)"):           "19517",
        (11, "PATIA (EL BORDO)"):            "19532",
        (11, "PURACE (COCONUCO)"):           "19573",
        (11, "SOTARA (PAISPAMBA)"):          "19698",  # Sotará - Paispamba
        # Chocó (27)
        (17, "ALTO BAUDO (PIE DE PATO)"):    "27025",
        (17, "ATRATO (YUTO)"):               "27050",
        (17, "BAHIA SOLANO (MUTIS)"):        "27073",
        (17, "BAJO BAUDO (PIZARRO)"):        "27075",
        (17, "BOJAYA (BELLAVISTA)"):         "27099",
        (17, "MEDIO ATRATO (BETE)"):         "27425",
        (17, "MEDIO BAUDO (PUERTO MELUK)"):  "27430",
        (17, "NUEVO BELEN DE BAJIRA"):       "27450",
        (17, "RIO QUITO (PAIMADO)"):         "27600",
        # Córdoba (23)
        (13, "COTORRA (BONGO)"):             "23162",
        (13, "LA APARTADA (FRONTERA)"):      "23350",
        # Cundinamarca (25)
        (15, "PARATEBUENO (LA NAGUAYA)"):    "25530",
        (15, "UBATE"):                       "25843",
        # Guainía (85 → REG 50)
        (50, "MORICHAL (MORICHAL NUEVO)"):   "94888",
        (50, "PANA PANA (CAMPO ALEGRE)"):    "94886",
        # Huila (41 → REG 19)
        (19, "LA ARGENTINA (PLATA VIEJA)"):  "41244",
        (19, "TESALIA (CARNICERIAS)"):       "41770",
        # Magdalena (47 → REG 21)
        (21, "ARIGUANI (EL DIFICIL)"):       "47053",
        (21, "ZONA BANANERA (SEVILLA)"):     "47980",
        # Meta (50 → REG 52)
        (52, "SAN MARTIN DE LOS LLANOS"):    "50689",  # San Martín
        (52, "VISTA HERMOSA"):               "50711",  # Vistahermosa
        # Nariño (52 → REG 23)
        (23, "ALBAN (SAN JOSE)"):            "52019",
        (23, "ARBOLEDA (BERRUECOS)"):        "52036",
        (23, "COLON (GENOVA)"):              "52203",
        (23, "CUASPUD (CARLOSAMA)"):         "52224",  # Cuaspud Carlosama
        (23, "LOS ANDES (SOTOMAYOR)"):       "52385",
        (23, "MAGUI (PAYAN)"):               "52399",
        (23, "MALLAMA (PIEDRANCHA)"):        "52405",
        (23, "ROBERTO PAYAN (SAN JOSE)"):    "52612",
        (23, "SANTA BARBARA (ISCUANDE)"):    "52696",
        (23, "SANTACRUZ (GUACHAVES)"):       "52699",
        (23, "TUMACO"):                      "52835",  # San Andrés de Tumaco
        # Norte de Santander (54 → REG 25)
        (25, "CUCUTA"):                      "54001",  # San José de Cúcuta
        # Putumayo (86 → REG 64)
        (64, "SAN MIGUEL (LA DORADA)"):      "86757",
        # Sucre (70 → REG 28)
        (28, "COLOSO (RICAURTE)"):           "70204",
        (28, "GALERAS (NUEVA GRANADA)"):     "70235",
        (28, "TOLU"):                        "70820",
        (28, "TOLUVIEJO"):                   "70823",
        # Tolima (73 → REG 29)
        (29, "ARMERO (GUAYABAL)"):           "73055",
        (29, "MARIQUITA"):                   "73411",  # San Sebastián de Mariquita
        # Valle (76 → REG 31)
        (31, "CALIMA (DARIEN)"):             "76126",
        # Vaupés (97 → REG 68)
        (68, "BUENOS AIRES (PACOA)"):        "97161",  # Pacoa
        (68, "MORICHAL (PAPUNAGUA)"):        "97511",
        # Amazonas (91 → REG 60)
        (60, "MIRITI PARANA"):               "91430",  # Mirití - Paraná
    }

    ARTICLES = ("EL ", "LA ", "LOS ", "LAS ")
    SUFFIXES = (" D.C.", " D.E.", " DISTRITO ESPECIAL", " DIST ESPECIAL")

    def get_divipola(dept_co, muni_nombre):
        dept_int = int(dept_co)
        dpto = REG_TO_DIVIPOLA.get(dept_int, "")
        if not dpto:
            return ""
        norm = _norm(muni_nombre)

        # 0. Manual correction table
        v = MANUAL_CODES.get((dept_int, norm), "")
        if v:
            return v

        # 1. Exact match
        v = geo_lookup.get((dpto, norm), "")
        if v:
            return v

        # 2. Without leading article
        for art in ARTICLES:
            if norm.startswith(art):
                v = geo_lookup.get((dpto, norm[len(art):]), "")
                if v:
                    return v

        # 3. Without trailing district suffix
        for suf in SUFFIXES:
            if norm.endswith(suf):
                v = geo_lookup.get((dpto, norm[: -len(suf)].strip()), "")
                if v:
                    return v

        # 4. Strip parenthetical (e.g. "TIQUISIO (PTO. RICO)" → "TIQUISIO")
        if " (" in norm:
            base = norm.split(" (")[0].strip()
            v = geo_lookup.get((dpto, base), "")
            if v:
                return v

        # 5. Strip hyphen suffix (e.g. "PUERTO NARE-LA MAGDALENA" → "PUERTO NARE")
        if "-" in norm:
            base = norm.split("-")[0].strip()
            v = geo_lookup.get((dpto, base), "")
            if v:
                return v

        # 6. Prefix match (first 14 chars) as last resort
        prefix = norm[:14]
        for (d, n), code in geo_lookup.items():
            if d == dpto and n.startswith(prefix):
                return code

        return ""

    mun["divipola_muni"] = mun.apply(
        lambda r: get_divipola(r["dept_co"], r["muni_nombre"]), axis=1
    )

    _unmatched = mun[mun["divipola_muni"] == ""][["dept_co", "dept_nombre", "muni_nombre"]]
    if not _unmatched.empty:
        import logging as _logging
        _logging.warning(f"[DIVIPOLA] {len(_unmatched)} municipios sin match:\n{_unmatched.to_string()}")

    # GeoJSON filtrado solo con Antioquia (más rápido y mejor zoom en ese mapa)
    geo_ant = {
        "type": "FeatureCollection",
        "features": [
            f for f in geo_munis["features"]
            if f["properties"]["DPTO_CCDGO"] == "05"
        ],
    }

    return df, mun, pre, geo_depts, geo_munis, geo_ant


df, mun, pre, geo_depts, geo_munis, geo_ant = load_data()

# ── Tema oscuro editorial (fijo) ──────────────────────────────────────────────
_PLOTLY_TPL = "plotly_dark"
_GEO_LAND   = "rgba(40,40,40,0.7)"
_GEO_OCEAN  = "rgba(10,20,35,0.7)"
_GEO_COAST  = "rgba(200,169,110,0.2)"

pio.templates["editorial_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111111",
        font=dict(family="IBM Plex Sans, sans-serif", color="#9A9A90", size=12),
        title=dict(font=dict(family="Georgia, serif", color="#F0EDE8", size=14)),
        xaxis=dict(
            gridcolor="#1E1E1E", showgrid=True,
            zeroline=False, showline=False,
            tickfont=dict(color="#9A9A90"),
        ),
        yaxis=dict(
            gridcolor="#1E1E1E", showgrid=True,
            zeroline=False, showline=False,
            tickfont=dict(color="#9A9A90"),
        ),
        legend=dict(
            bgcolor="rgba(17,17,17,0.8)",
            bordercolor="#2A2A2A", borderwidth=1,
            font=dict(color="#9A9A90"),
        ),
        hoverlabel=dict(
            bgcolor="#1A1A1A", font_color="#F0EDE8",
            bordercolor="#C8A96E",
        ),
        coloraxis=dict(colorbar=dict(
            tickfont=dict(color="#9A9A90"),
            title=dict(font=dict(color="#9A9A90")),
        )),
    )
)
pio.templates.default = "editorial_dark"
_PLOTLY_TPL = "editorial_dark"

# Separar voto interior (municipios) del exterior (consulados)
df_interior  = df[df["dept_nombre"] != "CONSULADOS"]
df_exterior  = df[df["dept_nombre"] == "CONSULADOS"]
mun_interior = mun[mun["dept_nombre"] != "CONSULADOS"]
mun_exterior = mun[mun["dept_nombre"] == "CONSULADOS"]


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("Elecciones 2026")
st.sidebar.markdown("**Filtros globales**")

dept_opts = (["Todos", "── Exterior (Consulados) ──"]
             + sorted(df_interior["dept_nombre"].unique().tolist()))
sel_dept = st.sidebar.selectbox("Departamento", dept_opts)

candidatos = ["Todos"] + sorted(df["candidato_presidente"].unique().tolist())
sel_cand   = st.sidebar.selectbox("Candidato", candidatos)

# Filtros aplicados
EXTERIOR_LABEL = "── Exterior (Consulados) ──"
if sel_dept == EXTERIOR_LABEL:
    df_f  = df_exterior.copy()
    mun_f = mun_exterior.copy()
elif sel_dept != "Todos":
    df_f  = df_interior[df_interior["dept_nombre"]   == sel_dept].copy()
    mun_f = mun_interior[mun_interior["dept_nombre"] == sel_dept].copy()
else:
    df_f  = df_interior.copy()   # "Todos" = solo interior; exterior tiene sección propia
    mun_f = mun_interior.copy()

if sel_cand != "Todos":
    df_f = df_f[df_f["candidato_presidente"] == sel_cand]

# Etiqueta de municipio con departamento cuando hay nombres duplicados entre deptos
_dup_munis = (
    mun_interior["muni_nombre"]
    .value_counts()
    .pipe(lambda s: s[s > 1].index)
    .tolist()
)

def _muni_label(row: pd.Series) -> str:
    if row["muni_nombre"] in _dup_munis:
        dept_abbr = row["dept_nombre"][:6]
        return f"{row['muni_nombre']} ({dept_abbr})"
    return row["muni_nombre"]

mun_f["muni_label"] = mun_f.apply(_muni_label, axis=1)

# Config para mapas estáticos (sin zoom ni pan, sin barra de herramientas)
_MAP_CFG = {"scrollZoom": False, "doubleClick": False, "displayModeBar": False}


# ── Callback para restablecer sliders de Proyección ───────────────────────────
def _reset_proyeccion() -> None:
    _dae  = {"PALOMA VALENCIA LASERNA": 72, "SERGIO FAJARDO VALDERRAMA": 22,
             "CLAUDIA LÓPEZ": 10, "OTROS": 35}
    _dic  = {"PALOMA VALENCIA LASERNA":  6, "SERGIO FAJARDO VALDERRAMA": 48,
             "CLAUDIA LÓPEZ": 58, "OTROS": 35}
    _dabs = {"PALOMA VALENCIA LASERNA": 22, "SERGIO FAJARDO VALDERRAMA": 30,
             "CLAUDIA LÓPEZ": 32, "OTROS": 30}
    for f in ["PALOMA VALENCIA LASERNA", "SERGIO FAJARDO VALDERRAMA", "CLAUDIA LÓPEZ", "OTROS"]:
        st.session_state[f"ae_{f}"]  = _dae[f]
        st.session_state[f"ic_{f}"]  = _dic[f]
        st.session_state[f"abs_{f}"] = _dabs[f]
    st.session_state["nuevos_total"]    = 1_500_000
    st.session_state["nuevos_abs_pct"]  = 15
    st.session_state["nuevos_ae_pct"]   = 48


# ── Tabs ──────────────────────────────────────────────────────────────────────
t_nacional, t_depts, t_antioquia, t_fuerza_ae, t_fuerza_paloma, t_coalicion, t_proyeccion = st.tabs([
    "Resultados Nacionales",
    "Por Departamento",
    "Solo Antioquia",
    "Fuerza Abelardo",
    "Fuerza Paloma",
    "Análisis Coalición",
    "Proyección 2ª Vuelta",
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 – RESULTADOS NACIONALES
# ═══════════════════════════════════════════════════════════════════════════════
with t_nacional:
    st.title("Resultados Primera Vuelta – Colombia 2026")

    # ── Cálculos ─────────────────────────────────────────────────────────────────
    nac_int = df_interior.drop_duplicates("muni_co")
    nac_ext = df_exterior.drop_duplicates("muni_co")  # una fila por consulado para sumar habilitados

    _hab_int    = int((nac_int["total_votantes"] + nac_int["total_abstencion"]).sum())
    _vot_int    = int(nac_int["total_votantes"].sum())
    _hab_ext    = int((nac_ext["total_votantes"] + nac_ext["total_abstencion"]).sum())
    _vot_ext    = int(nac_ext["total_votantes"].sum())
    _pct_ext    = _vot_ext / _hab_ext * 100 if _hab_ext > 0 else 0.0
    _consul_n   = df_exterior["muni_co"].nunique()

    # Total nacional = interior + exterior (coincide con el censo electoral oficial)
    _hab_nac    = _hab_int + _hab_ext
    _vot_nac    = _vot_int + _vot_ext
    _pct_part   = _vot_nac / _hab_nac * 100 if _hab_nac > 0 else 0.0

    # ── Métricas nacionales ───────────────────────────────────────────────────────
    st.caption("Total nacional (interior + exterior)")
    cn1, cn2, cn3 = st.columns(3)
    cn1.metric("Habilitados para votar", f"{_hab_nac:,}")
    cn2.metric("Votantes",              f"{_vot_nac:,}")
    cn3.metric("% Participación",       f"{_pct_part:.2f}%")

    # ── Métricas interior ────────────────────────────────────────────────────────
    st.caption("Municipios interiores")
    c4, c5, c6 = st.columns(3)
    c4.metric("Votos válidos",    f"{int(nac_int['votos_validos'].sum()):,}")
    c5.metric("Mesas escrutadas", f"{int(nac_int['mesas_escrutadas'].sum()):,} / {int(nac_int['mesas_total'].sum()):,}")
    c6.metric("Municipios",       f"{df_interior['muni_co'].nunique():,}")

    st.caption(
        f"El conteo oficial de municipios colombianos es 1.103, pero la Registraduría "
        f"opera con {df_interior['muni_co'].nunique():,} circunscripciones electorales: "
        "los 1.103 municipios más los corregimientos departamentales de Amazonas, Guainía "
        "y Vaupés (territorios sin categoría de municipio pero con votación independiente)."
    )

    # ── Métricas exterior ────────────────────────────────────────────────────────
    st.caption("Voto en el exterior (consulados)")
    cx1, cx2, cx3, cx4 = st.columns(4)
    cx1.metric("Habilitados exterior", f"{_hab_ext:,}")
    cx2.metric("Votantes exterior",    f"{_vot_ext:,}")
    cx3.metric("% Participación ext.", f"{_pct_ext:.2f}%")
    cx4.metric("Consulados",           f"{_consul_n:,}")

    st.divider()

    # Agrupación con OTROS
    agg_raw = (df_f.groupby("candidato_presidente", as_index=False)
                   .agg(votos=("votos_candidato", "sum"))
                   .sort_values("votos", ascending=False))

    # Separar top-4 + OTROS
    top4_rows  = agg_raw[agg_raw["candidato_presidente"].isin(TOP_CANDS)]
    otros_sum  = agg_raw[~agg_raw["candidato_presidente"].isin(TOP_CANDS)]["votos"].sum()
    otros_row  = pd.DataFrame([{"candidato_presidente": "OTROS", "votos": otros_sum}])
    agg        = (pd.concat([top4_rows, otros_row], ignore_index=True)
                    .sort_values("votos", ascending=False))
    agg["pct"] = agg["votos"] / agg["votos"].sum() * 100

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.subheader("Votos por candidato")
        fig = px.bar(
            agg, x="votos", y="candidato_presidente",
            orientation="h", color="candidato_presidente",
            color_discrete_map=COLORS,
            text=agg["votos"].apply(lambda v: f"{v:,.0f}"),
            labels={"votos": "Votos", "candidato_presidente": ""},
        )
        fig.update_traces(
            texttemplate="%{x:,.0f}",
            textposition="auto",
            cliponaxis=False,
        )
        fig.update_layout(
            showlegend=False, height=320,
            margin=dict(l=0, r=120, t=10, b=0),
            yaxis={"categoryorder": "total ascending"},
            xaxis={"autorange": True},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Distribución %")
        # Nombres cortos para que quepan dentro de las porciones
        agg_pie = agg.copy()
        SHORT = {
            "ABELARDO DE LA ESPRIELLA": "Abelardo",
            "IVÁN CEPEDA CASTRO":       "Cepeda",
            "PALOMA VALENCIA LASERNA":  "Paloma",
            "SERGIO FAJARDO VALDERRAMA":"Fajardo",
            "OTROS":                    "Otros",
        }
        agg_pie["nombre_corto"] = agg_pie["candidato_presidente"].map(
            lambda x: SHORT.get(x, x.split()[0])
        )
        _total_pie = agg_pie["votos"].sum()
        fig2 = px.pie(
            agg_pie, values="votos", names="nombre_corto",
            color="candidato_presidente", color_discrete_map=COLORS, hole=0.4,
        )
        # Rebanadas < 5 %: etiqueta vacía (visible solo en leyenda)
        fig2.update_traces(
            texttemplate="%{customdata}",
            textposition="outside",
            insidetextorientation="horizontal",
            pull=[0.05 if i == 0 else 0 for i in range(len(agg_pie))],
            customdata=[
                f"<b>{row['nombre_corto']}</b><br>{row['votos']/_total_pie*100:.1f}%"
                if row["votos"] / _total_pie >= 0.05 else ""
                for _, row in agg_pie.iterrows()
            ],
        )
        fig2.update_layout(
            showlegend=True,
            legend=dict(orientation="v", x=1.02, y=0.5),
            height=380,
            margin=dict(l=20, r=110, t=30, b=60),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Mapa: ganador por departamento ──────────────────────────────────────
    st.subheader("Ganador por departamento")

    # Calcular ganador por departamento (sobre todos los datos, sin filtro de candidato)
    df_map = df[df["candidato_presidente"].isin(TOP_CANDS)].copy()
    _dept_all = (
        df_map.groupby(["dept_nombre", "candidato_presidente"], as_index=False)
              .agg(votos=("votos_candidato", "sum"))
    )
    dept_winner = (
        _dept_all.sort_values("votos", ascending=False)
                 .drop_duplicates("dept_nombre")
    )
    # Añadir votos AE y IC para hover
    _ae_ic = (_dept_all[_dept_all["candidato_presidente"].isin(
                   ["ABELARDO DE LA ESPRIELLA", "IVÁN CEPEDA CASTRO"])]
              .pivot(index="dept_nombre", columns="candidato_presidente", values="votos")
              .rename(columns={"ABELARDO DE LA ESPRIELLA": "v_AE",
                               "IVÁN CEPEDA CASTRO": "v_IC"})
              .reset_index())
    _ae_ic.columns.name = None
    dept_winner = dept_winner.merge(_ae_ic, on="dept_nombre", how="left")
    dept_winner["divipola"] = dept_winner["dept_nombre"].map(DEPT_TO_DIVIPOLA)
    dept_winner = dept_winner.dropna(subset=["divipola"])

    fig_map = px.choropleth(
        dept_winner,
        geojson=geo_depts,
        locations="divipola",
        featureidkey="properties.DPTO",
        color="candidato_presidente",
        color_discrete_map=COLORS,
        hover_name="dept_nombre",
        hover_data={"v_AE": ":,", "v_IC": ":,", "divipola": False},
        labels={"candidato_presidente": "Ganador", "v_AE": "V. Abelardo", "v_IC": "V. Cepeda"},
        title="",
    )
    _fix_colombia_geo(fig_map, height=480)
    st.plotly_chart(fig_map, use_container_width=True, config=_MAP_CFG)

    # ── Tabla con dptos ganados ──────────────────────────────────────────────
    st.subheader("Tabla de resultados")

    # Departamentos ganados por candidato
    dptos_ganados = dept_winner.groupby("candidato_presidente")["dept_nombre"].count()

    tabla = agg[["candidato_presidente", "votos", "pct"]].copy()
    tabla.columns = ["Candidato", "Votos", "% Votos"]
    tabla["Dptos. ganados"] = tabla["Candidato"].map(dptos_ganados).fillna(0).astype(int)
    tabla = tabla.sort_values("Votos", ascending=False).reset_index(drop=True)
    tabla["Votos"]   = tabla["Votos"].apply(lambda v: f"{v:,.0f}")
    tabla["% Votos"] = tabla["% Votos"].apply(lambda v: f"{v:.2f}%")
    st.dataframe(tabla, use_container_width=True, hide_index=True)

    # ── Comparación histórica 2022 vs 2026 ──────────────────────────────────
    st.divider()
    st.subheader("Contexto histórico: primera vuelta 2022 vs 2026")
    st.caption("2022: datos oficiales Registraduría. Bloques definidos por alineación ideológica.")

    _cands_2022 = pd.DataFrame([
        {"Candidato": "Petro",          "pct": 40.32, "Bloque": "Izquierda"},
        {"Candidato": "Rodolfo",        "pct": 28.15, "Bloque": "Centro-der."},
        {"Candidato": "Fico Gutiérrez", "pct": 23.91, "Bloque": "Centro-der."},
        {"Candidato": "Fajardo",        "pct":  4.21, "Bloque": "Centro"},
        {"Candidato": "Otros",          "pct":  3.41, "Bloque": "Otros"},
    ])
    # Compute Otros 2026 from actual data (all candidates not in TOP_CANDS + votos blancos)
    _top4_votos_nac = df_interior.groupby("candidato_presidente")["votos_candidato"].sum()
    _validos_nac    = df_interior.drop_duplicates("muni_co")["votos_validos"].sum()
    _top4_sum_v     = sum(_top4_votos_nac.get(c, 0) for c in TOP_CANDS)
    _otros_2026_pct = round(100 - _top4_sum_v / _validos_nac * 100, 2)
    _cands_2026 = pd.DataFrame([
        {"Candidato": "Cepeda",   "pct": 40.90,           "Bloque": "Izquierda"},
        {"Candidato": "Abelardo", "pct": 43.74,           "Bloque": "Centro-der."},
        {"Candidato": "Valencia", "pct":  6.92,           "Bloque": "Centro-der."},
        {"Candidato": "Fajardo",  "pct":  4.26,           "Bloque": "Centro"},
        {"Candidato": "Otros",    "pct": _otros_2026_pct, "Bloque": "Otros"},
    ])
    _cands_2022["Año"] = "2022"
    _cands_2026["Año"] = "2026"
    _cands_hist = pd.concat([_cands_2022, _cands_2026], ignore_index=True)

    _COLOR_HIST = {
        "Petro":          "#CC0000",
        "Cepeda":         "#CC0000",
        "Fico Gutiérrez": "#1f77b4",
        "Rodolfo":        "#4a9ad4",
        "Abelardo":       "#1f77b4",
        "Valencia":       "#2ca02c",
        "Fajardo":        "#ff7f0e",
        "Otros":          "#aaaaaa",
    }

    _bloques_hist = (_cands_hist.groupby(["Año", "Bloque"], as_index=False)
                                .agg(pct=("pct", "sum")))

    _col_h1, _col_h2 = st.columns([3, 2])
    with _col_h1:
        fig_hist = px.bar(
            _cands_hist,
            x="Año", y="pct", color="Candidato",
            barmode="stack",
            color_discrete_map=_COLOR_HIST,
            text="pct",
            labels={"pct": "% Votos", "Año": ""},
            title="Distribución del voto por candidato",
        )
        fig_hist.update_traces(
            texttemplate="%{text:.1f}%", textposition="inside",
            insidetextanchor="middle",
        )
        fig_hist.update_layout(height=380, margin=dict(t=40, b=10))
        st.plotly_chart(fig_hist, use_container_width=True)

    with _col_h2:
        _COLOR_BLOQUES = {
            "Izquierda":  "#CC0000",
            "Centro-der.": "#1f77b4",
            "Centro":     "#ff7f0e",
            "Otros":      "#aaaaaa",
        }
        fig_bloq = px.bar(
            _bloques_hist,
            x="Año", y="pct", color="Bloque",
            barmode="stack",
            color_discrete_map=_COLOR_BLOQUES,
            text="pct",
            labels={"pct": "% Votos", "Año": ""},
            title="Bloques políticos",
        )
        fig_bloq.update_traces(
            texttemplate="%{text:.1f}%", textposition="inside",
            insidetextanchor="middle",
        )
        fig_bloq.update_layout(height=380, margin=dict(t=40, b=10))
        st.plotly_chart(fig_bloq, use_container_width=True)

    _izq_2022 = _cands_2022[_cands_2022["Bloque"] == "Izquierda"]["pct"].sum()
    _izq_2026 = _cands_2026[_cands_2026["Bloque"] == "Izquierda"]["pct"].sum()
    _der_2022 = _cands_2022[_cands_2022["Bloque"] == "Centro-der."]["pct"].sum()
    _der_2026 = _cands_2026[_cands_2026["Bloque"] == "Centro-der."]["pct"].sum()
    _ae_pct   = _cands_2026[_cands_2026["Candidato"] == "Abelardo"]["pct"].iloc[0]
    _val_pct  = _cands_2026[_cands_2026["Candidato"] == "Valencia"]["pct"].iloc[0]
    st.info(
        f"El voto de izquierda (Petro 2022 → Cepeda 2026) se mantuvo estable: "
        f"**{_izq_2022:.1f}% → {_izq_2026:.1f}%** (+{_izq_2026-_izq_2022:.1f} pp).  "
        f"El bloque de derecha pasó de {_der_2022:.1f}% (disperso entre Fico y Rodolfo) "
        f"a {_der_2026:.1f}% (Abelardo {_ae_pct:.1f}% + Paloma {_val_pct:.1f}%). "
        f"Fajardo mantuvo su base: 4.21% → 4.26%."
    )

    # ── Voto en el Exterior ──────────────────────────────────────────────────
    st.divider()
    st.subheader("Voto en el Exterior (Consulados)")

    ext_cand = (df_exterior.groupby("candidato_presidente", as_index=False)
                           .agg(votos=("votos_candidato", "sum"))
                           .sort_values("votos", ascending=False))
    ext_cand["pct"] = ext_cand["votos"] / ext_cand["votos"].sum() * 100

    col_ext1, col_ext2 = st.columns([3, 2])
    with col_ext1:
        fig_ext = px.bar(
            ext_cand, x="votos", y="candidato_presidente",
            orientation="h", color="candidato_presidente",
            color_discrete_map=COLORS,
            text=ext_cand["votos"].apply(lambda v: f"{v:,}"),
            labels={"votos": "Votos exterior", "candidato_presidente": ""},
        )
        fig_ext.update_traces(textposition="outside")
        fig_ext.update_layout(
            showlegend=False, height=350,
            margin=dict(l=0, r=60, t=10, b=0),
            yaxis={"categoryorder": "total ascending"},
            title="Votos por candidato – Exterior",
        )
        st.plotly_chart(fig_ext, use_container_width=True)

    with col_ext2:
        ext_pais = (df_exterior.groupby("muni_nombre", as_index=False)
                               .agg(total=("votos_candidato", "sum"))
                               .sort_values("total", ascending=False)
                               .head(15))
        st.caption("Top 15 consulados por participación")
        fig_pais = px.bar(
            ext_pais.sort_values("total", ascending=True),
            x="total", y="muni_nombre", orientation="h",
            color_discrete_sequence=["#5588bb"],
            labels={"total": "Votos", "muni_nombre": ""},
        )
        fig_pais.update_layout(height=350, margin=dict(l=0, r=10, t=10, b=0),
                               yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_pais, use_container_width=True)

    tabla_ext = ext_cand.copy()
    tabla_ext["Votos"] = tabla_ext["votos"].apply(lambda v: f"{v:,}")
    tabla_ext["% del exterior"] = tabla_ext["pct"].apply(lambda v: f"{v:.2f}%")
    st.dataframe(tabla_ext[["candidato_presidente", "Votos", "% del exterior"]].rename(
        columns={"candidato_presidente": "Candidato"}),
        use_container_width=True, hide_index=True)

    # ── Mapa mundial: ganador por país ───────────────────────────────────────
    st.subheader("Mapa mundial – Ganador por país")

    PAIS_ISO3 = {_norm(k): v for k, v in {
        "ALEMANIA": "DEU", "ARGENTINA": "ARG", "AUSTRALIA": "AUS",
        "AUSTRIA": "AUT", "BELGICA": "BEL", "BOLIVIA": "BOL",
        "BRASIL": "BRA", "CANADA": "CAN", "CHILE": "CHL",
        "CHINA": "CHN", "COLOMBIA": "COL", "COSTA RICA": "CRI",
        "CUBA": "CUB", "DINAMARCA": "DNK", "ECUADOR": "ECU",
        "EGIPTO": "EGY", "EL SALVADOR": "SLV", "EMIRATOS": "ARE",
        "ESPANA": "ESP", "ESPAÑA": "ESP", "ESTADOS UNIDOS": "USA",
        "FILIPINAS": "PHL", "FINLANDIA": "FIN", "FRANCIA": "FRA",
        "GRECIA": "GRC", "GUATEMALA": "GTM", "HOLANDA": "NLD",
        "HONDURAS": "HND", "HUNGRIA": "HUN", "INDIA": "IND",
        "ISRAEL": "ISR", "ITALIA": "ITA", "JAPON": "JPN",
        "JORDANIA": "JOR", "LIBANO": "LBN", "LIBIA": "LBY",
        "LUXEMBURGO": "LUX", "MARRUECOS": "MAR", "MEXICO": "MEX",
        "NICARAGUA": "NIC", "NIGERIA": "NGA", "NORUEGA": "NOR",
        "NUEVA ZELANDA": "NZL", "PANAMA": "PAN", "PARAGUAY": "PRY",
        "PERU": "PER", "POLONIA": "POL", "PORTUGAL": "PRT",
        "REINO UNIDO": "GBR", "REPUBLICA DOMINICANA": "DOM",
        "RUSIA": "RUS", "SUECIA": "SWE", "SUIZA": "CHE",
        "TAILANDIA": "THA", "TRINIDAD Y TOBAGO": "TTO", "TURQUIA": "TUR",
        "UCRANIA": "UKR", "URUGUAY": "URY", "VENEZUELA": "VEN",
        "ARGELIA": "DZA", "ARUBA": "ABW", "AZERBAIYAN": "AZE", "COREA DEL SUR": "KOR",
        "CURAZAO": "CUW", "GHANA": "GHA", "HAITI": "HTI",
        "INDONESIA": "IDN", "INGLATERRA": "GBR", "IRLANDA": "IRL",
        "JAMAICA": "JAM", "KENIA": "KEN", "MALASIA": "MYS",
        "NUEVA ZELANDIA": "NZL", "PAISES BAJOS": "NLD", "PUERTO RICO": "PRI",
        "REPUBLICA DE SINGAPUR": "SGP",
        "REPUBLICA SOCIALISTA DE VIETNA": "VNM", "SUDAFRICA": "ZAF",
    }.items()}

    def _pais_from_muni(name: str) -> str:
        n = _norm(name)
        if "-" in n:
            candidate = n.split("-")[-1].strip()
            if candidate in PAIS_ISO3:
                return candidate
        for pais in sorted(PAIS_ISO3, key=len, reverse=True):
            if pais in n:
                return pais
        return ""

    df_ext_top = df_exterior[df_exterior["candidato_presidente"].isin(TOP_CANDS)].copy()
    df_ext_top["pais_key"] = df_ext_top["muni_nombre"].apply(_pais_from_muni)
    df_ext_top = df_ext_top[df_ext_top["pais_key"] != ""]

    _pais_all = (
        df_ext_top.groupby(["pais_key", "candidato_presidente"], as_index=False)
                  .agg(votos=("votos_candidato", "sum"))
    )
    pais_winner = (
        _pais_all.sort_values("votos", ascending=False)
                 .drop_duplicates("pais_key")
    )
    _pais_ae_ic = (
        _pais_all[_pais_all["candidato_presidente"].isin(
            ["ABELARDO DE LA ESPRIELLA", "IVÁN CEPEDA CASTRO"])]
        .pivot(index="pais_key", columns="candidato_presidente", values="votos")
        .rename(columns={"ABELARDO DE LA ESPRIELLA": "v_AE",
                         "IVÁN CEPEDA CASTRO": "v_IC"})
        .reset_index()
    )
    _pais_ae_ic.columns.name = None
    pais_winner = pais_winner.merge(_pais_ae_ic, on="pais_key", how="left")
    pais_winner["iso3"] = pais_winner["pais_key"].map(PAIS_ISO3)
    pais_winner = pais_winner.dropna(subset=["iso3"])

    if not pais_winner.empty:
        fig_world = px.choropleth(
            pais_winner,
            locations="iso3",
            color="candidato_presidente",
            color_discrete_map=COLORS,
            hover_name="pais_key",
            hover_data={"v_AE": ":,", "v_IC": ":,", "iso3": False},
            labels={"candidato_presidente": "Ganador",
                    "v_AE": "V. Abelardo", "v_IC": "V. Cepeda"},
            projection="natural earth",
        )
        fig_world.update_layout(
            height=420, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            template=_PLOTLY_TPL,
            dragmode=False,
            geo=dict(
                bgcolor="rgba(0,0,0,0)",
                showframe=False,
                showcoastlines=True,
                coastlinecolor=_GEO_COAST,
                landcolor=_GEO_LAND,
                oceancolor=_GEO_OCEAN,
                showocean=True,
                showland=True,
            ),
        )
        st.plotly_chart(fig_world, use_container_width=True, config=_MAP_CFG)
    else:
        st.caption("No se pudo mapear países desde los nombres de consulados.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 – POR DEPARTAMENTO
# ═══════════════════════════════════════════════════════════════════════════════
with t_depts:
    st.title("Distribución por Departamento")

    # Agrupación con OTROS por departamento — solo interior (sin consulados)
    df_dept = group_otros(df_interior, "candidato_presidente").copy()
    agg_d = (df_dept.groupby(["dept_nombre", "candidato_presidente"], as_index=False)
                    .agg(votos=("votos_candidato", "sum")))

    # Calcular porcentaje dentro de cada departamento
    agg_d["total_dept"] = agg_d.groupby("dept_nombre")["votos"].transform("sum")
    agg_d["pct_dept"]   = agg_d["votos"] / agg_d["total_dept"] * 100

    # Ordenar departamentos por votos de Abelardo descendente (mayor Abelardo = arriba en chart)
    _ae_by_dept = (agg_d[agg_d["candidato_presidente"] == "ABELARDO DE LA ESPRIELLA"]
                   .set_index("dept_nombre")["votos"])
    orden_dept = _ae_by_dept.sort_values(ascending=True).index.tolist()  # ascending=True → arriba = mayor

    st.subheader("Distribución % por departamento – Colombia interior (top 4 + Otros)")
    fig = px.bar(
        agg_d,
        y="dept_nombre",
        x="pct_dept",
        color="candidato_presidente",
        color_discrete_map=COLORS,
        category_orders={
            "dept_nombre": orden_dept,
            "candidato_presidente": TOP_CANDS + ["OTROS"],
        },
        labels={
            "pct_dept": "% Votos",
            "dept_nombre": "",
            "candidato_presidente": "Candidato",
        },
        orientation="h",
        barmode="stack",
    )
    fig.update_layout(
        height=620,
        legend_title="Candidato",
        yaxis={"categoryorder": "array", "categoryarray": orden_dept},
        xaxis=dict(ticksuffix="%", range=[0, 101]),
        margin=dict(l=180, r=20, t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Mapa: % AE por departamento ─────────────────────────────────────────
    st.subheader("Mapa: % Abelardo vs Cepeda por departamento")

    dept_agg2 = (df_interior.groupby(["dept_nombre", "candidato_presidente"], as_index=False)
                             .agg(votos=("votos_candidato", "sum")))
    total_dept = dept_agg2.groupby("dept_nombre")["votos"].sum().rename("total")
    dept_agg2  = dept_agg2.join(total_dept, on="dept_nombre")
    dept_agg2["pct"] = dept_agg2["votos"] / dept_agg2["total"] * 100

    ae_dept = dept_agg2[dept_agg2["candidato_presidente"] == "ABELARDO DE LA ESPRIELLA"].copy()
    ae_dept["divipola"] = ae_dept["dept_nombre"].map(DEPT_TO_DIVIPOLA)
    ae_dept = ae_dept.dropna(subset=["divipola"])

    ae_dept_mg = ae_dept.copy()
    ic_dept_vals = (dept_agg2[dept_agg2["candidato_presidente"] == "IVÁN CEPEDA CASTRO"]
                    [["dept_nombre", "pct"]]
                    .rename(columns={"pct": "pct_IC"}))
    ae_dept_mg = ae_dept_mg.merge(ic_dept_vals, on="dept_nombre", how="left")
    ae_dept_mg["margen"] = ae_dept_mg["pct"] - ae_dept_mg["pct_IC"]

    fig_margin = px.choropleth(
        ae_dept_mg,
        geojson=geo_depts,
        locations="divipola",
        featureidkey="properties.DPTO",
        color="margen",
        color_continuous_scale="RdBu",
        color_continuous_midpoint=0,
        range_color=[-40, 40],
        hover_name="dept_nombre",
        hover_data={"pct": ":.1f", "pct_IC": ":.1f", "margen": ":.1f", "divipola": False},
        labels={"margen": "Margen AE−IC (pp)", "pct": "% AE", "pct_IC": "% IC"},
        title="Margen AE − IC por departamento (azul = AE lidera, rojo = IC lidera)",
    )
    _fix_colombia_geo(fig_margin, height=460)
    fig_margin.update_layout(coloraxis_colorbar=dict(title="Margen pp", thickness=15, len=0.6))
    st.plotly_chart(fig_margin, use_container_width=True, config=_MAP_CFG)

    # ── Mapa municipal: ganador por municipio ───────────────────────────────
    st.subheader("Mapa: ganador por municipio")

    mun_winner = mun[["dept_nombre", "muni_nombre", "divipola_muni",
                       "ganador", "votos_AE", "votos_IC", "diff_AE_IC"]].copy()
    mun_winner = mun_winner[mun_winner["divipola_muni"] != ""]

    fig_muni = px.choropleth(
        mun_winner,
        geojson=geo_munis,
        locations="divipola_muni",
        featureidkey="properties.MPIO_CCNCT",
        color="ganador",
        color_discrete_map=GANADOR_COLORS,
        hover_name="muni_nombre",
        hover_data={
            "dept_nombre": True,
            "votos_AE": ":,",
            "votos_IC": ":,",
            "diff_AE_IC": ":,",
            "divipola_muni": False,
        },
        labels={"ganador": "Ganador", "diff_AE_IC": "Diferencia AE−IC"},
    )
    fig_muni.update_layout(legend=dict(title="Ganador"))
    _fix_colombia_geo(fig_muni, height=580)
    st.plotly_chart(fig_muni, use_container_width=True, config=_MAP_CFG)

    # Participación promedio
    st.subheader("Participación promedio por departamento")
    part = (mun.groupby("dept_nombre", as_index=False)
               .agg(part_prom=("pct_participacion", "mean"))
               .sort_values("part_prom", ascending=False))
    fig2 = px.bar(
        part, x="dept_nombre", y="part_prom",
        color="part_prom", color_continuous_scale="Blues",
        labels={"dept_nombre": "Departamento", "part_prom": "% Participación"},
    )
    fig2.update_layout(height=400, xaxis_tickangle=-45, margin=dict(b=120))
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Abstención por municipio – distribución")
    fig_abs = px.histogram(
        mun_interior,
        x="pct_participacion",
        nbins=30,
        color="ganador",
        color_discrete_map=GANADOR_COLORS,
        barmode="overlay",
        opacity=0.7,
        labels={"pct_participacion": "% Participación", "ganador": "Ganador"},
        title="Distribución de participación según ganador del municipio",
    )
    _media_part = mun_interior["pct_participacion"].mean()
    fig_abs.add_vline(
        x=_media_part,
        line_dash="dash", line_color="gray",
        annotation_text=f"Media {_media_part:.1f}%",
        annotation_position="top right",
    )
    st.plotly_chart(fig_abs, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 – FUERZA ABELARDO
# ═══════════════════════════════════════════════════════════════════════════════
with t_fuerza_ae:
    st.title("Donde fue fuerte Abelardo De La Espriella")

    top_n = st.slider("Número de municipios", 10, 100, 30)
    top = mun_f.nlargest(top_n, "pct_AE")[
        ["dept_nombre", "muni_nombre", "muni_label", "votos_AE", "pct_AE",
         "votos_IC", "pct_IC", "diff_AE_IC"]
    ].reset_index(drop=True)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.subheader(f"Top {top_n} municipios por % AE")
        fig = px.bar(
            top.sort_values("pct_AE", ascending=True),
            x="pct_AE", y="muni_label",
            color="dept_nombre",
            orientation="h",
            labels={"pct_AE": "% Votos AE", "muni_label": "", "dept_nombre": "Depto."},
        )
        _nac_pct_AE = mun_interior["pct_AE"].mean()
        fig.add_vline(
            x=_nac_pct_AE, line_dash="dash", line_color="gray", opacity=0.6,
            annotation_text=f"Media nacional {_nac_pct_AE:.1f}%",
            annotation_position="top right",
        )
        fig.update_layout(
            height=min(max(400, top_n * 22), 1400), showlegend=True,
            margin=dict(l=0, r=20, t=10, b=0),
            yaxis={"categoryorder": "total ascending"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.subheader("Datos")
        top_show = top[["dept_nombre", "muni_label", "votos_AE", "pct_AE",
                         "votos_IC", "pct_IC", "diff_AE_IC"]].copy()
        top_show["votos_AE"]   = top_show["votos_AE"].apply(lambda v: f"{v:,.0f}")
        top_show["votos_IC"]   = top_show["votos_IC"].apply(lambda v: f"{v:,.0f}")
        top_show["pct_AE"]     = top_show["pct_AE"].apply(lambda v: f"{v:.1f}%")
        top_show["pct_IC"]     = top_show["pct_IC"].apply(lambda v: f"{v:.1f}%")
        top_show["diff_AE_IC"] = top_show["diff_AE_IC"].apply(lambda v: f"{v:+,.0f}")
        top_show.columns = ["Depto", "Municipio", "V_AE", "% AE", "V_IC", "% IC", "Dif"]
        st.dataframe(top_show, use_container_width=True, hide_index=True, height=600)

    # Scatter % AE vs % IC — contexto nacional, departamento resaltado si hay filtro
    st.subheader("% AE vs % IC por municipio")
    _sc3_base = mun_interior.copy()
    _sc3_base["muni_label"] = _sc3_base.apply(_muni_label, axis=1)

    if sel_dept not in ("Todos", EXTERIOR_LABEL):
        _sc3_bg = _sc3_base[_sc3_base["dept_nombre"] != sel_dept]
        _sc3_hl = _sc3_base[_sc3_base["dept_nombre"] == sel_dept]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=_sc3_bg["pct_AE"], y=_sc3_bg["pct_IC"],
            mode="markers", name="Otros departamentos",
            marker=dict(color="#cccccc", opacity=0.2, size=4),
            text=_sc3_bg["muni_label"],
            hovertemplate="%{text}<br>AE: %{x:.1f}%  IC: %{y:.1f}%<extra></extra>",
        ))
        fig3.add_trace(go.Scatter(
            x=_sc3_hl["pct_AE"], y=_sc3_hl["pct_IC"],
            mode="markers", name=sel_dept,
            marker=dict(color="#1f77b4", opacity=0.9, size=7),
            text=_sc3_hl["muni_label"],
            hovertemplate="%{text}<br>AE: %{x:.1f}%  IC: %{y:.1f}%<extra></extra>",
        ))
        fig3.update_layout(
            xaxis_title="% Abelardo", yaxis_title="% Cepeda",
            xaxis=dict(range=[0, 100]), yaxis=dict(range=[0, 100]),
        )
    else:
        fig3 = px.scatter(
            mun_f, x="pct_AE", y="pct_IC",
            color="dept_nombre", hover_name="muni_label",
            hover_data={"votos_AE": ":,", "votos_IC": ":,", "dept_nombre": True},
            labels={"pct_AE": "% Abelardo", "pct_IC": "% Cepeda"},
            opacity=0.7,
        )

    fig3.add_shape(
        type="line", x0=0, y0=0, x1=100, y1=100,
        line=dict(dash="dash", color="gray", width=1),
    )
    fig3.add_annotation(
        x=73, y=82, text="IC gana", showarrow=False,
        font=dict(color="#CC0000", size=12, family="Arial"), opacity=0.85,
    )
    fig3.add_annotation(
        x=72, y=28, text="AE gana", showarrow=False,
        font=dict(color="#1f77b4", size=12, family="Arial"), opacity=0.85,
    )
    fig3.update_layout(height=440)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption(
        "Contexto nacional: cada punto = un municipio. "
        "Línea punteada = empate (AE% = IC%). "
        + (f"Resaltados {len(_sc3_hl)} municipios de {sel_dept}. "
           if sel_dept not in ("Todos", EXTERIOR_LABEL) else "")
        + f"AE gana en {(mun_interior['pct_AE'] >= mun_interior['pct_IC']).sum()} "
          f"municipios, IC en {(mun_interior['pct_IC'] > mun_interior['pct_AE']).sum()}."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 – FUERZA PALOMA
# ═══════════════════════════════════════════════════════════════════════════════
with t_fuerza_paloma:
    st.title("Donde fue fuerte Paloma Valencia Laserna")

    top_n = st.slider("Número de municipios", 10, 100, 30, key="slider_paloma")
    top = mun_f.nlargest(top_n, "pct_Valencia")[
        ["dept_nombre", "muni_nombre", "muni_label", "votos_Valencia", "pct_Valencia",
         "votos_AE", "votos_IC", "pct_AE", "pct_IC"]
    ].reset_index(drop=True)

    fig = px.bar(
        top.sort_values("pct_Valencia", ascending=True),
        x="pct_Valencia", y="muni_label",
        color="dept_nombre",
        orientation="h",
        labels={"pct_Valencia": "% Votos Paloma", "muni_label": "", "dept_nombre": "Depto."},
    )
    _nac_pct_Val = mun_interior["pct_Valencia"].mean()
    fig.add_vline(
        x=_nac_pct_Val, line_dash="dash", line_color="gray", opacity=0.6,
        annotation_text=f"Media nacional {_nac_pct_Val:.1f}%",
        annotation_position="top right",
    )
    fig.update_layout(
        height=min(max(400, top_n * 22), 1400),
        margin=dict(l=0, r=20, t=10, b=0),
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # Correlación Paloma ↔ AE y IC — contexto nacional, dept resaltado si hay filtro
    _sc_pal_base = mun_interior.copy()
    _sc_pal_base["muni_label"] = _sc_pal_base.apply(_muni_label, axis=1)
    _r_pval_ae = mun_interior["pct_Valencia"].corr(mun_interior["pct_AE"])
    _r_pval_ic = mun_interior["pct_Valencia"].corr(mun_interior["pct_IC"])
    st.subheader("Correlación Paloma con AE y con IC (por municipio)")

    _pal_highlight = sel_dept not in ("Todos", EXTERIOR_LABEL)
    if _pal_highlight:
        _pal_bg = _sc_pal_base[_sc_pal_base["dept_nombre"] != sel_dept]
        _pal_hl = _sc_pal_base[_sc_pal_base["dept_nombre"] == sel_dept]

    col_a, col_b = st.columns(2)
    with col_a:
        if _pal_highlight:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=_pal_bg["pct_Valencia"], y=_pal_bg["pct_AE"],
                mode="markers", name="Otros",
                marker=dict(color="#cccccc", opacity=0.2, size=4),
                text=_pal_bg["muni_label"],
                hovertemplate="%{text}<br>Paloma: %{x:.1f}%  AE: %{y:.1f}%<extra></extra>",
            ))
            fig2.add_trace(go.Scatter(
                x=_pal_hl["pct_Valencia"], y=_pal_hl["pct_AE"],
                mode="markers", name=sel_dept,
                marker=dict(color="#1f77b4", opacity=0.9, size=7),
                text=_pal_hl["muni_label"],
                hovertemplate="%{text}<br>Paloma: %{x:.1f}%  AE: %{y:.1f}%<extra></extra>",
            ))
            add_trend(fig2, _sc_pal_base["pct_Valencia"], _sc_pal_base["pct_AE"], name="Tendencia nac.")
            fig2.update_layout(xaxis_title="% Paloma", yaxis_title="% Abelardo")
        else:
            fig2 = px.scatter(
                mun_f, x="pct_Valencia", y="pct_AE",
                color="dept_nombre", hover_name="muni_label", opacity=0.7,
                hover_data={"dept_nombre": True},
                labels={"pct_Valencia": "% Paloma", "pct_AE": "% Abelardo"},
            )
            add_trend(fig2, mun_f["pct_Valencia"], mun_f["pct_AE"], name="Tendencia")
        fig2.update_layout(
            showlegend=False,
            title=f"Paloma vs Abelardo  (r = {_r_pval_ae:+.2f})",
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        if _pal_highlight:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=_pal_bg["pct_Valencia"], y=_pal_bg["pct_IC"],
                mode="markers", name="Otros",
                marker=dict(color="#cccccc", opacity=0.2, size=4),
                text=_pal_bg["muni_label"],
                hovertemplate="%{text}<br>Paloma: %{x:.1f}%  IC: %{y:.1f}%<extra></extra>",
            ))
            fig3.add_trace(go.Scatter(
                x=_pal_hl["pct_Valencia"], y=_pal_hl["pct_IC"],
                mode="markers", name=sel_dept,
                marker=dict(color="#CC0000", opacity=0.9, size=7),
                text=_pal_hl["muni_label"],
                hovertemplate="%{text}<br>Paloma: %{x:.1f}%  IC: %{y:.1f}%<extra></extra>",
            ))
            add_trend(fig3, _sc_pal_base["pct_Valencia"], _sc_pal_base["pct_IC"], name="Tendencia nac.")
            fig3.update_layout(xaxis_title="% Paloma", yaxis_title="% Cepeda")
        else:
            fig3 = px.scatter(
                mun_f, x="pct_Valencia", y="pct_IC",
                color="dept_nombre", hover_name="muni_label", opacity=0.7,
                hover_data={"dept_nombre": True},
                labels={"pct_Valencia": "% Paloma", "pct_IC": "% Cepeda"},
            )
            add_trend(fig3, mun_f["pct_Valencia"], mun_f["pct_IC"], name="Tendencia")
        fig3.update_layout(
            showlegend=False,
            title=f"Paloma vs Cepeda  (r = {_r_pval_ic:+.2f})",
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.caption(
        "r > 0: relación positiva (donde Paloma es fuerte, ese candidato también). "
        "r < 0: relación negativa. "
        "Paloma y AE comparten electorado de derecha; Paloma y Cepeda son opuestos ideológicos. "
        "Contexto nacional siempre visible; el departamento seleccionado se resalta en color."
    )

    st.subheader("Datos")
    top_show = top[["dept_nombre", "muni_label", "votos_Valencia", "pct_Valencia",
                     "votos_AE", "votos_IC", "pct_AE", "pct_IC"]].copy()
    for c in ["votos_Valencia", "votos_AE", "votos_IC"]:
        top_show[c] = top_show[c].apply(lambda v: f"{v:,.0f}")
    for c in ["pct_Valencia", "pct_AE", "pct_IC"]:
        top_show[c] = top_show[c].apply(lambda v: f"{v:.1f}%")
    top_show.columns = ["Depto", "Municipio", "V_Paloma", "% Paloma",
                        "V_AE", "V_IC", "% AE", "% IC"]
    st.dataframe(top_show, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 – ANÁLISIS COALICIÓN
# ═══════════════════════════════════════════════════════════════════════════════
with t_coalicion:
    st.title("Análisis Coalición – Constructor de escenarios")

    # ── Configurar escenario ─────────────────────────────────────────────────
    st.markdown("**Asigna el apoyo de cada candidato en segunda vuelta:**")
    coal_opts = ["→ Abelardo", "→ Cepeda", "Ninguno"]

    cfg_col1, cfg_col2, cfg_col3 = st.columns(3)
    with cfg_col1:
        apoyo_valencia = st.radio(
            "Paloma Valencia (1,637,665 v.)",
            coal_opts, index=0, horizontal=True, key="coal_paloma",
        )
    with cfg_col2:
        apoyo_fajardo = st.radio(
            "Sergio Fajardo (1,007,943 v.)",
            coal_opts, index=0, horizontal=True, key="coal_fajardo",
        )
    with cfg_col3:
        apoyo_claudia = st.radio(
            "Claudia López (225,335 v.)*",
            coal_opts, index=2, horizontal=True, key="coal_claudia",
        )
    st.caption("Referencia 2022 (primera vuelta): Petro 40.3% · Rodolfo Hernández 28.2% · F. Gutiérrez 23.9% · Fajardo 4.2%")

    # ── Calcular coalición dinámica ─────────────────────────────────────────
    CLAUDIA_VOTOS = 225_335

    mun_coal = mun.copy()
    mun_coal["votos_ae_coal"] = mun_coal["votos_AE"].copy()
    mun_coal["votos_ic_coal"] = mun_coal["votos_IC"].copy()

    if apoyo_valencia == "→ Abelardo":
        mun_coal["votos_ae_coal"] += mun_coal["votos_Valencia"]
    elif apoyo_valencia == "→ Cepeda":
        mun_coal["votos_ic_coal"] += mun_coal["votos_Valencia"]

    if apoyo_fajardo == "→ Abelardo":
        mun_coal["votos_ae_coal"] += mun_coal["votos_Fajardo"]
    elif apoyo_fajardo == "→ Cepeda":
        mun_coal["votos_ic_coal"] += mun_coal["votos_Fajardo"]

    mun_coal["diff_coal"]    = mun_coal["votos_ae_coal"] - mun_coal["votos_ic_coal"]
    mun_coal["gana_ae_solo"] = (mun_coal["votos_AE"] > mun_coal["votos_IC"]).astype(int)
    mun_coal["gana_coal"]    = (mun_coal["votos_ae_coal"] > mun_coal["votos_ic_coal"]).astype(int)

    # Totales nacionales (Claudia se suma solo a nivel nacional)
    ae_nac = int(mun_coal["votos_ae_coal"].sum())
    ic_nac = int(mun_coal["votos_ic_coal"].sum())
    if apoyo_claudia == "→ Abelardo":
        ae_nac += CLAUDIA_VOTOS
    elif apoyo_claudia == "→ Cepeda":
        ic_nac += CLAUDIA_VOTOS

    total_ae        = int(mun["votos_AE"].sum())
    total_ic        = int(mun["votos_IC"].sum())
    munis_gana_ae   = int(mun_coal["gana_ae_solo"].sum())
    munis_gana_coal = int(mun_coal["gana_coal"].sum())
    n_coal          = len(mun_coal)
    ganados_extra   = munis_gana_coal - munis_gana_ae

    # ── Totales nacionales (al tope, visual y destacado) ────────────────────
    st.subheader("Totales nacionales – Escenario coalición")
    _diff_nac = ae_nac - ic_nac
    _ganador_label = "ABELARDO GANA" if _diff_nac > 0 else "CEPEDA GANA"
    _ganador_color = "#1f77b4" if _diff_nac > 0 else "#CC0000"

    tot_c1, tot_c2, tot_c3 = st.columns(3)
    tot_c1.metric(
        "Abelardo (con coalición)",
        f"{ae_nac:,}",
        f"+{ae_nac - total_ae:,} vs solo",
    )
    tot_c2.metric(
        "Cepeda",
        f"{ic_nac:,}",
    )
    tot_c3.metric(
        "Diferencia",
        f"{abs(_diff_nac):,}",
        _ganador_label,
        delta_color="normal" if _diff_nac > 0 else "inverse",
    )

    # Barra comparativa AE vs IC
    fig_tot = px.bar(
        pd.DataFrame({
            "Candidato": ["Abelardo (coalición)", "Cepeda"],
            "Votos":     [ae_nac, ic_nac],
            "Color":     ["ABELARDO DE LA ESPRIELLA", "IVÁN CEPEDA CASTRO"],
        }),
        x="Votos", y="Candidato", orientation="h",
        color="Color", color_discrete_map=COLORS,
        text=pd.Series([ae_nac, ic_nac]).apply(lambda v: f"{v:,.0f}"),
    )
    fig_tot.update_traces(textposition="outside", cliponaxis=False)
    fig_tot.update_layout(
        showlegend=False, height=150,
        margin=dict(l=0, r=180, t=4, b=4),
        xaxis={"autorange": True},
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig_tot, use_container_width=True)

    st.divider()

    # ── Métricas de municipios ───────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("AE gana solo",
              f"{munis_gana_ae:,} / {n_coal:,} municipios",
              f"{munis_gana_ae/n_coal*100:.0f}%")
    c2.metric("AE con coalición",
              f"{munis_gana_coal:,} / {n_coal:,} municipios",
              f"{munis_gana_coal/n_coal*100:.0f}%", delta_color="normal")
    c3.metric("Municipios que suma coalición",
              f"+{ganados_extra:,}" if ganados_extra >= 0 else f"{ganados_extra:,}")

    st.divider()

    # ── Diferencia por departamento ──────────────────────────────────────────
    st.subheader("Diferencia votos: coalición AE – Cepeda por departamento")
    st.caption("Verde = coalición gana el departamento  |  Rojo = Cepeda gana")

    mun_coal_int = mun_coal[mun_coal["dept_nombre"] != "CONSULADOS"]
    dept_coal = (mun_coal_int.groupby("dept_nombre", as_index=False)
                    .agg(
                        votos_AE=("votos_AE", "sum"),
                        votos_IC=("votos_IC", "sum"),
                        votos_ae_coal=("votos_ae_coal", "sum"),
                        votos_ic_coal=("votos_ic_coal", "sum"),
                        votos_Valencia=("votos_Valencia", "sum"),
                        votos_Fajardo=("votos_Fajardo", "sum"),
                    ))
    dept_coal["diff_coal"]    = dept_coal["votos_ae_coal"] - dept_coal["votos_ic_coal"]
    dept_coal["ganador_coal"] = dept_coal["diff_coal"].apply(
        lambda d: "COALICIÓN AE" if d > 0 else "CEPEDA"
    )
    dept_coal = dept_coal.sort_values("diff_coal", ascending=False)

    fig_dept = px.bar(
        dept_coal, x="diff_coal", y="dept_nombre",
        color="ganador_coal",
        color_discrete_map={"COALICIÓN AE": "#2ca02c", "CEPEDA": "#CC0000"},
        orientation="h",
        labels={"diff_coal": "Diferencia (coalición AE – Cepeda)",
                "dept_nombre": "", "ganador_coal": ""},
        hover_data={
            "votos_AE": ":,", "votos_IC": ":,",
            "votos_Valencia": ":,", "votos_Fajardo": ":,",
            "votos_ae_coal": ":,", "votos_ic_coal": ":,",
        },
    )
    fig_dept.add_vline(x=0, line_dash="solid", line_color="black", line_width=1)
    fig_dept.update_layout(
        height=700, showlegend=True,
        margin=dict(l=0, r=10, t=10, b=0),
        yaxis={"categoryorder": "total ascending"},
    )
    st.plotly_chart(fig_dept, use_container_width=True)

    # ── Mapas departamentos: original vs coalición ───────────────────────────
    st.subheader("Mapa por departamento: 1ª vuelta vs Escenario coalición")
    _dept_coal_map = dept_coal.copy()
    _dept_coal_map["divipola"] = _dept_coal_map["dept_nombre"].map(DEPT_TO_DIVIPOLA)
    _dept_coal_map = _dept_coal_map.dropna(subset=["divipola"])

    # Ganador original por departamento
    _dept_orig_map = (mun_coal_int.groupby("dept_nombre", as_index=False)
                                  .agg(votos_AE=("votos_AE", "sum"),
                                       votos_IC=("votos_IC", "sum")))
    _dept_orig_map["ganador_orig"] = _dept_orig_map.apply(
        lambda r: "ABELARDO" if r["votos_AE"] > r["votos_IC"] else "CEPEDA", axis=1
    )
    _dept_orig_map["divipola"] = _dept_orig_map["dept_nombre"].map(DEPT_TO_DIVIPOLA)
    _dept_orig_map = _dept_orig_map.dropna(subset=["divipola"])

    _GANADOR_COAL_COLORS = {"COALICIÓN AE": "#2ca02c", "CEPEDA": "#CC0000"}
    _GANADOR_ORIG_COLORS = {"ABELARDO": "#1f77b4",    "CEPEDA": "#CC0000"}

    def _dept_choropleth(df, color_col, color_map, title):
        fig = px.choropleth(
            df, geojson=geo_depts, locations="divipola",
            featureidkey="properties.DPTO",
            color=color_col, color_discrete_map=color_map,
            hover_name="dept_nombre",
            labels={color_col: "Ganador"},
            title=title,
        )
        _fix_colombia_geo(fig, height=400)
        return fig

    _col_dm1, _col_dm2 = st.columns(2)
    with _col_dm1:
        st.caption("Primera vuelta (sin coalición)")
        fig_dmap_orig = _dept_choropleth(
            _dept_orig_map, "ganador_orig", _GANADOR_ORIG_COLORS, "1ª Vuelta"
        )
        st.plotly_chart(fig_dmap_orig, use_container_width=True, config=_MAP_CFG)
    with _col_dm2:
        st.caption("Con coalición seleccionada")
        fig_dmap = _dept_choropleth(
            _dept_coal_map, "ganador_coal", _GANADOR_COAL_COLORS, "Coalición"
        )
        st.plotly_chart(fig_dmap, use_container_width=True, config=_MAP_CFG)

    # ── Mapas municipios: original vs coalición ──────────────────────────────
    st.subheader("Mapa por municipio: 1ª vuelta vs Escenario coalición")
    _mun_coal_map = mun_coal[
        (mun_coal["dept_nombre"] != "CONSULADOS") &
        (mun_coal["divipola_muni"].astype(str) != "")
    ].copy()
    _mun_coal_map["ganador_coal_label"] = _mun_coal_map["gana_coal"].map(
        {1: "COALICIÓN AE", 0: "CEPEDA"}
    )

    def _muni_choropleth(df, color_col, color_map, title):
        fig = px.choropleth(
            df, geojson=geo_munis, locations="divipola_muni",
            featureidkey="properties.MPIO_CCNCT",
            color=color_col, color_discrete_map=color_map,
            hover_name="muni_nombre",
            hover_data={"dept_nombre": True, "votos_AE": ":,",
                        "votos_IC": ":,", "divipola_muni": False},
            labels={color_col: "Ganador"},
            title=title,
        )
        _fix_colombia_geo(fig, height=500)
        return fig

    _col_mm1, _col_mm2 = st.columns(2)
    with _col_mm1:
        st.caption("Primera vuelta (sin coalición)")
        fig_mmap_orig = _muni_choropleth(
            _mun_coal_map, "ganador", _GANADOR_ORIG_COLORS, "1ª Vuelta"
        )
        st.plotly_chart(fig_mmap_orig, use_container_width=True, config=_MAP_CFG)
    with _col_mm2:
        st.caption("Con coalición seleccionada")
        fig_mmap = _muni_choropleth(
            _mun_coal_map, "ganador_coal_label", _GANADOR_COAL_COLORS, "Coalición"
        )
        st.plotly_chart(fig_mmap, use_container_width=True, config=_MAP_CFG)

    # ── Municipios revertidos ────────────────────────────────────────────────
    st.subheader("Municipios donde la coalición revierte el resultado")

    if sel_dept == EXTERIOR_LABEL:
        mun_coal_f = mun_coal[mun_coal["dept_nombre"] == "CONSULADOS"]
    elif sel_dept != "Todos":
        mun_coal_f = mun_coal[mun_coal["dept_nombre"] == sel_dept]
    else:
        mun_coal_f = mun_coal[mun_coal["dept_nombre"] != "CONSULADOS"]

    revertidos = mun_coal_f[
        (mun_coal_f["gana_ae_solo"] == 0) & (mun_coal_f["gana_coal"] == 1)
    ][["dept_nombre", "muni_nombre", "votos_AE", "votos_IC",
       "votos_Valencia", "votos_Fajardo", "votos_ae_coal", "diff_coal"]].copy()

    st.metric("Municipios revertidos por coalición", f"{len(revertidos):,}")

    if not revertidos.empty:
        revertidos = revertidos.sort_values("diff_coal", ascending=False)
        for c in ["votos_AE", "votos_IC", "votos_Valencia", "votos_Fajardo", "votos_ae_coal"]:
            revertidos[c] = revertidos[c].apply(lambda v: f"{v:,.0f}")
        revertidos["diff_coal"] = revertidos["diff_coal"].apply(lambda v: f"{v:+,.0f}")
        st.dataframe(revertidos.reset_index(drop=True),
                     use_container_width=True, hide_index=True)



# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 – PROYECCIÓN 2ª VUELTA
# ═══════════════════════════════════════════════════════════════════════════════
with t_proyeccion:
    st.title("Proyección Segunda Vuelta")

    st.markdown("""
    Modelo de transferencia de votos basado en ideología y endorsements observados.
    Ajusta las tasas para ver cómo cambia el resultado.
    """)

    # ── Encuestas 2ª vuelta ──────────────────────────────────────────────────
    st.subheader("Encuestas publicadas – 2ª vuelta")

    _POLLS = [
        # (firma, fecha_pub, AE%, IC%, blanco_ns%, muestra, nota)
        ("Invamer",          "abr-2026", 40.4, 40.6,  19.0,  None,  "Pre-1ª vuelta · escenario hipotético AE vs IC"),
        ("CNC",              "may-2026", 43.6, 40.9,  15.5,  None,  "Pre-1ª vuelta · escenario hipotético"),
        ("Guarumo / EcoAna", "may-2026", 43.6, 40.0,  16.4,  None,  "Pre-1ª vuelta · ninguno=16.4%"),
        ("AtlasIntel",       "may-2026", 50.0, 41.3,   8.7,  None,  "Pre-1ª vuelta · escenario 2v"),
        ("AtlasIntel",       "1-2 jun",  50.3, 42.6,   7.1,  2030,  "Post-1ª vuelta · blanco 3.7%, NS 2.9% · ±2% IC 95%"),
    ]
    _poll_df = pd.DataFrame(_POLLS, columns=["Firma", "Fecha", "AE%", "IC%", "Otros/NS%", "Muestra", "Nota"])

    # Normalizar AE vs IC (excluyendo blancos/NS)
    _poll_df["AE% norm"] = (_poll_df["AE%"] / (_poll_df["AE%"] + _poll_df["IC%"]) * 100).round(1)
    _poll_df["IC% norm"] = 100 - _poll_df["AE% norm"]
    _poll_df["Margen AE-IC"] = (_poll_df["AE%"] - _poll_df["IC%"]).round(1).apply(lambda v: f"{v:+.1f} pp")

    # Gráfico de encuestas
    _fig_polls = go.Figure()
    _firms = _poll_df["Firma"].tolist()
    _labels = [f"{r['Firma']}<br>{r['Fecha']}" for _, r in _poll_df.iterrows()]

    _fig_polls.add_trace(go.Bar(
        name="AE (bruto)", x=_labels, y=_poll_df["AE%"],
        marker_color="#1f77b4", text=_poll_df["AE%"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
    ))
    _fig_polls.add_trace(go.Bar(
        name="IC (bruto)", x=_labels, y=_poll_df["IC%"],
        marker_color="#CC0000", text=_poll_df["IC%"].apply(lambda v: f"{v:.1f}%"),
        textposition="outside",
    ))
    _fig_polls.add_hline(y=50, line_dash="dot", line_color="#C8A96E",
                         annotation_text="50% mayoría", annotation_position="right")
    _fig_polls.update_layout(
        barmode="group", height=400,
        title="Intención de voto 2ª vuelta por encuestadora (% bruto)",
        xaxis_title="", yaxis_title="% intención de voto",
        yaxis_range=[30, 60],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=20),
    )
    st.plotly_chart(_fig_polls, use_container_width=True)

    # Gráfico de evolución del margen
    _fig_margen = go.Figure()
    _margenes = (_poll_df["AE%"] - _poll_df["IC%"]).tolist()
    _fig_margen.add_trace(go.Scatter(
        x=_labels, y=_margenes,
        mode="lines+markers+text",
        text=[f"{v:+.1f}" for v in _margenes],
        textposition="top center",
        marker_color=["#1f77b4" if v > 0 else "#CC0000" for v in _margenes],
        marker_size=10,
        line_color="#C8A96E",
        name="Margen AE − IC",
    ))
    _fig_margen.add_hline(y=0, line_dash="dash", line_color="#666666",
                          annotation_text="Empate", annotation_position="right")
    _fig_margen.update_layout(
        height=300, title="Evolución del margen AE − IC por encuesta (pp)",
        yaxis_title="pp (positivo = AE lidera)", showlegend=False,
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(_fig_margen, use_container_width=True)

    # Gráfico mercados de predicción
    st.subheader("Mercados de predicción")
    _fig_pred = go.Figure()
    _fig_pred.add_trace(go.Bar(
        name="Polymarket (1 jun)", x=["AE", "IC"],
        y=[88, 13], marker_color=["#1f77b4", "#CC0000"],
        text=["88%", "13%"], textposition="outside",
    ))
    _fig_pred.add_trace(go.Bar(
        name="Kalshi (may)", x=["AE", "IC"],
        y=[43, 41], marker_color=["#5fa8e0", "#e06060"],
        text=["43%", "41%"], textposition="outside",
    ))
    _fig_pred.add_hline(y=50, line_dash="dot", line_color="#C8A96E",
                        annotation_text="50%", annotation_position="right")
    _fig_pred.update_layout(
        barmode="group", height=350,
        title="Probabilidad de ganar la 2ª vuelta (mercados de apuestas)",
        yaxis_title="% probabilidad", yaxis_range=[0, 100],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=60, b=20),
    )
    st.plotly_chart(_fig_pred, use_container_width=True)
    st.caption(
        "Polymarket post-1ª vuelta: AE 88% de probabilidad de ganar el 21 jun. "
        "Kalshi: pre-1ª vuelta, prácticamente empatados."
    )

    st.divider()

    v1 = {
        "PALOMA VALENCIA LASERNA":   1_637_665,
        "SERGIO FAJARDO VALDERRAMA": 1_007_943,
        "CLAUDIA LÓPEZ":               225_335,
        "OTROS":                       150_000,
    }
    ae_base = 10_346_212
    ic_base  =  9_682_199

    st.subheader("Tasas de transferencia (ajustables)")
    st.button("Restablecer a estimación base", on_click=_reset_proyeccion)
    cols = st.columns(4)
    fuentes = list(v1.keys())

    # Defaults: AE + IC + ABS = 100 en cada fila
    defaults_ae  = {"PALOMA VALENCIA LASERNA": 72, "SERGIO FAJARDO VALDERRAMA": 22,
                    "CLAUDIA LÓPEZ": 10, "OTROS": 35}
    defaults_ic  = {"PALOMA VALENCIA LASERNA":  6, "SERGIO FAJARDO VALDERRAMA": 48,
                    "CLAUDIA LÓPEZ": 58, "OTROS": 35}
    defaults_abs = {"PALOMA VALENCIA LASERNA": 22, "SERGIO FAJARDO VALDERRAMA": 30,
                    "CLAUDIA LÓPEZ": 32, "OTROS": 30}

    # Inicializar session_state con defaults solo si no existen aún
    for fuente in fuentes:
        for key, val in [(f"ae_{fuente}",  defaults_ae[fuente]),
                         (f"ic_{fuente}",  defaults_ic[fuente]),
                         (f"abs_{fuente}", defaults_abs[fuente])]:
            if key not in st.session_state:
                st.session_state[key] = val

    taus = {}
    for i, fuente in enumerate(fuentes):
        with cols[i]:
            label = fuente.split()[0]
            st.markdown(f"**{label}**")
            total_fuente = v1[fuente]
            st.caption(f"{total_fuente:,} votos disponibles")

            # AE: libre 0-100
            t_ae = st.slider("→ AE %", 0, 100, key=f"ae_{fuente}")

            # IC: clampeado al espacio restante tras AE
            max_ic = 100 - t_ae
            if st.session_state[f"ic_{fuente}"] > max_ic:
                st.session_state[f"ic_{fuente}"] = max_ic
            if max_ic > 0:
                t_ic = st.slider("→ IC %", 0, max_ic, key=f"ic_{fuente}")
            else:
                st.session_state[f"ic_{fuente}"] = 0
                t_ic = 0
                st.caption("→ IC %: **0%** (AE ocupa el 100%)")

            # ABS: clampeado al espacio restante tras AE+IC
            max_abs = 100 - t_ae - t_ic
            if st.session_state[f"abs_{fuente}"] > max_abs:
                st.session_state[f"abs_{fuente}"] = max_abs
            if max_abs > 0:
                t_abs = st.slider("→ Abstención %", 0, max_abs, key=f"abs_{fuente}")
            else:
                st.session_state[f"abs_{fuente}"] = 0
                t_abs = 0
                st.caption("→ Abstención %: **0%** (AE+IC ocupan el 100%)")

            restante  = 100 - t_ae - t_ic - t_abs
            votos_ae  = int(total_fuente * t_ae  / 100)
            votos_ic  = int(total_fuente * t_ic  / 100)
            votos_abs = int(total_fuente * t_abs / 100)
            votos_nr  = int(total_fuente * restante / 100)

            st.caption(
                f"AE: **{votos_ae:,}**  ·  IC: **{votos_ic:,}**  ·  "
                f"Abs: **{votos_abs:,}**"
                + (f"  ·  Sin asignar: {restante}% ({votos_nr:,})" if restante else "")
            )
            taus[fuente] = (t_ae / 100, t_ic / 100, t_abs / 100)

    ae_extra = sum(v1[f] * taus[f][0] for f in fuentes)
    ic_extra = sum(v1[f] * taus[f][1] for f in fuentes)

    # ── Nuevos votantes segunda vuelta ───────────────────────────────────────
    st.divider()
    st.subheader("Nuevos votantes en segunda vuelta")
    st.caption(
        "En segunda vuelta suelen participar entre 1 y 2 millones de personas adicionales "
        "que no votaron en la primera. Ajusta cuántos llegan y cómo se reparten."
    )

    if "nuevos_total" not in st.session_state:
        st.session_state["nuevos_total"] = 1_500_000
    if "nuevos_abs_pct" not in st.session_state:
        st.session_state["nuevos_abs_pct"] = 15
    if "nuevos_ae_pct" not in st.session_state:
        st.session_state["nuevos_ae_pct"] = 48

    cn1, cn2, cn3 = st.columns(3)
    with cn1:
        nuevos_total = st.slider(
            "Nuevos votantes potenciales",
            min_value=500_000, max_value=4_000_000,
            step=50_000, key="nuevos_total",
            format="%,d",
            help="Personas que no votaron en primera vuelta pero podrían votar en segunda",
        )
    with cn2:
        nuevos_abs_pct = st.slider(
            "% que no participa (abstención)",
            min_value=0, max_value=80,
            step=1, key="nuevos_abs_pct",
            help="Fracción de los nuevos potenciales que finalmente no vota en segunda vuelta",
        )
    with cn3:
        _ae_max = 100 - nuevos_abs_pct
        nuevos_ae_pct_raw = st.slider(
            "% de los que sí votan → Abelardo",
            min_value=0, max_value=100,
            step=1, key="nuevos_ae_pct",
            help="Del subgrupo que sí participa, qué fracción va a Abelardo. El resto va a Cepeda.",
        )

    _nuevos_participan = int(nuevos_total * (1 - nuevos_abs_pct / 100))
    nuevos_ae  = int(_nuevos_participan * nuevos_ae_pct_raw / 100)
    nuevos_ic  = _nuevos_participan - nuevos_ae
    _nuevos_no_votan = nuevos_total - _nuevos_participan
    st.caption(
        f"De **{nuevos_total:,}** potenciales: **{_nuevos_participan:,}** votan — "
        f"AE **{nuevos_ae:,}** · IC **{nuevos_ic:,}** — "
        f"abstienen **{_nuevos_no_votan:,}**"
    )

    ae_total = ae_base + ae_extra + nuevos_ae
    ic_total = ic_base + ic_extra + nuevos_ic
    total    = ae_total + ic_total
    ae_pct   = ae_total / total * 100
    ic_pct   = ic_total / total * 100

    st.divider()
    st.subheader("Resultado proyectado")

    ganador   = "ABELARDO DE LA ESPRIELLA" if ae_total > ic_total else "IVÁN CEPEDA CASTRO"
    margen    = abs(ae_total - ic_total)
    win_color = "#1f77b4" if ae_total > ic_total else "#CC0000"

    st.markdown(
        f"""<div style="background:{win_color}; padding:16px 24px; border-radius:10px;
                        color:white; font-size:1.25em; font-weight:600; margin-bottom:12px;">
            GANA: {ganador} &nbsp;&nbsp;|&nbsp;&nbsp;
            Margen: {margen:,.0f} votos &nbsp;&nbsp;|&nbsp;&nbsp;
            AE {ae_pct:.1f}% &nbsp;–&nbsp; IC {ic_pct:.1f}%
        </div>""",
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("ABELARDO – 1ª Vuelta",    f"{ae_base:,}")
    c2.metric("ABELARDO – Transferencias", f"+{int(ae_extra):,}")
    c3.metric("CEPEDA – 1ª Vuelta",      f"{ic_base:,}")
    c4.metric("CEPEDA – Transferencias",  f"+{int(ic_extra):,}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("ABELARDO – Nuevos",  f"+{nuevos_ae:,}")
    c6.metric("ABELARDO TOTAL",     f"{ae_total:,.0f}", f"{ae_pct:.1f}%")
    c7.metric("CEPEDA – Nuevos",    f"+{nuevos_ic:,}")
    c8.metric("CEPEDA TOTAL",       f"{ic_total:,.0f}", f"{ic_pct:.1f}%")

    fig = go.Figure()
    fig.add_bar(name="1ª vuelta",
                x=["ABELARDO", "CEPEDA"],
                y=[ae_base, ic_base],
                marker_color=["#1f77b4", "#CC0000"], opacity=0.45,
                text=[f"{ae_base:,}", f"{ic_base:,}"],
                textposition="inside")
    fig.add_bar(name="+ Transferencias",
                x=["ABELARDO", "CEPEDA"],
                y=[int(ae_extra), int(ic_extra)],
                marker_color=["#5fa8e0", "#e06060"], opacity=0.85,
                text=[f"+{int(ae_extra):,}", f"+{int(ic_extra):,}"],
                textposition="inside")
    fig.add_bar(name=f"+ Nuevos votantes ({nuevos_total/1e6:.1f}M)",
                x=["ABELARDO", "CEPEDA"],
                y=[nuevos_ae, nuevos_ic],
                marker_color=["#aad4f5", "#f5aaaa"], opacity=0.95,
                text=[f"+{nuevos_ae:,}", f"+{nuevos_ic:,}"],
                textposition="inside")
    fig.update_layout(
        barmode="stack", height=480,
        yaxis_title="Votos",
        title="Segunda Vuelta proyectada – Composición de votos",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        annotations=[
            dict(x="ABELARDO", y=ae_total, text=f"<b>{ae_total:,}</b> ({ae_pct:.1f}%)",
                 showarrow=False, yanchor="bottom", font=dict(size=13, color="#1f77b4")),
            dict(x="CEPEDA",   y=ic_total, text=f"<b>{ic_total:,}</b> ({ic_pct:.1f}%)",
                 showarrow=False, yanchor="bottom", font=dict(size=13, color="#CC0000")),
        ],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Detalle de transferencias")
    rows = []
    for f in fuentes:
        t_ae, t_ic, t_abs = taus[f]
        rows.append({
            "Fuente":       f,
            "Votos 1ª":     f"{v1[f]:,}",
            "→ AE":         f"{v1[f]*t_ae:,.0f}  ({t_ae*100:.0f}%)",
            "→ IC":         f"{v1[f]*t_ic:,.0f}  ({t_ic*100:.0f}%)",
            "Abstención":   f"{v1[f]*t_abs:,.0f}  ({t_abs*100:.0f}%)",
        })
    rows.append({
        "Fuente":     "TOTAL TRANSFERENCIAS",
        "Votos 1ª":   f"{sum(v1.values()):,}",
        "→ AE":       f"{ae_extra:,.0f}",
        "→ IC":       f"{ic_extra:,.0f}",
        "Abstención": "",
    })
    rows.append({
        "Fuente":     f"NUEVOS VOTANTES potenciales ({nuevos_total:,})",
        "Votos 1ª":   "—",
        "→ AE":       f"{nuevos_ae:,}  ({nuevos_ae_pct_raw}% de votantes)",
        "→ IC":       f"{nuevos_ic:,}  ({100-nuevos_ae_pct_raw}% de votantes)",
        "Abstención": f"{_nuevos_no_votan:,}  ({nuevos_abs_pct}%)",
    })
    rows.append({
        "Fuente":     "TOTAL PROYECTADO",
        "Votos 1ª":   f"{ae_base + ic_base:,}",
        "→ AE":       f"{ae_total:,.0f}  ({ae_pct:.1f}%)",
        "→ IC":       f"{ic_total:,.0f}  ({ic_pct:.1f}%)",
        "Abstención": "",
    })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7 – SOLO ANTIOQUIA
# ═══════════════════════════════════════════════════════════════════════════════
with t_antioquia:
    st.title("Análisis Detallado – Antioquia")

    ant = mun[mun["dept_co"] == 1].copy()
    ant_df = df[df["dept_co"] == 1].copy()

    if ant.empty:
        st.warning("No hay datos de Antioquia.")
    else:
        # Métricas
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Municipios",        f"{len(ant):,}")
        c2.metric("Total votantes",    f"{ant['total_votantes'].sum():,}")
        c3.metric("Votos AE",          f"{ant['votos_AE'].sum():,}")
        c4.metric("Votos IC",          f"{ant['votos_IC'].sum():,}")

        munis_ae_ant = (ant["gana_AE"] == 1).sum()
        munis_ic_ant = (ant["gana_AE"] == 0).sum()
        c5, c6, c7 = st.columns(3)
        c5.metric("Municipios ganados AE",
                  f"{munis_ae_ant} / {len(ant)}",
                  f"{munis_ae_ant/len(ant)*100:.0f}%",
                  delta_color="off")
        c6.metric("Municipios ganados IC",
                  f"{munis_ic_ant} / {len(ant)}",
                  f"{munis_ic_ant/len(ant)*100:.0f}%",
                  delta_color="inverse")
        diff_total = int(ant["votos_AE"].sum() - ant["votos_IC"].sum())
        c7.metric("Diferencia AE – IC", f"{diff_total:+,}",
                  "AE gana" if diff_total > 0 else "IC gana",
                  delta_color="off")

        st.divider()

        # ── Mapa municipal Antioquia ─────────────────────────────────────────
        st.subheader("Mapa: ganador por municipio – Antioquia")

        ant_map = ant[ant["divipola_muni"] != ""].copy()
        fig_ant_map = px.choropleth(
            ant_map,
            geojson=geo_ant,
            locations="divipola_muni",
            featureidkey="properties.MPIO_CCNCT",
            color="ganador",
            color_discrete_map=GANADOR_COLORS,
            hover_name="muni_nombre",
            hover_data={
                "votos_AE": ":,",
                "votos_IC": ":,",
                "diff_AE_IC": ":,",
                "pct_AE": ":.1f",
                "pct_IC": ":.1f",
                "divipola_muni": False,
            },
            labels={"ganador": "Ganador", "diff_AE_IC": "Diferencia AE−IC",
                    "pct_AE": "% AE", "pct_IC": "% IC"},
        )
        # Antioquia: bounds específicos para la región
        fig_ant_map.update_geos(
            visible=False,
            lataxis_range=[5.3, 8.9],
            lonaxis_range=[-77.2, -73.8],
            projection_type="mercator",
        )
        fig_ant_map.update_layout(
            height=580, margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            dragmode=False, autosize=True,
            geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False),
        )
        st.plotly_chart(fig_ant_map, use_container_width=True, config=_MAP_CFG)

        # ── Barra: municipios por % AE, coloreados por ganador ──────────────
        st.subheader("Todos los municipios de Antioquia – % AE vs % IC")
        ant_plot = ant.sort_values("pct_AE", ascending=False).copy()

        fig_ant = go.Figure()
        fig_ant.add_bar(
            x=ant_plot["muni_nombre"],
            y=ant_plot["pct_AE"],
            name="% AE",
            marker_color="#1f77b4",
            hovertemplate="%{x}<br>AE: %{y:.1f}%<extra></extra>",
        )
        fig_ant.add_bar(
            x=ant_plot["muni_nombre"],
            y=ant_plot["pct_IC"],
            name="% IC",
            marker_color="#CC0000",
            hovertemplate="%{x}<br>IC: %{y:.1f}%<extra></extra>",
        )
        fig_ant.update_layout(
            barmode="group",
            height=500,
            xaxis_tickangle=-60,
            xaxis={"tickfont": {"size": 8}},
            legend_title="Candidato",
            yaxis_title="% Votos",
            margin=dict(b=140),
        )
        st.plotly_chart(fig_ant, use_container_width=True)

        # ── Barra: Paloma por municipio ──────────────────────────────────────
        st.subheader("Todos los municipios de Antioquia – % Paloma Valencia")
        ant_pal = ant.sort_values("pct_Valencia", ascending=False).copy()

        fig_ant_pal = go.Figure()
        fig_ant_pal.add_bar(
            x=ant_pal["muni_nombre"],
            y=ant_pal["pct_Valencia"],
            name="% Paloma",
            marker_color="#2ca02c",
            hovertemplate="%{x}<br>Paloma: %{y:.1f}%<extra></extra>",
        )
        fig_ant_pal.add_bar(
            x=ant_pal["muni_nombre"],
            y=ant_pal["pct_AE"],
            name="% AE",
            marker_color="#1f77b4",
            opacity=0.55,
            hovertemplate="%{x}<br>AE: %{y:.1f}%<extra></extra>",
        )
        fig_ant_pal.add_bar(
            x=ant_pal["muni_nombre"],
            y=ant_pal["pct_IC"],
            name="% IC",
            marker_color="#CC0000",
            opacity=0.55,
            hovertemplate="%{x}<br>IC: %{y:.1f}%<extra></extra>",
        )
        fig_ant_pal.update_layout(
            barmode="group",
            height=500,
            xaxis_tickangle=-60,
            xaxis={"tickfont": {"size": 8}},
            legend_title="Candidato",
            yaxis_title="% Votos",
            margin=dict(b=140),
        )
        st.plotly_chart(fig_ant_pal, use_container_width=True)

        # ── Top municipios AE vs IC ──────────────────────────────────────────
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Mejores municipios de AE en Antioquia")
            top_ae = ant.nlargest(20, "pct_AE")[
                ["muni_nombre", "votos_AE", "pct_AE", "pct_IC", "diff_AE_IC"]
            ].reset_index(drop=True)
            fig_ta = px.bar(
                top_ae.sort_values("pct_AE", ascending=True),
                x="pct_AE", y="muni_nombre", orientation="h",
                color_discrete_sequence=["#1f77b4"],
                labels={"pct_AE": "% AE", "muni_nombre": ""},
            )
            fig_ta.update_layout(height=500, margin=dict(l=0, r=20, t=10, b=0),
                                 yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_ta, use_container_width=True)

        with col_b:
            st.subheader("Mejores municipios de IC en Antioquia")
            top_ic = ant.nlargest(20, "pct_IC")[
                ["muni_nombre", "votos_IC", "pct_IC", "pct_AE", "diff_AE_IC"]
            ].reset_index(drop=True)
            fig_ti = px.bar(
                top_ic.sort_values("pct_IC", ascending=True),
                x="pct_IC", y="muni_nombre", orientation="h",
                color_discrete_sequence=["#CC0000"],
                labels={"pct_IC": "% IC", "muni_nombre": ""},
            )
            fig_ti.update_layout(height=500, margin=dict(l=0, r=20, t=10, b=0),
                                 yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig_ti, use_container_width=True)

        # ── Scatter Margen AE−IC vs Participación ─────────────────────────
        ant_sc = ant.copy()
        ant_sc["margen_AE"] = ant_sc["pct_AE"] - ant_sc["pct_IC"]
        _r_ant_margen = ant_sc["margen_AE"].corr(ant_sc["pct_participacion"])
        st.subheader(f"Margen AE−IC vs Participación – Antioquia  (r = {_r_ant_margen:+.2f})")
        fig_sc = px.scatter(
            ant_sc, x="margen_AE", y="pct_participacion",
            hover_name="muni_nombre",
            hover_data={
                "margen_AE": ":.1f",
                "pct_participacion": ":.1f",
                "votos_AE": ":,",
                "votos_IC": ":,",
                "ganador": True,
            },
            color="ganador",
            color_discrete_map=GANADOR_COLORS,
            labels={
                "margen_AE": "Margen AE − IC (pp)",
                "pct_participacion": "% Participación",
                "ganador": "Ganador",
            },
            opacity=0.75,
            size="votos_AE",
        )
        fig_sc.add_vline(x=0, line_dash="dot", line_color="gray", opacity=0.5)
        add_trend(fig_sc, ant_sc["margen_AE"], ant_sc["pct_participacion"], color="black", name="Tendencia")
        fig_sc.update_layout(
            height=450,
            xaxis_title="Margen AE − IC (puntos porcentuales)",
            yaxis_title="% Participación",
            title="Margen AE−IC vs Participación – Municipios Antioquia",
        )
        st.plotly_chart(fig_sc, use_container_width=True)

        # ── Tabla coalición Antioquia ─────────────────────────────────────
        st.subheader("Conversión con coalición – Antioquia")
        st.caption("Muestra si sumar a Paloma + Fajardo a AE cambia el resultado municipio a municipio")

        coal_ant = ant[[
            "muni_nombre", "votos_AE", "votos_IC", "votos_Valencia",
            "votos_Fajardo", "votos_coalicion_AE",
            "diff_AE_IC", "diff_coalicion_IC", "gana_AE", "gana_coalicion",
        ]].sort_values("diff_AE_IC", ascending=True).reset_index(drop=True).copy()

        coal_ant["Conversión"] = coal_ant.apply(
            lambda r: "Revierte" if (r["gana_AE"] == 0 and r["gana_coalicion"] == 1)
                      else ("Mantiene" if r["gana_AE"] == 1 else "Sin cambio"),
            axis=1,
        )

        for c in ["votos_AE", "votos_IC", "votos_Valencia",
                  "votos_Fajardo", "votos_coalicion_AE"]:
            coal_ant[c] = coal_ant[c].apply(lambda v: f"{v:,.0f}")
        coal_ant["diff_AE_IC"]       = coal_ant["diff_AE_IC"].apply(lambda v: f"{v:+,.0f}")
        coal_ant["diff_coalicion_IC"] = coal_ant["diff_coalicion_IC"].apply(lambda v: f"{v:+,.0f}")

        coal_ant = coal_ant.drop(columns=["gana_AE", "gana_coalicion"])
        coal_ant.columns = [
            "Municipio", "V. AE", "V. IC", "V. Paloma", "V. Fajardo",
            "V. Coalición", "Dif AE–IC", "Dif Coal–IC", "Resultado",
        ]
        st.dataframe(coal_ant, use_container_width=True, hide_index=True)

        # ── Tabla completa ────────────────────────────────────────────────
        st.subheader("Tabla completa – Antioquia")
        tabla_ant = ant[[
            "muni_nombre", "total_votantes", "votos_AE", "pct_AE",
            "votos_IC", "pct_IC", "votos_Valencia", "votos_Fajardo",
            "diff_AE_IC", "ganador",
        ]].sort_values("votos_AE", ascending=False).reset_index(drop=True).copy()

        tabla_ant["total_votantes"]  = tabla_ant["total_votantes"].apply(lambda v: f"{v:,.0f}")
        tabla_ant["votos_AE"]        = tabla_ant["votos_AE"].apply(lambda v: f"{v:,.0f}")
        tabla_ant["votos_IC"]        = tabla_ant["votos_IC"].apply(lambda v: f"{v:,.0f}")
        tabla_ant["votos_Valencia"]  = tabla_ant["votos_Valencia"].apply(lambda v: f"{v:,.0f}")
        tabla_ant["votos_Fajardo"]   = tabla_ant["votos_Fajardo"].apply(lambda v: f"{v:,.0f}")
        tabla_ant["pct_AE"]          = tabla_ant["pct_AE"].apply(lambda v: f"{v:.1f}%")
        tabla_ant["pct_IC"]          = tabla_ant["pct_IC"].apply(lambda v: f"{v:.1f}%")
        tabla_ant["diff_AE_IC"]      = tabla_ant["diff_AE_IC"].apply(lambda v: f"{v:+,.0f}")
        tabla_ant.columns = [
            "Municipio", "Votantes", "Votos AE", "% AE",
            "Votos IC", "% IC", "Votos Paloma", "Votos Fajardo",
            "Dif AE-IC", "Ganador",
        ]
        st.dataframe(tabla_ant, use_container_width=True, hide_index=True)

# ── Pie de página ─────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Fuente: Registraduría Nacional del Estado Civil – Preconteo 31 mayo 2026 · "
    "Datos actualizados al 99.92% de mesas informadas · "
    "Código: github.com/carfmono/elecciones-2026"
)
