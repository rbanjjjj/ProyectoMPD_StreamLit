import os
import base64
import streamlit as st
from utils.pipeline import aplicar_estilos_streamlit, renderizar_sidebar_carga, PALETA

# Ruta robusta relativa a este archivo (funciona tanto en local como en Streamlit Cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_ICONO = os.path.join(BASE_DIR, "assets", "logo.png")
icono_caratula = RUTA_ICONO if os.path.exists(RUTA_ICONO) else "📊"

st.set_page_config(
    page_title="Showcase Analítico | Cadena de Suministro",
    page_icon=icono_caratula,
    layout="wide",
)

aplicar_estilos_streamlit()
renderizar_sidebar_carga()


def obtener_html_logo(ruta, alto_px=68):
    """Convierte la imagen local a Base64 para incrustarla junto al título."""
    if not os.path.exists(ruta):
        return ""
    ext = os.path.splitext(ruta)[1].lower().lstrip(".")
    mime = "image/svg+xml" if ext == "svg" else f"image/{'jpeg' if ext in ('jpg', 'jpeg') else ext}"
    with open(ruta, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f'<img src="data:{mime};base64,{b64}" style="height:{alto_px}px; width:auto; border-radius:10px; object-fit:contain; flex-shrink:0;" />'


logo_html = obtener_html_logo(RUTA_ICONO, alto_px=68)

# HTML sin indentación de 4 espacios para evitar que Markdown lo convierta en bloque de código
banner_html = (
    f'<div class="showcase-banner" style="display:flex; align-items:center; gap:1.2rem;">'
    f'{logo_html}'
    f'<div>'
    f'<h1 style="margin:0;">Showcase Analítico: Modelos Predictivos e Inventarios</h1>'
    f'<p style="margin:0.35rem 0 0 0;">Proyecciones econométricas, series de tiempo, gestión de cobertura y simulación de escenarios</p>'
    f'</div>'
    f'</div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

st.markdown(
    "Este entorno consolida en **Streamlit** los modelos predictivos desarrollados en Power BI, R y Python, "
    "junto con dos escenarios de estrés predictivo. Para comenzar, **carga los dos archivos CSV en las ranuras de la barra lateral izquierda**:"
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        f'<div class="method-card">'
        f'<h3>1. Rodrigo</h3>'
        f'<p><strong>Proyecciones con regresion metodo OLS en Power BI</strong></p>'
        f'<p style="font-size:0.92rem; color:{PALETA["gris"]};">Estimación econométrica de tendencia lineal y variables dummy mensuales (mes base: Enero).</p>'
        f'</div>'
        f'<div class="method-card">'
        f'<h3>3. Emily</h3>'
        f'<p><strong>Analisis de inventario con la demanda proyectada en Rodrigo</strong></p>'
        f'<p style="font-size:0.92rem; color:{PALETA["gris"]};">Contraste entre abastecimiento histórico de MP, demanda proyectada de PT y requerimiento neto (K = 1).</p>'
        f'</div>'
        f'<div class="method-card">'
        f'<h3>5. Escenario alternativo 1</h3>'
        f'<p><strong>Modelo Predictivo ante Riesgo de Incumplimiento de Proveedores</strong></p>'
        f'<p style="font-size:0.92rem; color:{PALETA["gris"]};">Re-estimación predictiva de oferta y cobertura ante contracción del 20 % en suministro de proveedores.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f'<div class="method-card">'
        f'<h3>2. Luis</h3>'
        f'<p><strong>Proyecciones de series de tiempo con R o Python en Power Bi</strong></p>'
        f'<p style="font-size:0.92rem; color:{PALETA["gris"]};">Suavizamiento exponencial triple (Holt-Winters aditivo con estacionalidad de 12 meses).</p>'
        f'</div>'
        f'<div class="method-card">'
        f'<h3>4. Nicole</h3>'
        f'<p><strong>Analisis de rotacion de inventario con la demanda proyectada por Luis en Power BI</strong></p>'
        f'<p style="font-size:0.92rem; color:{PALETA["gris"]};">Evaluación dinámica de rotación, días de cobertura (meta 27–33 días) y alertas tipo semáforo.</p>'
        f'</div>'
        f'<div class="method-card">'
        f'<h3>6. Escenario alternativo 2</h3>'
        f'<p><strong>Modelo Predictivo ante Choque Estacional de Alta Demanda (+15 %)</strong></p>'
        f'<p style="font-size:0.92rem; color:{PALETA["gris"]};">Recalibración de OLS estacional y Holt-Winters ante picos de demanda en Ene, Jun, Jul y Ago.</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
        </div>
        """,
        unsafe_allow_html=True,
    )
