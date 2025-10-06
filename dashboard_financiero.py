"""
DASHBOARD FINANCIERO INTERACTIVO CON STREAMLIT
Archivo: dashboard_financiero.py

INSTRUCCIONES DE INSTALACIÓN Y EJECUCIÓN:

1. Instalar dependencias (ejecutar UNA VEZ en terminal):
   pip install streamlit yfinance pandas numpy plotly

2. Ejecutar la aplicación (en la carpeta del proyecto):
   streamlit run dashboard_financiero.py

3. Se abrirá automáticamente en el navegador en:
   http://localhost:8501

4. Para detener la aplicación:
   Presionar Ctrl+C en la terminal

ESTRUCTURA DE ARCHIVOS RECOMENDADA:
proyecto/
├── dashboard_financiero.py (este archivo)
├── requirements.txt (opcional)
└── README.md (opcional)
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================

st.set_page_config(
    page_title="Dashboard Financiero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

@st.cache_data(ttl=3600)
def descargar_datos(tickers, inicio, fin):
    """
    Descarga datos históricos de Yahoo Finance con cache.
    
    Args:
        tickers: Lista de símbolos de activos
        inicio: Fecha de inicio (datetime)
        fin: Fecha de fin (datetime)
    
    Returns:
        DataFrame con precios históricos
    """
    datos = pd.DataFrame()
    errores = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(tickers):
        try:
            status_text.text(f"Descargando {ticker}...")
            
            df = yf.download(
                ticker, 
                start=inicio, 
                end=fin, 
                progress=False,
                auto_adjust=True  # Usar precios ajustados automáticamente
            )
            
            if not df.empty:
                # Yahoo Finance devuelve 'Close' cuando auto_adjust=True
                if 'Close' in df.columns:
                    datos[ticker] = df['Close']
                else:
                    errores.append(f"{ticker}: Formato inesperado")
            else:
                errores.append(f"{ticker}: Sin datos disponibles")
                
        except Exception as e:
            errores.append(f"{ticker}: {str(e)}")
        
        progress_bar.progress((idx + 1) / len(tickers))
    
    progress_bar.empty()
    status_text.empty()
    
    if errores:
        with st.expander("⚠️ Advertencias durante la descarga"):
            for error in errores:
                st.warning(error)
    
    return datos.dropna()


def calcular_metricas(datos):
    """
    Calcula métricas financieras completas.
    
    Args:
        datos: DataFrame con precios históricos
    
    Returns:
        Tuple (metricas_df, retornos_df)
    """
    retornos = datos.pct_change().dropna()
    
    metricas = pd.DataFrame()
    
    # Métricas básicas
    metricas['Precio Inicial'] = datos.iloc[0]
    metricas['Precio Final'] = datos.iloc[-1]
    metricas['Rendimiento (%)'] = ((datos.iloc[-1] / datos.iloc[0]) - 1) * 100
    
    # Métricas de riesgo
    metricas['Volatilidad Diaria (%)'] = retornos.std() * 100
    metricas['Volatilidad Anualizada (%)'] = retornos.std() * np.sqrt(252) * 100
    
    # Ratios ajustados por riesgo
    metricas['Sharpe'] = (retornos.mean() / retornos.std()) * np.sqrt(252)
    
    # Ratio Sortino (solo penaliza volatilidad negativa)
    retornos_negativos = retornos[retornos < 0]
    downside_std = retornos_negativos.std()
    metricas['Sortino'] = (retornos.mean() / downside_std) * np.sqrt(252)
    
    # Métricas de riesgo extremo
    metricas['VaR 5% (%)'] = retornos.quantile(0.05) * 100
    metricas['Max Retorno (%)'] = retornos.max() * 100
    metricas['Min Retorno (%)'] = retornos.min() * 100
    
    # Drawdown máximo
    cumulative = (1 + retornos).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    metricas['Max Drawdown (%)'] = drawdown.min() * 100
    
    return metricas.round(2), retornos


def crear_grafico_evolucion(datos_norm):
    """Crea gráfico de evolución de precios normalizado"""
    fig = go.Figure()
    
    for col in datos_norm.columns:
        fig.add_trace(
            go.Scatter(
                x=datos_norm.index,
                y=datos_norm[col],
                mode='lines',
                name=col,
                line=dict(width=2.5),
                hovertemplate='<b>%{fullData.name}</b><br>Valor: %{y:.2f}<extra></extra>'
            )
        )
    
    fig.update_layout(
        height=500,
        hovermode='x unified',
        template='plotly_white',
        yaxis_title='Índice (Base 100)',
        xaxis_title='Fecha',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    fig.add_hline(
        y=100, 
        line_dash="dash", 
        line_color="gray", 
        opacity=0.5,
        annotation_text="Nivel inicial",
        annotation_position="right"
    )
    
    return fig


def crear_grafico_riesgo_rendimiento(metricas):
    """Crea gráfico de análisis riesgo-rendimiento"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=metricas['Volatilidad Anualizada (%)'],
            y=metricas['Rendimiento (%)'],
            mode='markers+text',
            text=metricas.index,
            textposition='top center',
            textfont=dict(size=10, color='black'),
            marker=dict(
                size=20,
                color=metricas['Sharpe'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Sharpe<br>Ratio"),
                line=dict(width=2, color='white'),
                cmin=-1,
                cmax=2
            ),
            hovertemplate='<b>%{text}</b><br>' +
                         'Volatilidad: %{x:.2f}%<br>' +
                         'Rendimiento: %{y:.2f}%<br>' +
                         'Sharpe: %{marker.color:.2f}<extra></extra>'
        )
    )
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        xaxis_title='Volatilidad Anualizada (%)',
        yaxis_title='Rendimiento Total (%)',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.3)
    fig.add_vline(
        x=metricas['Volatilidad Anualizada (%)'].median(), 
        line_dash="dash", 
        line_color="gray", 
        opacity=0.3
    )
    
    return fig


