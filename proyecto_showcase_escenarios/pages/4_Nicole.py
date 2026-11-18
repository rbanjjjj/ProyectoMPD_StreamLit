import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import streamlit as st
from utils.pipeline import (
    aplicar_estilos_streamlit,
    configurar_matplotlib,
    renderizar_sidebar_carga,
    obtener_demanda_mensual,
    calcular_modelo_luis,
    etiqueta_mes,
    PALETA,
)

st.set_page_config(page_title="Nicole | Rotación y Cobertura", page_icon="🔄", layout="wide")
aplicar_estilos_streamlit()
configurar_matplotlib()
renderizar_sidebar_carga()

st.markdown(
    """
    <div class="showcase-banner">
        <h1>Nicole</h1>
        <p>Analisis de rotacion de inventario con la demanda proyectada por Luis en Power BI</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="method-card">
        <strong>Descripción del método:</strong> Evaluación de eficiencia de inventario a partir de la serie histórica y la
        proyección de 12 meses de <strong>Luis (Holt-Winters)</strong>. Se calculan indicadores equivalentes a medidas
        <strong>DAX</strong>: índice de rotación (<code>Demanda / Demanda Promedio</code>) y días de cobertura
        (<code>Días del mes / Rotación</code>), clasificando cada periodo frente a una meta operativa de <strong>27 a 33 días</strong>.
    </div>
    """,
    unsafe_allow_html=True,
)

_, mensual = obtener_demanda_mensual()

if mensual is None:
    st.info("⬅️ Por favor, sube la **Base de Demanda (`demanda_limpio.csv`)** en la **Ranura 1** de la barra lateral para visualizar este análisis.")
    st.stop()

COB_MIN, COB_MAX, COB_OBJETIVO = 27, 33, 30

d = calcular_modelo_luis(mensual)
d_prom = d["demanda"].mean()
d["rotacion"] = d["demanda"] / d_prom
d["cobertura"] = d["dias"] / d["rotacion"]


def semaforo_cod(cob):
    if cob < COB_MIN:
        return 0  # Rojo: riesgo de quiebre
    if cob > COB_MAX:
        return 2  # Ámbar: exceso de stock
    return 1      # Verde: dentro de meta


proy_df = d[d["tipo"] == "Proyección"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Demanda Ref. (D̄)</div><div class="kpi-value">{d_prom:,.0f} u</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Cobertura Media Proy.</div><div class="kpi-value">{proy_df["cobertura"].mean():.1f} días</div></div>', unsafe_allow_html=True)
with c3:
    en_meta = int(proy_df["cobertura"].between(COB_MIN, COB_MAX).sum())
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Meses Proy. en Meta</div><div class="kpi-value">{en_meta} / {len(proy_df)}</div></div>', unsafe_allow_html=True)
with c4:
    en_riesgo = int((proy_df["cobertura"] < COB_MIN).sum())
    st.markdown(f'<div class="kpi-box"><div class="kpi-label">Meses Riesgo Quiebre</div><div class="kpi-value">{en_riesgo}</div></div>', unsafe_allow_html=True)

st.write("")

x = np.arange(len(d))
proy = (d["tipo"] == "Proyección").values
col_barras = [PALETA["primario_oscuro"] if p else PALETA["espresso"] for p in proy]
cob = d["cobertura"].values

fig, (a1, a2, a3) = plt.subplots(
    3, 1, figsize=(13, 9.5), sharex=True,
    gridspec_kw={"height_ratios": [1, 1, 1.15], "hspace": 0.28}
)

ini_proy = int(np.argmax(proy))
for a in (a1, a2, a3):
    a.axvspan(ini_proy - 0.5, len(d) - 0.5, color=PALETA["primario"], alpha=0.20, zorder=0)
    a.grid(axis="x", visible=False)

# 1) Demanda
a1.plot(x[~proy], d["demanda"].values[~proy], color=PALETA["espresso"], lw=2.3, marker="o", ms=4, label="Histórica")
idx = np.r_[np.where(~proy)[0][-1], np.where(proy)[0]]
a1.plot(idx, d["demanda"].values[idx], color=PALETA["primario_oscuro"], lw=2.3, ls="--", marker="o", ms=4, label="Proyectada (Luis)")
a1.axhline(d_prom, color=PALETA["gris"], ls=":", lw=2.0, label=f"Promedio D̄ = {d_prom:,.0f}")
a1.set_ylabel("Unidades")
a1.set_title("1) Demanda mensual (entrada)")
a1.legend(loc="lower left", ncol=3, frameon=False, fontsize=10)
a1.text(x[proy].mean(), a1.get_ylim()[1] - 20, "PROYECCIÓN", ha="center", va="top", color=PALETA["primario_oscuro"], fontsize=10, fontweight="bold")

# 2) Rotación
a2.bar(x, d["rotacion"] - 1, bottom=1, color=col_barras, width=0.72, zorder=3)
a2.axhline(1, color=PALETA["gris"], lw=1.8, zorder=4)
a2.set_ylabel("Rotación (veces)")
a2.set_title("2) Rotación = demanda ÷ D̄   (sobre 1.0: demanda por encima del promedio)")
a2.set_ylim(d["rotacion"].min() - 0.06, d["rotacion"].max() + 0.06)

# 3) Cobertura y Semáforo
a3.axhspan(COB_MIN, COB_MAX, color=PALETA["verde"], alpha=0.14, zorder=1)
a3.plot(x[~proy], cob[~proy], color=PALETA["espresso"], lw=2.1, zorder=3)
a3.plot(idx, cob[idx], color=PALETA["primario_oscuro"], lw=2.1, ls="--", zorder=3)
est = np.vectorize(semaforo_cod)(cob)
a3.scatter(
    x, cob, s=55,
    c=[{0: PALETA["rojo"], 1: PALETA["verde"], 2: PALETA["ambar"]}[e] for e in est],
    zorder=4, edgecolor="white", linewidth=0.8
)
a3.axhline(COB_OBJETIVO, color=PALETA["gris"], ls="--", lw=1.2, zorder=2)
a3.set_ylim(min(COB_MIN - 2, cob.min() - 1), max(COB_MAX + 2, cob.max() + 1))
a3.set_ylabel("Días de cobertura")
a3.set_title(f"3) Cobertura = días del mes ÷ rotación   (meta {COB_MIN}–{COB_MAX} días)")
a3.legend(
    handles=[
        Patch(color=PALETA["verde"], alpha=0.45, label="Zona de meta (27–33 d)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETA["verde"], ms=8, label="Dentro de meta"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETA["ambar"], ms=8, label="Exceso de stock (>33 d)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETA["rojo"], ms=8, label="Riesgo de quiebre (<27 d)"),
    ],
    loc="upper center", ncol=4, frameon=False, fontsize=10, bbox_to_anchor=(0.5, -0.14)
)

marcas = x[::3]
a3.set_xticks(marcas)
a3.set_xticklabels([etiqueta_mes(f) for f in d["fecha"].iloc[::3]])
fig.suptitle(
    "Cuando la demanda sube, la rotación sube y los días de cobertura bajan",
    x=0.01, ha="left", fontsize=15, fontweight="bold", color=PALETA["espresso"], y=0.96
)
fig.tight_layout()
st.pyplot(fig)