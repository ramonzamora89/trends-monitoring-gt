# Monitor de Tendencias Políticas - Guatemala 🇬🇹

Sistema automatizado de monitoreo de tendencias de búsqueda en Google Trends para Guatemala, enfocado en las categorías de **Política y Gobierno** y **Leyes**.

## 🚀 Funcionalidades
- **Extracción Inteligente:** Obtiene tendencias en tiempo real usando la API de Trendspy y RSS.
- **Filtrado Temático:** Prioriza estrictamente temas de política y leyes, excluyendo deportes y entretenimiento.
- **Análisis con IA:** Utiliza la API de Gemini (Google) para sintetizar noticias vinculadas en resúmenes estilo *Smart Brevity*.
- **Visualización:** Genera gráficas de interés histórico para las principales tendencias.
- **Reportes Profesionales:** Produce documentos PDF listos para distribución.
- **Automatización:** Ejecución diaria programada mediante GitHub Actions.

## 🛠️ Instalación Local

1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Activar el entorno: `source venv/bin/activate` (Mac/Linux).
4. Instalar dependencias: `pip install -r trendsMonitoring/requirements.txt`.
5. Configurar el archivo `.env` con tu clave de API: `GEMINI_API_KEY=tu_clave_aqui`.

## 🤖 Automatización (GitHub Actions)
El reporte se genera automáticamente todos los días a las 06:00 UTC. Para que funcione la IA, debes configurar un **Repository Secret** en GitHub llamado `GEMINI_API_KEY`.

## 📂 Estructura del Proyecto
- `scripts/`: Lógica de extracción, visualización y reporte.
- `data/`: Datos crudos de las últimas tendencias.
- `outputs/`: Reportes generados en Markdown y PDF.
- `templates/`: Plantillas HTML para el diseño del reporte.

---
*Desarrollado como parte del kit de herramientas de periodismo asistido por IA.*
