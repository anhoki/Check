import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import locale
import folium
from streamlit_folium import st_folium


# Configuración de página
st.set_page_config(
    page_title="Dashboard de Proyectos - Guatemala",
    page_icon="🏗️",
    layout="wide"
)

# Título
st.title("🏗️ Dashboard de Seguimiento de Proyectos de Inversión")
st.markdown("### Guatemala - Infraestructura Pública y Educativa")
st.markdown("---")

# Cargar datos
@st.cache_data
def cargar_datos():
    df = pd.read_csv("proyectos_guatemala.csv", parse_dates=["fecha_inicio_gestion", "fecha_fin_estimada"])
    return df

df = cargar_datos()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro por departamento
departamentos = ["Todos"] + sorted(df["departamento"].unique())
departamento_seleccionado = st.sidebar.selectbox("Departamento", departamentos)

# Filtro por tipología
tipologias = ["Todas"] + sorted(df["tipologia"].unique())
tipologia_seleccionada = st.sidebar.selectbox("Tipología de proyecto", tipologias)

# Filtro por fase
fases = ["Todas"] + sorted(df["fase_actual"].unique())
fase_seleccionada = st.sidebar.selectbox("Fase actual", fases)

# Filtro por estado
estados = ["Todos"] + sorted(df["estado_general"].unique())
estado_seleccionado = st.sidebar.selectbox("Estado general", estados)

# Aplicar filtros
df_filtrado = df.copy()

if departamento_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["departamento"] == departamento_seleccionado]

if tipologia_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["tipologia"] == tipologia_seleccionada]

if fase_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["fase_actual"] == fase_seleccionada]

if estado_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["estado_general"] == estado_seleccionado]


# ============================================
# COORDENADAS DE DEPARTAMENTOS DE GUATEMALA
# ============================================
COORDENADAS_DEPARTAMENTOS = {
    'GUATEMALA': [14.6349, -90.5069],
    'EL PROGRESO': [14.8500, -90.0667],
    'SACATEPEQUEZ': [14.5333, -90.7333],
    'CHIMALTENANGO': [14.7000, -90.8167],
    'ESCUINTLA': [14.3000, -90.7833],
    'SANTA ROSA': [14.1667, -90.3500],
    'SOLOLÁ': [14.7667, -91.1833],
    'TOTONICAPÁN': [14.9167, -91.3667],
    'QUETZALTENANGO': [14.8333, -91.5167],
    'SUCHITEPÉQUEZ': [14.5333, -91.5000],
    'RETALHULEU': [14.5333, -91.6833],
    'SAN MARCOS': [14.9667, -91.8000],
    'HUEHUETENANGO': [15.3167, -91.4667],
    'QUICHÉ': [15.3000, -91.0000],
    'BAJA VERAPAZ': [15.1333, -90.3667],
    'ALTA VERAPAZ': [15.5000, -90.3333],
    'PETÉN': [16.9000, -89.9000],
    'IZABAL': [15.5000, -88.5000],
    'ZACAPA': [14.9667, -89.5333],
    'CHIQUIMULA': [14.8000, -89.5333],
    'JALAPA': [14.6333, -89.9833],
    'JUTIAPA': [14.2833, -89.9000],
}

def crear_mapa_burbujas(df):
    """Crea un mapa de burbujas con folium - adaptado para tu CSV"""
    
    if df.empty or 'departamento' not in df.columns:
        return None
    
    # Agrupar por departamento
    monto_por_depto = df.groupby('departamento')['inversion_estimada'].sum().reset_index()
    monto_por_depto.columns = ['departamento', 'monto_total']
    
    if monto_por_depto.empty:
        return None
    
    # Centro de Guatemala
    center_lat, center_lon = 15.5, -90.25
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7.5, control_scale=True)
    
    max_monto = monto_por_depto['monto_total'].max()
    min_radius = 8
    max_radius = 35
    
    for _, row in monto_por_depto.iterrows():
        depto = row['departamento'].upper()
        monto = row['monto_total']
        
        coords = COORDENADAS_DEPARTAMENTOS.get(depto)
        if not coords:
            continue
        
        # Radio proporcional al monto
        radius = min_radius + (monto / max_monto) * (max_radius - min_radius) if max_monto > 0 else min_radius
        num_proyectos = len(df[df['departamento'].str.upper() == depto])
        
        folium.CircleMarker(
            location=coords,
            radius=radius,
            popup=f"""
                <b>{depto}</b><br>
                💰 Inversión: Q{monto:,.0f}<br>
                📊 Proyectos: {num_proyectos}
            """,
            tooltip=f"{depto}: Q{monto:,.0f}",
            color='#2E86AB',
            fill=True,
            fill_color='#2E86AB',
            fill_opacity=0.6,
            weight=2
        ).add_to(m)
    
    return m

