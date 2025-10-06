# Taller-comunicacion-financiera
Material del Taller de Comunicación Financiera orientado al uso de Python en el análisis de datos económicos y financieros. Incluye un cuaderno ejecutable en Google Colab, un script de Streamlit para visualizaciones interactivas, el enlace al lookerstudio y la presentación teórica en formato PDF.

Este repositorio contiene los materiales de la **Clase 1 del Taller de Comunicación Financiera**, orientado al uso de **Python** en el análisis de datos financieros, la creación de dashboards interactivos y la comunicación visual de resultados económicos.

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/DrDarioDiaz/Taller-comunicacion-financiera/blob/main/notebooks/Clase1_Python_Comunicacion.ipynb)

---

## 🎯 Objetivo del repositorio

El propósito de este repositorio es ofrecer un entorno reproducible para:

* Ejecutar los análisis presentados en clase mediante un notebook en **Google Colab** o **Jupyter**.
* Desplegar un **dashboard financiero interactivo** desarrollado con **Streamlit**.
* Acceder a los **datos originales** utilizados durante la sesión.
* Consultar las **visualizaciones** y la **presentación teórica** asociadas a la clase.

---

## 🗂️ Estructura del proyecto

```
notebooks/
└─ Clase1_Python_Comunicacion.ipynb   → Notebook principal (Colab o Jupyter)

app/
├─ dashboard_financiero.py            → Dashboard local con Streamlit
└─ clase1_python_comunicacion.py      → Script auxiliar de la clase

data/
├─ analisis_completo.csv
├─ datos_fundamentales.csv
├─ matriz_correlaciones.csv
├─ metricas_avanzadas.csv
├─ metricas_basicas.csv
├─ precios_historicos.csv
└─ retornos_diarios.csv               → Conjuntos de datos financieros utilizados

html/
├─ 01_evolucion_precios.html
├─ 03_riesgo_rendimiento.html
├─ 07_dashboard_completo.html
├─ 08_dashboard_filtros.html
└─ 09_dashboard_slider.html           → Visualizaciones exportadas de la clase

slides/
└─ Clase_1_Maestría_en_Finanzas_y_Contabilidad_Posdoctorado.pdf → Presentación teórica

links/
└─ Enlace a lookerstudio.txt          → Referencia al tablero en Looker Studio
```

---

## ▶️ Ejecución del notebook en Google Colab

1. Haz clic en el badge superior o abre directamente:
   [**Abrir en Google Colab**](https://colab.research.google.com/github/DrDarioDiaz/Taller-comunicacion-financiera/blob/main/notebooks/Clase1_Python_Comunicacion.ipynb)
2. Ejecuta las celdas de manera secuencial.
3. Si el notebook requiere datos locales, se asume la estructura de carpetas indicada arriba (`data/`, `html/`, etc.).

---

## 💻 Ejecución del dashboard local con Streamlit

### 1️⃣ Instalar dependencias

Crea un entorno virtual (opcional pero recomendable) y ejecuta:

```bash
python -m venv .venv
.venv\Scripts\activate          # En Windows
pip install -r requirements.txt
```

Si no cuentas con `requirements.txt`, instala manualmente:

```bash
pip install streamlit pandas numpy matplotlib plotly
```

### 2️⃣ Ejecutar la aplicación

Desde la carpeta raíz del repositorio:

```bash
streamlit run app/dashboard_financiero.py
```

La aplicación se abrirá automáticamente en el navegador, usualmente en
🔗 `http://localhost:8501`

---

## 📦 Dependencias sugeridas (`requirements.txt`)

```
streamlit>=1.36
pandas>=2.2
numpy>=1.26
matplotlib>=3.8
plotly>=5.22
```

Si tu dashboard usa librerías adicionales (por ejemplo, `yfinance`, `scipy`, `seaborn`), añádelas en este archivo.

---

## 📑 Licencias

* **Código fuente** (`.py`, `.ipynb`): Licencia **MIT**.
* **Material docente** (PDF, HTML, datos, slides): Licencia **Creative Commons BY 4.0**.

> Se permite reutilizar y adaptar el material siempre que se otorgue el crédito correspondiente al autor original.

---

## 🤝 Contribuciones y contacto

Las sugerencias o mejoras son bienvenidas.
Podés abrir un *issue* o enviar un *pull request* con tus propuestas.

Autor: **Dr. Darío Ezequiel Díaz**
📧 [drdarioezequieldiaz@gmail.com](mailto:drdarioezequieldiaz@gmail.com)
🌐 [GitHub — DrDarioDiaz](https://github.com/DrDarioDiaz)

---

## 🧟‍♂️ Nota final

Este material forma parte del Taller de Comunicación Financiera, enfocado en la integración de **herramientas de análisis de datos, visualización y comunicación estadística aplicada a las finanzas**.
Su objetivo es fomentar prácticas reproducibles y transparentes en la presentación de resultados financieros y económicos.

---
