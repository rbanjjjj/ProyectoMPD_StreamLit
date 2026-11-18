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
    obtener_abastecimiento_mensual,
    calcular_modelo_luis,
    simular_escenario_predictivo,
    etiqueta_mes,
    PALETA,
)

st.set_page_config(page_title="Escenario alternativo 1", page_icon="⚠️", layout="wide")
aplicar_estilos_streamlit()
configurar_matplotlib()
renderizar_sidebar_carga()

st.markdown(
    """
    <div class="showcase-banner">
        <h1>Escenario alternativo 1</h1>
        <p>Modelo predictivo de suministro y cobertura ante incumplimiento de proveedores (-20 % capacidad efectiva)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="method-card">
        <strong>Enfoque predictivo del escenario:</strong> A partir de las tasas históricas de entrega a tiempo de proveedores
        (<code>On_Time_Delivery_Rate</code> entre 61 % y 99 %) y el historial de órdenes de compra, se ajusta una
        <strong>regresión OLS de oferta mensual</strong> y se proyecta el impacto de una contracción del <strong>20 % en el stock efectivo
        (<code>f_stock = 0.80</code>)</strong> sobre la proyección Holt-Winters de 12 meses.
    </div>
    """,
    unsafe_allow_html=True,
)

_, mensual_dem = obtener_demanda_mensual()
_, mensual_abast = obtener_abastecimiento_mensual()

if mensual_dem is None or mensual_abast is None:
    st.info("⬅️ Sube ambos archivos (**Base de Demanda** y **Base de Abastecimiento**) en la barra lateral para ejecutar este escenario predictivo.")
    st.stop()

COB_MIN, COB_MAX = 27, 33

# 1. Modelo predictivo OLS sobre abastecimiento histórico vs ajustado por riesgo OTD (-20%)
ols_abast_base = smf.ols("Order_Quantity ~ t", data=mensual_abast).fit()
mensual_abast["Abast_Riesgo"] = mensual_abast["Order_Quantity"] * 0.80
ols_abast_riesgo = smf.ols("Abast_Riesgo ~ t", data=mensual_abast).fit()

t_futuro = pd.DataFrame({"t": np.arange(len(mensual_abast) + 1, len(mensual_abast) + 13)})
proy_abast_base = ols_abast_base.predict(t_futuro)
proy_abast_riesgo = ols_abast_riesgo.predict(t_futuro)

# 2. Proyección de cobertura Holt-Winters bajo contracción de stock (f_stock = 0.80)
df_luis = calcular_modelo_luis(mensual_dem)
sim_df, d_prom, stock_esc = simular_escenario_predictivo(df_luis, f_dem=1.00, f_stock=0.80)

# KPIs ejecutivos
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Abast. Predicho Base</div><div class="kpi-value">{proy_abast_base.mean():,.0f} u/mes</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Abast. Predicho Riesgo</div><div class="kpi-value">{proy_abast_riesgo.mean():,.0f} u/mes</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Cobertura Media Predicha</div><div class="kpi-value">{sim_df["cobertura_esc"].mean():.1f} días</div></div>', unsafe_allow_html=True)
with c4:
    meses_quiebre = int((sim_df["cobertura_esc"] < COB_MIN).sum())
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Meses en Quiebre (&lt;27d)</div><div class="kpi-value">{meses_quiebre} / 12</div></div>', unsafe_allow_html=True)

st.write("")

# Gráfico comparativo de dos paneles: Predicción de Abastecimiento OLS + Predicción de Cobertura
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.2))

# Panel 1: Modelo Predictivo OLS de Abastecimiento (Base vs Riesgo Proveedores)
meses_t = np.arange(1, 13)
ax1.plot(meses_t, proy_abast_base, color=PALETA["espresso"], lw=2.4, marker="o", label="Proyección OLS Base (100 %)")
ax1.plot(meses_t, proy_abast_riesgo, color=PALETA["rojo"], lw=2.4, linestyle="--", marker="s", label="Proyección OLS Riesgo (-20 %)")
ax1.fill_between(meses_t, proy_abast_riesgo, proy_abast_base, color=PALETA["primario"], alpha=0.35, label="Déficit predictivo de oferta")
ax1.set_title("1) Predicción OLS de Abastecimiento (12 meses)")
ax1.set_xlabel("Mes proyectado (t+1 a t+12)")
ax1.set_ylabel("Unidades de compra proyectadas")
ax1.set_xticks(meses_t)
ax1.legend(frameon=False, loc="lower left")

# Panel 2: Impacto Predictivo en Días de Cobertura (Base vs Escenario 1)
x = np.arange(len(sim_df))
ax2.axhspan(COB_MIN, COB_MAX, color=PALETA["verde"], alpha=0.15, label="Zona meta (27–33 días)")
ax2.plot(x, sim_df["cobertura_base"], color=PALETA["espresso"], lw=2.2, marker="o", label="Cobertura Predicha Base")
ax2.plot(x, sim_df["cobertura_esc"], color=PALETA["rojo"], lw=2.4, linestyle="--", marker="s", label="Cobertura Escenario 1 (-20 % stock)")
ax2.axhline(COB_MIN, color=PALETA["rojo"], linestyle=":", lw=1.3)
ax2.set_title("2) Predicción de Cobertura de Inventario (Holt-Winters)")
ax2.set_xlabel("Mes proyectado")
ax2.set_ylabel("Días de cobertura")
ax2.set_xticks(x)
ax2.set_xticklabels([etiqueta_mes(f) for f in sim_df["fecha"]], rotation=45)
ax2.legend(frameon=False, loc="upper right")

fig.tight_layout()
st.pyplot(fig)

# Tabla de resultados predictivos
st.subheader("Proyección Mensual Comparativa — Escenario Alternativo 1")
tabla_e1 = pd.DataFrame({
    "Mes": [etiqueta_mes(f) for f in sim_df["fecha"]],
    "Demanda Proy. (u)": sim_df["demanda_base"].round(0).astype(int),
    "Cobertura Base (días)": sim_df["cobertura_base"].round(1),
    "Cobertura Esc. 1 (días)": sim_df["cobertura_esc"].round(1),
    "Faltante Estimado (u)": sim_df["faltante_u"].round(0).astype(int),
    "Diagnóstico Predictivo": np.where(sim_df["cobertura_esc"] < COB_MIN, "Riesgo de quiebre (<27d)", "Dentro de meta"),
})
st.dataframe(tabla_e1, use_container_width=True, hide_index=True)