def crear_mapa_calor(df):
    """Crea un mapa de calor con folium - adaptado para tu CSV"""
    
    if df.empty or 'departamento' not in df.columns:
        return None
    
    heat_data = []
    for _, row in df.iterrows():
        depto = row['departamento'].upper()
        monto = row['inversion_estimada']
        coords = COORDENADAS_DEPARTAMENTOS.get(depto)
        if coords:
            # Intensidad basada en el monto (más monto = más puntos de calor)
            intensidad = max(1, min(100, int(monto / 100000)))
            for _ in range(intensidad):
                heat_data.append(coords)
    
    if not heat_data:
        return None
    
    center_lat, center_lon = 15.5, -90.25
    heat_map = folium.Map(location=[center_lat, center_lon], zoom_start=7.5, control_scale=True)
    
    from folium.plugins import HeatMap
    HeatMap(heat_data, radius=20, blur=15, min_opacity=0.3).add_to(heat_map)
    
    return heat_map
# ========== MÉTRICAS PRINCIPALES ==========
st.subheader("📊 Resumen General")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total de proyectos", len(df_filtrado))

with col2:
    proyectos_aprobacion = df_filtrado[df_filtrado["estado_general"] == "En aprobación"].shape[0]
    st.metric("En aprobación", proyectos_aprobacion)

with col3:
    proyectos_listos = df_filtrado[df_filtrado["estado_general"] == "Listo para compras"].shape[0]
    st.metric("Listos para compras", proyectos_listos)

with col4:
    inversion_total = df_filtrado["inversion_estimada"].sum() / 1_000_000
    st.metric("Inversión total", f"Q{inversion_total:,.1f}M")

with col5:
    beneficiarios_total = df_filtrado["beneficiarios"].sum()
    st.metric("Beneficiarios", f"{beneficiarios_total:,}")

st.markdown("---")

# ========== GRÁFICOS ==========
col1, col2 = st.columns(2)

with col1:
    # Proyectos por departamento
    st.subheader("📍 Proyectos por departamento")
    df_deptos = df_filtrado.groupby("departamento").size().reset_index(name="cantidad")
    df_deptos = df_deptos.sort_values("cantidad", ascending=True)
    fig_deptos = px.bar(
        df_deptos, 
        x="cantidad", 
        y="departamento",
        orientation="h",
        color="cantidad",
        color_continuous_scale="Blues",
        title="Cantidad de proyectos por departamento"
    )
    fig_deptos.update_layout(height=500)
    st.plotly_chart(fig_deptos, use_container_width=True)

with col2:
    # Proyectos por tipología
    st.subheader("🏗️ Proyectos por tipología")
    df_tipos = df_filtrado.groupby("tipologia").size().reset_index(name="cantidad")
    fig_tipos = px.pie(
        df_tipos, 
        values="cantidad", 
        names="tipologia",
        title="Distribución por tipo de proyecto"
    )
    st.plotly_chart(fig_tipos, use_container_width=True)

# ========== SEGUNDA FILA DE GRÁFICOS ==========
col1, col2 = st.columns(2)

with col1:
    # Avance por fase
    st.subheader("📈 Avance promedio por fase")
    df_fases = df_filtrado.groupby("fase_actual")["avance_porcentaje"].mean().reset_index()
    fig_fases = px.bar(
        df_fases,
        x="fase_actual",
        y="avance_porcentaje",
        color="avance_porcentaje",
        color_continuous_scale="RdYlGn",
        title="Avance promedio por fase",
        labels={"fase_actual": "Fase", "avance_porcentaje": "Avance promedio (%)"}
    )
    st.plotly_chart(fig_fases, use_container_width=True)

with col2:
    # Inversión vs beneficiarios
    st.subheader("💰 Inversión vs Beneficiarios")
    fig_inv = px.scatter(
        df_filtrado,
        x="beneficiarios",
        y="inversion_estimada",
        color="tipologia",
        size="avance_porcentaje",
        hover_data=["nombre_proyecto", "departamento", "estado_general"],
        title="Relación: Inversión vs Beneficiarios",
        labels={"beneficiarios": "Beneficiarios", "inversion_estimada": "Inversión (Q)"}
    )
    st.plotly_chart(fig_inv, use_container_width=True)

# ========== TABLA DE DATOS ==========
st.subheader("📋 Listado de proyectos")

# Selector de columnas para tabla
columnas_mostrar = st.multiselect(
    "Selecciona las columnas a mostrar",
    options=df_filtrado.columns.tolist(),
    default=["id", "nombre_proyecto", "departamento", "municipio", "tipologia", 
             "inversion_estimada", "avance_porcentaje", "fase_actual", "estado_general"]
)

# Ordenamiento
ordenar_por = st.selectbox("Ordenar por", columnas_mostrar)
orden_ascendente = st.checkbox("Orden ascendente", True)

df_display = df_filtrado[columnas_mostrar].sort_values(
    by=ordenar_por, 
    ascending=orden_ascendente
)

st.dataframe(
    df_display.style.format({
        "inversion_estimada": "Q{:,.2f}",
        "avance_porcentaje": "{:.0f}%"
    }),
    use_container_width=True,
    height=400
)

# ========== INDICADORES DE APROBACIÓN ==========
st.subheader("✅ Estado de aprobaciones externas")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**IDAEH**")
    conteo_idaeh = df_filtrado["aprobacion_idaeh"].value_counts()
    st.bar_chart(conteo_idaeh)

