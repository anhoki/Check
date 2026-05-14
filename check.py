import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import locale

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

# ========== MAPA (si hay coordenadas) ==========
st.subheader("🗺️ Distribución geográfica de proyectos")

# Nota: El CSV original no tiene coordenadas, esto es un placeholder
st.info("Para activar el mapa, agrega columnas 'lat' y 'lon' al CSV con coordenadas reales de cada municipio.")

# Simular coordenadas (opcional - descomentar si se agregan al CSV)
if "lat" in df_filtrado.columns and "lon" in df_filtrado.columns:
    fig_mapa = px.scatter_mapbox(
        df_filtrado,
        lat="lat",
        lon="lon",
        hover_name="nombre_proyecto",
        size="inversion_estimada",
        color="estado_general",
        zoom=6,
        height=500,
        title="Ubicación de proyectos"
    )
    fig_mapa.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_mapa, use_container_width=True)

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
