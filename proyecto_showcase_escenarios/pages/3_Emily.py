import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from utils.pipeline import (
    aplicar_estilos_streamlit,
    configurar_matplotlib,
    renderizar_sidebar_carga,
    PALETA,
)

st.set_page_config(page_title="Emily | Análisis de Inventario", page_icon="📦", layout="wide")
aplicar_estilos_streamlit()
configurar_matplotlib()
renderizar_sidebar_carga()

st.markdown(
    """
    <div class="showcase-banner">
        <h1>Emily</h1>
        <p>Analisis de inventario con la demanda proyectada en Rodrigo</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="method-card">
        <strong>Descripción del método:</strong> Evaluación del plan de abastecimiento de materia prima (MP) frente a la
        demanda proyectada de producto terminado (PT) obtenida mediante el modelo OLS de Rodrigo (<code>Oct-24</code> a <code>Sep-25</code>).
        Se contrastan las <strong>compras históricas promedio de MP</strong> (560 u/mes) contra el requerimiento neto
        de materia prima (<code>MP requerida, K = 1</code>) para dimensionar la brecha de suministro.
    </div>
    """,
    unsafe_allow_html=True,
)

df_abast = st.session_state.get("df_abastecimiento_raw")

if df_abast is None:
    st.info("⬅️ Por favor, sube la **Base de Abastecimiento (`Gestion_de_abastecimiento.csv`)** en la **Ranura 2** de la barra lateral para visualizar este análisis.")
    st.stop()

# Datos del modelo de Emily
meses = ['Oct-24', 'Nov-24', 'Dic-24', 'Ene-25',
         'Feb-25', 'Mar-25', 'Abr-25', 'May-25',
         'Jun-25', 'Jul-25', 'Ago-25', 'Sep-25']

demanda_pt = [2919, 2761, 2894, 3146, 2659, 2978,
              2850, 3017, 3064, 3102, 3090, 2697]

compras_mp = [560] * 12

mp_requerida = [845, 2761, 2894, 3146, 2659, 2978,
                2850, 3017, 3064, 3102, 3090, 2697]

# KPIs ejecutivos
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Compras Hist. MP</div><div class="kpi-value">{np.mean(compras_mp):,.0f} u/mes</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Demanda Proy. PT Media</div><div class="kpi-value">{np.mean(demanda_pt):,.0f} u/mes</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">MP Requerida Total (12m)</div><div class="kpi-value">{np.sum(mp_requerida):,.0f} u</div></div>', unsafe_allow_html=True)
with c4:
    brecha_total = np.sum(mp_requerida) - np.sum(compras_mp)
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Brecha Acumulada MP</div><div class="kpi-value">{brecha_total:,.0f} u</div></div>', unsafe_allow_html=True)

st.write("")

# Gráfico adaptado a la estética del showcase (#FFCA87)
x = np.arange(len(meses))
fig, ax = plt.subplots(figsize=(14, 6.2))

# Barras: compras de materia prima
ax.bar(
    x, compras_mp, width=0.55,
    color=PALETA["primario"], edgecolor=PALETA["primario_oscuro"], linewidth=1.1,
    label='Compras históricas de MP', alpha=0.9
)

# Líneas: demanda y requerimiento
ax.plot(
    x, demanda_pt, marker='o', linewidth=2.5,
    color=PALETA["espresso"], label='Demanda proyectada de PT'
)

ax.plot(
    x, mp_requerida, marker='s', linewidth=2.5,
    linestyle='--', color=PALETA["primario_oscuro"], label='MP requerida (K = 1)'
)

# Formato
ax.set_title('Análisis de abastecimiento e inventario', fontsize=17, fontweight='bold', pad=20)
ax.set_xlabel('Mes', fontsize=12)
ax.set_ylabel('Unidades mensuales', fontsize=12)

ax.set_xticks(x)
ax.set_xticklabels(meses)
ax.set_ylim(0, 3500)

ax.grid(axis='y', linestyle='--', alpha=0.3)
ax.legend(loc='upper right', frameon=False)

fig.tight_layout()
st.pyplot(fig)

# Tabla resumen de soporte
st.subheader("Detalle Mensual de Planificación de Materia Prima (Oct-24 a Sep-25)")
df_resumen_emily = pd.DataFrame({
    "Mes": meses,
    "Compras históricas MP (u)": compras_mp,
    "Demanda proyectada PT (u)": demanda_pt,
    "MP requerida K=1 (u)": mp_requerida,
    "Déficit mensual MP (u)": [req - comp for req, comp in zip(mp_requerida, compras_mp)],
})
st.dataframe(df_resumen_emily, use_container_width=True, hide_index=True)