with col2:
    st.markdown("**MARN**")
    conteo_marn = df_filtrado["aprobacion_marn"].value_counts()
    st.bar_chart(conteo_marn)

with col3:
    st.markdown("**SEGEPLAN**")
    conteo_segeplan = df_filtrado["aprobacion_segeplan"].value_counts()
    st.bar_chart(conteo_segeplan)

# ============================================
# MAPAS
# ============================================
st.subheader("🗺️ Distribución geográfica de proyectos")

# Verificar que hay datos
if df_filtrado.empty:
    st.warning("No hay datos para mostrar en el mapa")
else:
    # Selector de tipo de mapa
    tipo_mapa = st.radio(
        "Selecciona tipo de mapa",
        ["Mapa de burbujas (Inversión)", "Mapa de calor"],
        horizontal=True
    )
    
    try:
        if tipo_mapa == "Mapa de burbujas (Inversión)":
            mapa = crear_mapa_burbujas(df_filtrado)
            if mapa is not None:
                # Usar folium_static en lugar de st_folium para evitar errores
                from folium.plugins import HeatMap
                st.components.v1.html(mapa._repr_html_(), width=800, height=500)
            else:
                st.info("No se pudo generar el mapa de burbujas. Verifica que hay datos con coordenadas.")
        else:
            mapa_calor = crear_mapa_calor(df_filtrado)
            if mapa_calor is not None:
                st.components.v1.html(mapa_calor._repr_html_(), width=800, height=500)
            else:
                st.info("No se pudo generar el mapa de calor. Verifica que hay datos con coordenadas.")
    except Exception as e:
        st.error(f"Error al generar el mapa: {e}")
        st.info("Asegúrate de que el archivo CSV tiene la columna 'departamento' correctamente escrita")

# ============================================
# 🚦 SEMÁFORO DE AVANCE POR PROYECTO
# ============================================
st.subheader("🚦 Semáforo de avance por proyecto")

# Selector de proyecto
proyectos_disponibles = df_filtrado['nombre_proyecto'].tolist()
proyecto_seleccionado = st.selectbox(
    "Selecciona un proyecto para ver su estado",
    proyectos_disponibles,
    key="semaforo_selector"
)

# Obtener datos del proyecto seleccionado
proyecto_data = df_filtrado[df_filtrado['nombre_proyecto'] == proyecto_seleccionado].iloc[0]

# Definir color del semáforo según avance
avance = proyecto_data['avance_porcentaje']

if avance < 30:
    color_semaforo = "🔴"  # Rojo - crítico
    mensaje_estado = "Crítico - Avance insuficiente"
    color_fondo = "#FFE5E5"
elif avance < 70:
    color_semaforo = "🟡"  # Amarillo - en progreso
    mensaje_estado = "En progreso - Requiere atención"
    color_fondo = "#FFF4E5"
else:
    color_semaforo = "🟢"  # Verde - buen avance
    mensaje_estado = "Buen avance - En camino"
    color_fondo = "#E5FFE5"

# Mostrar semáforo con estilo
col_semaforo, col_detalles = st.columns([1, 3])

with col_semaforo:
    st.markdown(
        f"""
        <div style="text-align: center; background-color: {color_fondo}; padding: 20px; border-radius: 20px;">
            <h1 style="font-size: 80px; margin: 0;">{color_semaforo}</h1>
            <p style="font-weight: bold; margin: 0;">{avance:.0f}%</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_detalles:
    st.markdown(
        f"""
        <div style="background-color: {color_fondo}; padding: 15px; border-radius: 10px;">
            <h4 style="margin: 0 0 10px 0;">📋 {proyecto_data['nombre_proyecto']}</h4>
            <p style="margin: 5px 0;">📍 <b>Ubicación:</b> {proyecto_data['departamento']} - {proyecto_data['municipio']}</p>
            <p style="margin: 5px 0;">🏗️ <b>Tipo:</b> {proyecto_data['tipologia']}</p>
            <p style="margin: 5px 0;">💰 <b>Inversión:</b> Q{proyecto_data['inversion_estimada']:,.0f}</p>
            <p style="margin: 5px 0;">👥 <b>Beneficiarios:</b> {proyecto_data['beneficiarios']:,}</p>
            <p style="margin: 5px 0;">📊 <b>Fase actual:</b> {proyecto_data['fase_actual']}</p>
            <p style="margin: 10px 0 0 0; font-weight: bold;">🚦 Estado: {mensaje_estado}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Barra de progreso adicional
st.progress(avance / 100, text=f"Progreso general del proyecto: {avance:.0f}%")


# ========== DESCARGA DE DATOS ==========
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Descarga de datos")

if st.sidebar.button("Exportar datos filtrados a CSV"):
    csv = df_filtrado.to_csv(index=False).encode("utf-8-sig")
    st.sidebar.download_button(
        label="⬇️ Descargar CSV",
        data=csv,
        file_name=f"proyectos_filtrados_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Datos simulados para 50 proyectos en Guatemala")
