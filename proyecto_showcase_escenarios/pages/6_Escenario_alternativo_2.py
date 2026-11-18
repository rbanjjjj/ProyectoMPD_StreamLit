import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import streamlit as st
from utils.pipeline import (
    aplicar_estilos_streamlit,
    configurar_matplotlib,
    renderizar_sidebar_carga,
    obtener_demanda_mensual,
    calcular_modelos_rodrigo,
    calcular_modelo_luis,
    simular_escenario_predictivo,
    etiqueta_mes,
    PALETA,
)

st.set_page_config(page_title="Escenario alternativo 2", page_icon="📈", layout="wide")
aplicar_estilos_streamlit()
configurar_matplotlib()
renderizar_sidebar_carga()

st.markdown(
    """
    <div class="showcase-banner">
        <h1>Escenario alternativo 2</h1>
        <p>Modelo predictivo ante choque estacional de alta demanda (+15 % en meses pico: Ene, Jun, Jul, Ago)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="method-card">
        <strong>Enfoque predictivo del escenario:</strong> Se recalibran los dos modelos predictivos de demanda
        (<strong>OLS con dummies estacionales</strong> y <strong>Holt-Winters aditivo</strong>) incorporando un choque positivo
        del <strong>+15 % en los meses de mayor estacionalidad histórica (Enero, Junio, Julio y Agosto)</strong>,
        midiendo el desplazamiento en la demanda proyectada, la rotación mensual y los días de cobertura.
    </div>
    """,
    unsafe_allow_html=True,
)

_, mensual_dem = obtener_demanda_mensual()

if mensual_dem is None:
    st.info("⬅️ Sube la **Base de Demanda (`demanda_limpio.csv`)** en la **Ranura 1** de la barra lateral para ejecutar este escenario predictivo.")
    st.stop()

MESES_PICO = [1, 6, 7, 8]
FACTOR_PICO = 1.15
COB_MIN, COB_MAX = 27, 33

# 1. Recalibración predictiva OLS Estacional (Rodrigo) bajo choque estacional
_, _, df_ols_base = calcular_modelos_rodrigo(mensual_dem)
proy_ols = df_ols_base[df_ols_base["Tipo"] == "Proyección"].copy().reset_index(drop=True)
proy_ols["OLS_Escenario2"] = np.where(
    proy_ols["Month_Num"].isin(MESES_PICO),
    proy_ols["OLS_Estacional"] * FACTOR_PICO,
    proy_ols["OLS_Estacional"],
)

# 2. Recalibración predictiva Holt-Winters (Luis -> Nicole)
df_luis = calcular_modelo_luis(mensual_dem)
sim_df, d_prom, _ = simular_escenario_predictivo(
    df_luis, f_dem=1.00, meses_pico=MESES_PICO, f_pico=FACTOR_PICO, f_stock=1.00
)

# KPIs ejecutivos
incremento_total = (sim_df["demanda_esc"] - sim_df["demanda_base"]).sum()
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Demanda Extra Proy. (12m)</div><div class="kpi-value">+{incremento_total:,.0f} u</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Pico Máximo Holt-Winters</div><div class="kpi-value">{sim_df["demanda_esc"].max():,.0f} u</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Rotación Máx. Predicha</div><div class="kpi-value">{sim_df["rotacion_esc"].max():.2f}x</div></div>', unsafe_allow_html=True)
with c4:
    meses_alerta = int((sim_df["cobertura_esc"] < COB_MIN).sum())
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Meses Bajo Meta (&lt;27d)</div><div class="kpi-value">{meses_alerta} / 12</div></div>', unsafe_allow_html=True)

st.write("")

# Gráfico comparativo de dos paneles: Modelos Predictivos (OLS vs HW) + Cobertura resultante
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2))
x = np.arange(len(sim_df))
etiquetas_x = [etiqueta_mes(f) for f in sim_df["fecha"]]

# Panel 1: Comparación de trayectorias predictivas (Holt-Winters y OLS Estacional)
ax1.plot(x, sim_df["demanda_base"], color=PALETA["espresso"], lw=2.0, marker="o", ms=4, label="Holt-Winters Base")
ax1.plot(x, sim_df["demanda_esc"], color=PALETA["primario_oscuro"], lw=2.5, linestyle="--", marker="s", ms=5, label="Holt-Winters Escenario 2 (+15 % pico)")
ax1.plot(x, proy_ols["OLS_Escenario2"], color=PALETA["gris"], lw=1.9, linestyle=":", marker="^", ms=4.5, label="OLS Estacional Escenario 2")

# Resaltar meses pico
for i, m in enumerate(sim_df["fecha"].dt.month):
    if m in MESES_PICO:
        ax1.axvspan(i - 0.35, i + 0.35, color=PALETA["primario"], alpha=0.28)

ax1.set_title("1) Trayectorias Predictivas de Demanda (12 meses)")
ax1.set_xlabel("Mes proyectado (sombreado = meses pico)")
ax1.set_ylabel("Unidades proyectadas")
ax1.set_xticks(x)
ax1.set_xticklabels(etiquetas_x, rotation=45)
ax1.legend(frameon=False, loc="lower left", fontsize=9.5)

# Panel 2: Días de cobertura bajo choque estacional
ax2.axhspan(COB_MIN, COB_MAX, color=PALETA["verde"], alpha=0.15, label="Zona meta (27–33 días)")
ax2.plot(x, sim_df["cobertura_base"], color=PALETA["espresso"], lw=2.0, marker="o", label="Cobertura Base")
ax2.plot(x, sim_df["cobertura_esc"], color=PALETA["primario_oscuro"], lw=2.4, linestyle="--", marker="s", label="Cobertura Escenario 2")
ax2.axhline(COB_MIN, color=PALETA["rojo"], linestyle=":", lw=1.3)
ax2.set_title("2) Impacto en Cobertura por Aceleración de Rotación")
ax2.set_xlabel("Mes proyectado")
ax2.set_ylabel("Días de cobertura")
ax2.set_xticks(x)
ax2.set_xticklabels(etiquetas_x, rotation=45)
ax2.legend(frameon=False, loc="upper right", fontsize=9.5)

fig.tight_layout()
st.pyplot(fig)

# Tabla de resultados predictivos
st.subheader("Proyección Mensual Comparativa — Escenario Alternativo 2")
tabla_e2 = pd.DataFrame({
    "Mes": etiquetas_x,
    "HW Base (u)": sim_df["demanda_base"].round(0).astype(int),
    "HW Escenario 2 (u)": sim_df["demanda_esc"].round(0).astype(int),
    "OLS Escenario 2 (u)": proy_ols["OLS_Escenario2"].round(0).astype(int),
    "Rotación Esc. 2": sim_df["rotacion_esc"].round(2),
    "Cobertura Esc. 2 (días)": sim_df["cobertura_esc"].round(1),
})
st.dataframe(tabla_e2, use_container_width=True, hide_index=True)