import os
import base64
import streamlit as st
from utils.pipeline import aplicar_estilos_streamlit, renderizar_sidebar_carga, PALETA

# Ruta de la imagen para el favicon y el banner
RUTA_ICONO = "assets/logo_ulima.png"
icono_caratula = RUTA_ICONO if os.path.exists(RUTA_ICONO) else "📊"

st.set_page_config(
    page_title="Showcase Analítico | Cadena de Suministro",
    page_icon=icono_caratula,
    layout="wide",
)

aplicar_estilos_streamlit()
renderizar_sidebar_carga()


def obtener_html_logo(ruta, alto_px=64):
    """Convierte la imagen local a Base64 para incrustarla junto al título."""
    if not os.path.exists(ruta):
        return ""
    ext = os.path.splitext(ruta)[1].lower().lstrip(".")
    mime = "image/svg+xml" if ext == "svg" else f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
    with open(ruta, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return (
        f'<img src="data:{mime};base64,{b64}" '
        f'style="height:{alto_px}px; width:auto; border-radius:10px; object-fit:contain; flex-shrink:0;" />'
    )


logo_html = obtener_html_logo(RUTA_ICONO, alto_px=68)

st.markdown(
    f"""
    <div class="showcase-banner" style="display:flex; align-items:center; gap:1.2rem;">
        {logo_html}
        <div>
            <h1 style="margin:0;">Showcase Analítico: Modelos Predictivos e Inventarios</h1>
            <p style="margin:0.35rem 0 0 0;">Proyecciones econométricas, series de tiempo, gestión de cobertura y simulación de escenarios</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    Este entorno consolida en **Streamlit** los modelos predictivos desarrollados en Power BI, R y Python,
    junto con dos escenarios de estrés predictivo. Para comenzar, **carga los dos archivos CSV en las ranuras de la barra lateral izquierda**:
    """
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f"""
        <div class="method-card">
            <h3>1. Rodrigo</h3>
            <p><strong>Proyecciones con regresion metodo OLS en Power BI</strong></p>
            <p style="font-size:0.92rem; color:{PALETA['gris']};">
            Estimación econométrica de tendencia lineal y variables dummy mensuales (mes base: Enero).
            </p>
        </div>
        <div class="method-card">
            <h3>3. Emily</h3>
            <p><strong>Analisis de inventario con la demanda proyectada en Rodrigo</strong></p>
            <p style="font-size:0.92rem; color:{PALETA['gris']};">
            Contraste entre abastecimiento histórico de MP, demanda proyectada de PT y requerimiento neto (K = 1).
            </p>
        </div>
        <div class="method-card">
            <h3>5. Escenario alternativo 1</h3>
            <p><strong>Modelo Predictivo ante Riesgo de Incumplimiento de Proveedores</strong></p>
            <p style="font-size:0.92rem; color:{PALETA['gris']};">
            Re-estimación predictiva de oferta y cobertura ante contracción del 20 % en suministro de proveedores.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="method-card">
            <h3>2. Luis</h3>
            <p><strong>Proyecciones de series de tiempo con R o Python en Power Bi</strong></p>
            <p style="font-size:0.92rem; color:{PALETA['gris']};">
            Suavizamiento exponencial triple (Holt-Winters aditivo con estacionalidad de 12 meses).
            </p>
        </div>
        <div class="method-card">
            <h3>4. Nicole</h3>
            <p><strong>Analisis de rotacion de inventario con la demanda proyectada por Luis en Power BI</strong></p>
            <p style="font-size:0.92rem; color:{PALETA['gris']};">
            Evaluación dinámica de rotación, días de cobertura (meta 27–33 días) y alertas tipo semáforo.
            </p>
        </div>
        <div class="method-card">
            <h3>6. Escenario alternativo 2</h3>
            <p><strong>Modelo Predictivo ante Choque Estacional de Alta Demanda (+15 %)</strong></p>
            <p style="font-size:0.92rem; color:{PALETA['gris']};">
            Recalibración de OLS estacional y Holt-Winters ante picos de demanda en Ene, Jun, Jul y Ago.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )