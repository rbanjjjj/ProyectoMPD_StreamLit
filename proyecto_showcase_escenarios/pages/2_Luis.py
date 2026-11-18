import matplotlib.pyplot as plt
import streamlit as st
from utils.pipeline import (
    aplicar_estilos_streamlit,
    configurar_matplotlib,
    renderizar_sidebar_carga,
    obtener_demanda_mensual,
    calcular_modelo_luis,
    PALETA,
)

st.set_page_config(page_title="Luis | Series de Tiempo", page_icon="⏳", layout="wide")
aplicar_estilos_streamlit()
configurar_matplotlib()
renderizar_sidebar_carga()

st.markdown(
    """
    <div class="showcase-banner">
        <h1>Luis</h1>
        <p>Proyecciones de series de tiempo con R o Python en Power Bi</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="method-card">
        <strong>Descripción del método:</strong> Modelado de series de tiempo mediante <strong>Suavizamiento Exponencial Triple
        (Holt-Winters)</strong> en <strong>Python para Power BI</strong> (<code>statsmodels</code>), configurado con componente de
        tendencia aditiva (<code>trend='add'</code>) y estacionalidad aditiva de ciclo anual (<code>seasonal='add'</code>,
        <code>seasonal_periods=12</code>) para proyectar los próximos 12 meses.
    </div>
    """,
    unsafe_allow_html=True,
)

_, mensual = obtener_demanda_mensual()

if mensual is None:
    st.info("⬅️ Por favor, sube la **Base de Demanda (`demanda_limpio.csv`)** en la **Ranura 1** de la barra lateral para visualizar este análisis.")
    st.stop()

df_luis = calcular_modelo_luis(mensual)
hist = df_luis[df_luis["tipo"] == "Histórico"]
proy = df_luis[df_luis["tipo"] == "Proyección"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Meses Históricos</div><div class="kpi-value">{len(hist)}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Horizonte Proyectado</div><div class="kpi-value">{len(proy)} meses</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Demanda Media Proy.</div><div class="kpi-value">{proy["demanda"].mean():,.0f} u</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Total Proyectado 12m</div><div class="kpi-value">{proy["demanda"].sum():,.0f} u</div></div>', unsafe_allow_html=True)

st.write("")

fig, ax = plt.subplots(figsize=(11, 5))

ax.axvspan(proy["fecha"].min(), proy["fecha"].max(), color=PALETA["primario"], alpha=0.22, label="Ventana de Pronóstico")
ax.plot(hist["fecha"], hist["demanda"], label="Histórico", color=PALETA["espresso"], linewidth=2.3, marker="o", markersize=4)

puente_x = [hist["fecha"].iloc[-1]] + list(proy["fecha"])
puente_y = [hist["demanda"].iloc[-1]] + list(proy["demanda"])
ax.plot(puente_x, puente_y, label="Proyección (1 año)", color=PALETA["primario_oscuro"], linestyle="--", linewidth=2.4, marker="o", markersize=4.5)

ax.set_title("Proyección de Demanda — Suavizamiento Exponencial Holt-Winters (12 meses)")
ax.set_xlabel("Fecha")
ax.set_ylabel("Cantidad (Order_Quantity)")
ax.legend(frameon=False, loc="lower left", ncol=3)
fig.tight_layout()
st.pyplot(fig)

st.subheader("Tabla de Salida para Power BI (`df_final` — Pronóstico 12 Meses)")
tabla_proy = proy[["fecha", "demanda", "tipo"]].copy()
tabla_proy["fecha"] = tabla_proy["fecha"].dt.strftime("%Y-%m")
tabla_proy["demanda"] = tabla_proy["demanda"].round(1)
tabla_proy.columns = ["Mes", "Demanda Proyectada (u)", "Tipo"]
st.dataframe(tabla_proy, use_container_width=True, hide_index=True)