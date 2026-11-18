import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from utils.pipeline import (
    aplicar_estilos_streamlit,
    configurar_matplotlib,
    renderizar_sidebar_carga,
    obtener_demanda_mensual,
    calcular_modelos_rodrigo,
    etiqueta_mes,
    PALETA,
)

st.set_page_config(page_title="Rodrigo | Regresión OLS", page_icon="📈", layout="wide")
aplicar_estilos_streamlit()
configurar_matplotlib()
renderizar_sidebar_carga()

st.markdown(
    """
    <div class="showcase-banner">
        <h1>Rodrigo</h1>
        <p>Proyecciones con regresion metodo OLS en Power BI</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="method-card">
        <strong>Descripción del método:</strong> Ajuste por Mínimos Cuadrados Ordinarios (OLS) implementado originalmente mediante
        scripts de <strong>R en Power BI</strong> y medidas <strong>DAX</strong>. Se evalúa tanto la tendencia lineal pura
        (<code>Demanda = β₀ + β₁·t</code>) como la especificación con <strong>variables dummy estacionales mensuales</strong>
        (mes base: Enero) para capturar las caídas y picos recurrentes del año.
    </div>
    """,
    unsafe_allow_html=True,
)

_, mensual = obtener_demanda_mensual()

if mensual is None:
    st.info("⬅️ Por favor, sube la **Base de Demanda (`demanda_limpio.csv`)** en la **Ranura 1** de la barra lateral para visualizar este análisis.")
    st.stop()

ols_simple, ols_estacional, df_total = calcular_modelos_rodrigo(mensual)

sse_simple = sum(ols_simple.resid ** 2)
sse_est = sum(ols_estacional.resid ** 2)
r2_simple = ols_simple.rsquared
r2_est = ols_estacional.rsquared

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Intercepto OLS Estacional</div><div class="kpi-value">{ols_estacional.params["Intercept"]:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Pendiente Tendencia (t)</div><div class="kpi-value">{ols_estacional.params["t"]:.2f} u/mes</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">R² OLS Estacional</div><div class="kpi-value">{r2_est:.4f}</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">SSE Mínimo Estacional</div><div class="kpi-value">{sse_est:,.0f}</div></div>', unsafe_allow_html=True)

st.write("")

fig, ax = plt.subplots(figsize=(12, 4.8))
x = np.arange(len(df_total))
hist_mask = df_total["Tipo"] == "Histórico"

ax.axvspan(hist_mask.sum() - 0.5, len(df_total) - 0.5, color=PALETA["primario"], alpha=0.22, label="Horizonte Proyectado (12m)")
ax.plot(x[hist_mask], df_total.loc[hist_mask, "Order_Quantity"], color=PALETA["espresso"], lw=2.3, marker="o", ms=4.5, label="Demanda Histórica")
ax.plot(x, df_total["OLS_Estacional"], color=PALETA["primario_oscuro"], lw=2.4, linestyle="--", marker="s", ms=4, label="OLS con Dummies Estacionales (DAX/R)")
ax.plot(x, df_total["OLS_Simple"], color=PALETA["gris"], lw=1.8, linestyle=":", label="OLS Tendencia Lineal Simple")

ax.set_title("Ajuste y Proyección de Demanda — Método OLS (Histórico vs. Proyección)")
ax.set_ylabel("Unidades (Order_Quantity)")
ax.set_xticks(x[::3])
ax.set_xticklabels([etiqueta_mes(f) for f in df_total["fecha"].iloc[::3]])
ax.legend(loc="lower left", ncol=2, frameon=False)
fig.tight_layout()
st.pyplot(fig)

st.subheader("Salida Econométrica Equivalente (Script R en Power BI)")
coefs = ols_estacional.params
dummies = [f"{'+' if v >= 0 else '-'} {abs(v):.2f}*D_Mes{k.split('[T.')[1].rstrip(']')}" for k, v in coefs.items() if "Month_Num" in k]
linea_1 = f"Demanda_Mensual = {coefs['Intercept']:.2f} - {abs(coefs['t']):.2f}*t " + " ".join(dummies[:5])
linea_2 = "                  " + " ".join(dummies[5:])

resumen_r = "\n".join([
    "=== MODELO OLS CON DUMMIES ESTACIONALES (ESCALA MENSUAL) ===",
    "",
    "Ecuación estimada:",
    linea_1,
    linea_2,
    "",
    "(D_MesX = 1 si es el mes X, 0 si no lo es. Mes base = Enero)",
    "-------------------------------------------------------------------------",
    f"SSE Mínimo (Estacional): {sse_est:,.2f}   |   SSE Mínimo (Lineal Simple): {sse_simple:,.2f}",
    f"R-cuadrado (Estacional): {r2_est:.4f}       |   R-cuadrado (Lineal Simple): {r2_simple:.4f}",
    "-------------------------------------------------------------------------",
])
st.code(resumen_r, language="text")