def crear_grafico_correlacion(correlaciones):
    """Crea heatmap de correlaciones"""
    fig = go.Figure(
        data=go.Heatmap(
            z=correlaciones.values,
            x=correlaciones.columns,
            y=correlaciones.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlaciones.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 11},
            colorbar=dict(title="Correlación"),
            hovertemplate='%{y} vs %{x}<br>Correlación: %{z:.3f}<extra></extra>'
        )
    )
    
    fig.update_layout(
        height=500,
        template='plotly_white',
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig


# ==============================================================================
# SIDEBAR - PANEL DE CONTROL
# ==============================================================================

with st.sidebar:
    st.header("⚙️ Configuración")
    
    st.markdown("---")
    
    # Selector de activos por categoría
    st.subheader("Selección de Activos")
    
    activos_disponibles = {
        'Acciones Argentina': ['GGAL.BA', 'YPF', 'GLOB', 'PAM.BA', 'LOMA.BA'],
        'Tech USA': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA', 'TSLA'],
        'ETFs Globales': ['SPY', 'QQQ', 'EEM', 'VTI', 'IWM'],
        'Crypto': ['BTC-USD', 'ETH-USD', 'BNB-USD']
    }
    
    categoria = st.selectbox(
        "Categoría",
        list(activos_disponibles.keys()),
        help="Selecciona una categoría de activos"
    )
    
    activos_seleccionados = st.multiselect(
        "Activos a analizar",
        activos_disponibles[categoria],
        default=activos_disponibles[categoria][:3],
        help="Puedes seleccionar múltiples activos"
    )
    
    st.markdown("---")
    
    # Selector de período
    st.subheader("Período de Análisis")
    
    tipo_periodo = st.radio(
        "Tipo de período",
        ['Predefinido', 'Personalizado'],
        horizontal=True
    )
    
    if tipo_periodo == 'Predefinido':
        periodo = st.selectbox(
            "Rango temporal",
            ['1 mes', '3 meses', '6 meses', '1 año', '2 años', '5 años']
        )
        
        periodos_dias = {
            '1 mes': 30, '3 meses': 90, '6 meses': 180,
            '1 año': 365, '2 años': 730, '5 años': 1825
        }
        
        fecha_fin = datetime.now()
        fecha_inicio = fecha_fin - timedelta(days=periodos_dias[periodo])
        
    else:
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input(
                "Desde",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        with col2:
            fecha_fin = st.date_input(
                "Hasta",
                value=datetime.now(),
                max_value=datetime.now()
            )
    
    st.markdown("---")
    
    # Botón de actualización
    actualizar = st.button(
        "🔄 Actualizar Dashboard",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Información adicional
    with st.expander("ℹ️ Información"):
        st.markdown("""
        **Fuente de datos:** Yahoo Finance
        
        **Métricas calculadas:**
        - Rendimiento total
        - Volatilidad anualizada
        - Ratio Sharpe y Sortino
        - VaR (Value at Risk)
        - Drawdown máximo
        
        **Actualización:** 
        Los datos se cachean por 1 hora.
        """)
    
    # Botón para limpiar cache
    if st.button("🗑️ Limpiar Cache", use_container_width=True):
        st.cache_data.clear()
        st.success("Cache limpiado correctamente")
        st.rerun()

# ==============================================================================
# CONTENIDO PRINCIPAL
# ==============================================================================

# Título y descripción
st.title("📊 Dashboard Financiero Interactivo")
st.markdown(
    "Análisis cuantitativo de activos financieros con datos en tiempo real de Yahoo Finance"
)

st.markdown("---")

# Validación de selección
if not activos_seleccionados:
    st.warning("⚠️ Selecciona al menos un activo en el panel lateral para comenzar el análisis")
    st.stop()

# Descarga y procesamiento de datos
with st.spinner("Descargando y procesando datos..."):
    try:
        datos = descargar_datos(activos_seleccionados, fecha_inicio, fecha_fin)
    except Exception as e:
        st.error(f"Error al descargar datos: {str(e)}")
        st.stop()

if datos.empty:
    st.error("❌ No se pudieron descargar datos válidos. Verifica los tickers y el período seleccionado.")
    st.stop()

# Cálculo de métricas
metricas, retornos = calcular_metricas(datos)

# ==============================================================================
# SECCIÓN: MÉTRICAS PRINCIPALES (CARDS)
# ==============================================================================

st.subheader("📈 Resumen Ejecutivo")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Activos",
        len(datos.columns)
    )

with col2:
    mejor = metricas['Rendimiento (%)'].idxmax()
    valor = metricas.loc[mejor, 'Rendimiento (%)']
    st.metric(
        "Mejor Performer",
        mejor,
        delta=f"{valor:.1f}%",
        delta_color="normal"
    )

with col3:
    peor = metricas['Rendimiento (%)'].idxmin()
    valor = metricas.loc[peor, 'Rendimiento (%)']
    st.metric(
        "Peor Performer",
        peor,
        delta=f"{valor:.1f}%",
        delta_color="inverse"
    )

with col4:
    mejor_sharpe = metricas['Sharpe'].idxmax()
    valor = metricas.loc[mejor_sharpe, 'Sharpe']
    st.metric(
        "Mejor Sharpe",
        mejor_sharpe,
        delta=f"{valor:.2f}"
    )

with col5:
    dias_analisis = len(datos)
    st.metric(
        "Días Analizados",
        dias_analisis
    )

st.markdown("---")

# ==============================================================================
# SECCIÓN: VISUALIZACIONES EN TABS
# ==============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Evolución", 
    "🎯 Riesgo-Rendimiento", 
    "📊 Métricas", 
    "🔗 Correlaciones"
])

# TAB 1: Evolución de Precios
with tab1:
    st.subheader("Evolución Comparativa de Precios (Base 100)")
    
    datos_norm = (datos / datos.iloc[0]) * 100
    
    fig1 = crear_grafico_evolucion(datos_norm)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.markdown("---")
    
    # Detalle por activo
    st.subheader("Detalle por Activo")
    
    activo_detalle = st.selectbox(
        "Selecciona un activo para ver detalles:",
        datos.columns,
        key='detalle_activo'
    )
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        st.metric(
            "Precio Inicial", 
            f"${datos[activo_detalle].iloc[0]:.2f}"
        )
    
    with col_b:
        st.metric(
            "Precio Final", 
            f"${datos[activo_detalle].iloc[-1]:.2f}"
        )
    
    with col_c:
        cambio = ((datos[activo_detalle].iloc[-1] / datos[activo_detalle].iloc[0]) - 1) * 100
        st.metric(
            "Cambio Total", 
            f"{cambio:.2f}%",
            delta=f"{cambio:.2f}%"
        )
    
    with col_d:
        volatilidad = metricas.loc[activo_detalle, 'Volatilidad Anualizada (%)']
        st.metric(
            "Volatilidad Anual", 
            f"{volatilidad:.2f}%"
        )

# TAB 2: Riesgo-Rendimiento
with tab2:
    st.subheader("Análisis Riesgo-Rendimiento")
    
    fig2 = crear_grafico_riesgo_rendimiento(metricas)
    st.plotly_chart(fig2, use_container_width=True)
    
    st.info(
        "💡 **Interpretación:** Los activos por encima del eje horizontal (0%) tienen rendimiento positivo. "
        "El color indica el Ratio Sharpe: verde = mejor rendimiento ajustado por riesgo, "
        "rojo = peor rendimiento ajustado por riesgo."
    )
    
    # Cuadrantes
    st.markdown("---")
    st.subheader("Clasificación por Cuadrantes")
    
    vol_mediana = metricas['Volatilidad Anualizada (%)'].median()
    rend_mediano = metricas['Rendimiento (%)'].median()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Alta Performance, Baja Volatilidad** (Ideal)")
        ideal = metricas[
            (metricas['Rendimiento (%)'] > rend_mediano) & 
            (metricas['Volatilidad Anualizada (%)'] < vol_mediana)
        ]
        if not ideal.empty:
            st.success(", ".join(ideal.index.tolist()))
        else:
            st.info("Ningún activo en este cuadrante")
    
    with col2:
        st.markdown("**Baja Performance, Alta Volatilidad** (Evitar)")
        evitar = metricas[
            (metricas['Rendimiento (%)'] < rend_mediano) & 
            (metricas['Volatilidad Anualizada (%)'] > vol_mediana)
        ]
        if not evitar.empty:
            st.error(", ".join(evitar.index.tolist()))
        else:
            st.info("Ningún activo en este cuadrante")

# TAB 3: Métricas Detalladas
with tab3:
    st.subheader("Tabla de Métricas Completas")
    
    # Selector de columnas a mostrar
    columnas_disponibles = metricas.columns.tolist()
    columnas_seleccionadas = st.multiselect(
        "Selecciona métricas a visualizar:",
        columnas_disponibles,
        default=[
            'Rendimiento (%)', 
            'Volatilidad Anualizada (%)', 
            'Sharpe',
            'Max Drawdown (%)'
        ]
    )
    
    if columnas_seleccionadas:
        metricas_mostrar = metricas[columnas_seleccionadas]
        
        # Aplicar formato condicional
        st.dataframe(
            metricas_mostrar.style.background_gradient(
                subset=['Rendimiento (%)'] if 'Rendimiento (%)' in columnas_seleccionadas else [],
                cmap='RdYlGn'
            ).background_gradient(
                subset=['Sharpe'] if 'Sharpe' in columnas_seleccionadas else [],
                cmap='RdYlGn'
            ).background_gradient(
                subset=['Volatilidad Anualizada (%)'] if 'Volatilidad Anualizada (%)' in columnas_seleccionadas else [],
                cmap='YlOrRd'
            ),
            use_container_width=True,
            height=400
        )
    else:
        st.warning("Selecciona al menos una métrica para visualizar")
    
    # Botones de descarga
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_metricas = metricas.to_csv()
        st.download_button(
            label="📥 Descargar Métricas (CSV)",
            data=csv_metricas,
            file_name=f"metricas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        csv_precios = datos.to_csv()
        st.download_button(
            label="📥 Descargar Precios (CSV)",
            data=csv_precios,
            file_name=f"precios_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# TAB 4: Correlaciones
with tab4:
    st.subheader("Matriz de Correlaciones")
    
    correlaciones = retornos.corr()
    
    fig4 = crear_grafico_correlacion(correlaciones)
    st.plotly_chart(fig4, use_container_width=True)
    
    st.info(
        "💡 **Interpretación:** Valores cercanos a +1 (rojo) indican que los activos se mueven en la misma dirección. "
        "Valores cercanos a -1 (azul) indican movimientos opuestos. "
        "Valores cercanos a 0 (blanco) indican poca relación."
    )
    
    # Pares más y menos correlacionados
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Pares Más Correlacionados")
        corr_flat = correlaciones.where(
            np.triu(np.ones(correlaciones.shape), k=1).astype(bool)
        ).stack().sort_values(ascending=False)
        
        if len(corr_flat) > 0:
            for i, (par, valor) in enumerate(corr_flat.head(3).items()):
                st.metric(
                    f"{par[0]} - {par[1]}",
                    f"{valor:.3f}"
                )
    
    with col2:
        st.subheader("Pares Menos Correlacionados")
        if len(corr_flat) > 0:
            for i, (par, valor) in enumerate(corr_flat.tail(3).items()):
                st.metric(
                    f"{par[0]} - {par[1]}",
                    f"{valor:.3f}"
                )

# ==============================================================================
# SECCIÓN: ANÁLISIS AVANZADO (EXPANDIBLE)
# ==============================================================================

with st.expander("🔬 Análisis Estadístico Avanzado"):
    st.subheader("Distribución de Retornos Diarios")
    
    activo_hist = st.selectbox(
        "Selecciona activo para análisis detallado:",
        retornos.columns,
        key='analisis_avanzado'
    )
    
    # Histograma
    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Histogram(
            x=retornos[activo_hist] * 100,
            nbinsx=50,
            marker_color='steelblue',
            name='Retornos',
            hovertemplate='Rango: %{x:.2f}%<br>Frecuencia: %{y}<extra></extra>'
        )
    )
    
    fig_hist.update_layout(
        xaxis_title='Retorno Diario (%)',
        yaxis_title='Frecuencia',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    fig_hist.add_vline(
        x=0, 
        line_dash="dash", 
        line_color="red",
        annotation_text="0%"
    )
    
    st.plotly_chart(fig_hist, use_container_width=True)
    
    # Estadísticas descriptivas
    st.markdown("---")
    st.subheader("Estadísticas Descriptivas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        media = retornos[activo_hist].mean() * 100
        st.metric("Media", f"{media:.3f}%")
    
    with col2:
        std = retornos[activo_hist].std() * 100
        st.metric("Desv. Estándar", f"{std:.3f}%")
    
    with col3:
        skew = retornos[activo_hist].skew()
        st.metric("Asimetría", f"{skew:.3f}")
        if abs(skew) < 0.5:
            st.caption("Distribución simétrica")
        elif skew > 0:
            st.caption("Sesgo positivo")
        else:
            st.caption("Sesgo negativo")
    
    with col4:
        kurt = retornos[activo_hist].kurtosis()
        st.metric("Curtosis", f"{kurt:.3f}")
        if abs(kurt) < 1:
            st.caption("Normal")
        elif kurt > 1:
            st.caption("Colas pesadas")
        else:
            st.caption("Colas ligeras")

# ==============================================================================
# FOOTER
# ==============================================================================

st.markdown("---")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption(f"Período analizado: {datos.index[0].strftime('%Y-%m-%d')} a {datos.index[-1].strftime('%Y-%m-%d')}")

with col2:
    st.caption("Fuente: Yahoo Finance | Framework: Streamlit + Plotly")
    st.caption("Desarrollado para Maestría en Contabilidad y Finanzas")

with col3:
    if st.button("ℹ️ Ayuda"):
        st.info(
            "Usa el panel lateral para configurar tu análisis. "
            "Los datos se actualizan automáticamente al cambiar la selección."
        )