# Trends Monitoring Project

## Objective
Automatically track Google Trends in Guatemala for "Law & Government" and "Politics", analyze the data, and generate professional PDF reports.

## Workflows
1. **Fetch:** Get real-time trending searches from Google Trends for Guatemala (Category 19).
2. **Visualize:** Generate interest-over-time charts for the top 3 trends.
3. **Report:** Create a professional one-page summary in PDF format.
4. **Automate:** Run daily via GitHub Actions.

## Summary Generation Protocol (Prompt)
Para cada tendencia, el sistema debe generar un resumen siguiendo estas instrucciones:

- **Formato:** Un solo párrafo de 300-450 caracteres.
- **Estructura:** “La búsqueda “[término]” aparece como tendencia activa en Google Trends, con más de [volumen] búsquedas, un aumento de [porcentaje] y actividad registrada hace [tiempo]. Según reportes de [medio 1], [medio 2] y [medio 3], [resumen integrado de los hechos].”
- **Tono:** Descriptivo, neutral y no opinativo.
- **Atribución:** Integrar los nombres de los medios en el texto, no URLs.
- **Evitar:** Opiniones, lenguaje inflamatorio, repeticiones o detalles secundarios.
