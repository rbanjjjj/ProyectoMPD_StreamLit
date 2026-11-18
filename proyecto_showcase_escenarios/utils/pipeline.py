import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import streamlit as st

# Paleta cromática centrada en #FFCA87
PALETA = {
    "primario": "#FFCA87",        # Ámbar dorado principal
    "primario_oscuro": "#D97724", # Naranja tostado para líneas y énfasis
    "espresso": "#2C1E12",        # Marrón oscuro para series históricas y texto
    "crema": "#FFFDF9",           # Fondo limpio
    "arena": "#FFF4E3",           # Tarjetas y sombreados suaves
    "borde": "#F3B664",           # Contornos
    "verde": "#2E9E5B",           # Estado óptimo / meta
    "ambar": "#F2A900",           # Alerta / exceso
    "rojo": "#D64545",            # Riesgo de quiebre
    "gris": "#7A6A58",            # Referencias neutras
}

MESES_ES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def aplicar_estilos_streamlit():
    """Inyecta CSS personalizado alrededor del color #FFCA87."""
    st.markdown(
        f"""
        <style>
        .showcase-banner {{
            background: linear-gradient(135deg, {PALETA['primario']} 0%, #FFE4BE 100%);
            padding: 1.4rem 1.8rem;
            border-radius: 14px;
            border-left: 7px solid {PALETA['primario_oscuro']};
            color: {PALETA['espresso']};
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 14px rgba(44, 30, 18, 0.06);
        }}
        .showcase-banner h1 {{
            margin: 0;
            font-size: 1.85rem;
            font-weight: 800;
            color: {PALETA['espresso']};
        }}
        .showcase-banner p {{
            margin: 0.35rem 0 0 0;
            font-size: 1.05rem;
            font-weight: 500;
            opacity: 0.92;
        }}
        .method-card {{
            background-color: {PALETA['arena']};
            border: 1px solid {PALETA['primario']};
            border-radius: 10px;
            padding: 1rem 1.2rem;
            margin-bottom: 1.2rem;
            color: {PALETA['espresso']};
        }}
        .kpi-box {{
            background-color: #FFFFFF;
            border: 1.5px solid {PALETA['primario']};
            border-top: 5px solid {PALETA['primario_oscuro']};
            border-radius: 10px;
            padding: 0.85rem 1rem;
            text-align: center;
        }}
        .kpi-label {{
            font-size: 0.82rem;
            color: {PALETA['gris']};
            font-weight: 600;
            text-transform: uppercase;
        }}
        .kpi-value {{
            font-size: 1.45rem;
            font-weight: 800;
            color: {PALETA['espresso']};
            margin-top: 0.2rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def configurar_matplotlib():
    """Homogeniza la estética de todos los gráficos de Matplotlib."""
    plt.rcParams.update({
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#D6C5B3",
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.color": "#C9B7A2",
        "axes.titleweight": "bold",
        "axes.titlesize": 14,
        "axes.titlelocation": "left",
        "axes.titlecolor": PALETA["espresso"],
        "axes.labelcolor": PALETA["espresso"],
        "xtick.color": PALETA["espresso"],
        "ytick.color": PALETA["espresso"],
        "figure.facecolor": "white",
        "axes.facecolor": "#FFFDFB",
    })


def etiqueta_mes(fecha):
    return f"{MESES_ES[fecha.month - 1]}-{str(fecha.year)[2:]}"


def renderizar_sidebar_carga():
    """Renderiza las 2 ranuras de carga de CSV en la barra lateral y guarda en session_state."""
    if "df_demanda_raw" not in st.session_state:
        st.session_state["df_demanda_raw"] = None
    if "df_abastecimiento_raw" not in st.session_state:
        st.session_state["df_abastecimiento_raw"] = None

    with st.sidebar:
        st.markdown("### 📂 Carga de Bases de Datos")
        st.caption("Sube los archivos CSV para habilitar los modelos del showcase:")

        # RANURA 1: Demanda (Rodrigo, Luis, Nicole y Escenarios)
        archivo_dem = st.file_uploader(
            "1️⃣ Base de Demanda (demanda_limpio.csv)",
            type=["csv"],
            key="uploader_demanda",
            help="Alimenta los modelos de Rodrigo, Luis, Nicole y Escenarios.",
        )
        if archivo_dem is not None:
            st.session_state["df_demanda_raw"] = pd.read_csv(archivo_dem)

        if st.session_state["df_demanda_raw"] is not None:
            st.success(f"Demanda cargada ({len(st.session_state['df_demanda_raw']):,} filas)")
        else:
            st.warning("Pendiente: Base de Demanda")

        st.markdown("---")

        # RANURA 2: Abastecimiento (Emily y Escenario 1)
        archivo_proc = st.file_uploader(
            "2️⃣ Base de Abastecimiento (Gestion_de_abastecimiento.csv)",
            type=["csv"],
            key="uploader_abastecimiento",
            help="Alimenta el análisis de inventario de Emily y Escenario 1.",
        )
        if archivo_proc is not None:
            st.session_state["df_abastecimiento_raw"] = pd.read_csv(archivo_proc)

        if st.session_state["df_abastecimiento_raw"] is not None:
            st.success(f"Abastecimiento cargado ({len(st.session_state['df_abastecimiento_raw']):,} filas)")
        else:
            st.warning("Pendiente: Base de Abastecimiento")


def obtener_demanda_mensual():
    """Procesa el DataFrame cargado en la Ranura 1."""
    df_raw = st.session_state.get("df_demanda_raw")
    if df_raw is None:
        return None, None

    df = df_raw.copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    if "anio" not in df.columns:
        df["anio"] = df["Order_Date"].dt.year
    if "numero_mes" not in df.columns:
        df["numero_mes"] = df["Order_Date"].dt.month

    mensual = (
        df.groupby(["anio", "numero_mes"], as_index=False)["Order_Quantity"]
        .sum()
        .rename(columns={"anio": "Year_Num", "numero_mes": "Month_Num"})
    )
    mensual["fecha"] = pd.to_datetime(
        mensual["Year_Num"].astype(str)
        + "-"
        + mensual["Month_Num"].astype(str).str.zfill(2)
        + "-01"
    )
    mensual = mensual.sort_values("fecha").reset_index(drop=True)
    mensual["t"] = np.arange(1, len(mensual) + 1)
    mensual["dias"] = mensual["fecha"].dt.days_in_month
    return df, mensual


def obtener_abastecimiento_mensual():
    """Procesa el DataFrame cargado en la Ranura 2 para modelado predictivo de suministro."""
    df_raw = st.session_state.get("df_abastecimiento_raw")
    if df_raw is None:
        return None, None

    df = df_raw.copy()
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["fecha"] = df["Order_Date"].dt.to_period("M").dt.to_timestamp()
    mensual = (
        df.groupby("fecha", as_index=False)["Order_Quantity"]
        .sum()
        .sort_values("fecha")
        .reset_index(drop=True)
    )
    mensual["t"] = np.arange(1, len(mensual) + 1)
    return df, mensual


def calcular_modelos_rodrigo(mensual):
    """Homogeniza los modelos OLS simple y OLS estacional de Rodrigo."""
    ols_simple = smf.ols("Order_Quantity ~ t", data=mensual).fit()
    ols_estacional = smf.ols("Order_Quantity ~ t + C(Month_Num)", data=mensual).fit()

    fechas_proy = pd.date_range(
        start=mensual["fecha"].max() + pd.offsets.MonthBegin(1),
        periods=12,
        freq="MS",
    )
    df_futuro = pd.DataFrame({
        "fecha": fechas_proy,
        "Year_Num": fechas_proy.year,
        "Month_Num": fechas_proy.month,
        "t": np.arange(len(mensual) + 1, len(mensual) + 13),
        "Order_Quantity": np.nan,
        "Tipo": "Proyección",
    })
    df_hist = mensual[["fecha", "Year_Num", "Month_Num", "t", "Order_Quantity"]].copy()
    df_hist["Tipo"] = "Histórico"

    df_total = pd.concat([df_hist, df_futuro], ignore_index=True)
    df_total["OLS_Simple"] = ols_simple.predict(df_total)
    df_total["OLS_Estacional"] = ols_estacional.predict(df_total)

    return ols_simple, ols_estacional, df_total


def calcular_modelo_luis(mensual):
    """Homogeniza el modelo Holt-Winters Estacional (12 meses) de Luis."""
    serie_ts = mensual.set_index("fecha")["Order_Quantity"].asfreq("MS")

    modelo_hw = ExponentialSmoothing(
        serie_ts,
        trend="add",
        seasonal="add",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit()

    forecast = modelo_hw.forecast(12)

    df_hist = pd.DataFrame({
        "fecha": serie_ts.index,
        "demanda": serie_ts.values,
        "tipo": "Histórico",
    })
    df_proy = pd.DataFrame({
        "fecha": forecast.index,
        "demanda": forecast.values,
        "tipo": "Proyección",
    })
    df_final = pd.concat([df_hist, df_proy], ignore_index=True)
    df_final["dias"] = df_final["fecha"].dt.days_in_month
    return df_final


def simular_escenario_predictivo(df_luis, f_dem=1.0, meses_pico=None, f_pico=1.0, f_stock=1.0, cob_objetivo=30):
    """Aplica perturbaciones predictivas sobre el pronóstico Holt-Winters y calcula rotación/cobertura."""
    if meses_pico is None:
        meses_pico = []

    d_prom = df_luis["demanda"].mean()
    proy = df_luis[df_luis["tipo"] == "Proyección"].copy().reset_index(drop=True)

    # Demanda base vs escenario
    proy["demanda_base"] = proy["demanda"]
    proy["demanda_esc"] = proy["demanda"] * f_dem
    es_pico = proy["fecha"].dt.month.isin(meses_pico)
    proy.loc[es_pico, "demanda_esc"] *= f_pico

    # Rotación y cobertura base
    proy["rotacion_base"] = proy["demanda_base"] / d_prom
    proy["cobertura_base"] = proy["dias"] / proy["rotacion_base"]

    # Rotación y cobertura bajo escenario predictivo
    stock_disponible = d_prom * f_stock
    proy["rotacion_esc"] = proy["demanda_esc"] / d_prom
    proy["cobertura_esc"] = (proy["dias"] / proy["rotacion_esc"]) * f_stock
    proy["stock_necesario"] = proy["demanda_esc"] * cob_objetivo / proy["dias"]
    proy["faltante_u"] = (proy["stock_necesario"] - stock_disponible).clip(lower=0)

    return proy, d_prom, stock_disponible