import json
import os
import re
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.0-flash')
else:
    print("Warning: GEMINI_API_KEY not found. Falling back to simulated summaries.")
    model = None

def generate_ai_summary(trend):
    """
    Generates a summary using Gemini API following the protocol in PROJECT.md.
    If API is unavailable, falls back to simulated synthesis.
    """
    title = trend['title']
    volume = trend['traffic']
    growth = trend['growth']
    time = trend['activity_time']
    news_items = trend.get('news', [])
    
    # Extract facts for the prompt
    news_context = ""
    medios = []
    if news_items:
        for i, item in enumerate(news_items, 1):
            news_context += f"{i}. {item['title']} (Fuente: {item['source']})\n"
            if item.get('source') and item['source'] not in medios:
                medios.append(item['source'])

    if model and news_items:
        prompt = f"""
        Eres un periodista experto en Smart Brevity. Genera un resumen de tendencia para el siguiente término: "{title}".
        
        DATOS DE LA TENDENCIA:
        - Tráfico: {volume}
        - Crecimiento: {growth}
        - Tiempo activa: {time}
        
        NOTICIAS RELACIONADAS:
        {news_context}
        
        PROTOCOLO DE GENERACIÓN (ESTRICTO):
        1. Formato: Un solo párrafo de 300-450 caracteres.
        2. Estructura obligatoria: "La búsqueda "{title}" aparece como tendencia activa en Google Trends, con más de {volume} búsquedas, un aumento de {growth} y actividad registrada hace {time}. Según reportes de [medios], [resumen integrado de los hechos]."
        3. Tono: Descriptivo, neutral y no opinativo.
        4. Atribución: Integra los nombres de los medios ({', '.join(medios)}) de forma natural en el texto. NO uses URLs.
        5. Evita: Opiniones, lenguaje inflamatorio ("brutal", "estalló"), repeticiones o detalles secundarios.
        6. NO uses negritas ni formatos especiales.
        
        Genera el párrafo ahora:
        """
        try:
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip()
        except Exception as e:
            print(f"Error calling Gemini API: {e}")

    # Fallback simulation if model fails or no news
    summary = f"La búsqueda “{title}” aparece como tendencia activa en Google Trends, con más de {volume} búsquedas, un aumento de {growth} y actividad registrada hace {time}. "
    
    if news_items:
        if len(medios) > 1:
            medios_str = ", ".join(medios[:-1]) + f" y {medios[-1]}"
        elif medios:
            medios_str = medios[0]
        else:
            medios_str = "diversos medios"
            
        main_fact = news_items[0]['title']
        main_fact = re.sub(r' - .*$', '', main_fact)
        main_fact = re.sub(r' \| .*$', '', main_fact)
        summary += f"Según reportes de {medios_str}, {main_fact}, lo que ha generado interés y seguimiento sobre el impacto de esta noticia."
    else:
        summary += "A pesar del alto volumen de búsqueda, no se han detectado reportes de prensa directos vinculados en este momento."
    
    return summary

def build_markdown_report(trends_path, output_md):
    if not os.path.exists(trends_path):
        print(f"Trends file not found: {trends_path}")
        return

    with open(trends_path, 'r', encoding='utf-8') as f:
        trends = json.load(f)

    if not trends:
        print("No trends to report.")
        return

    date_str = datetime.now().strftime("%Y-%m-%d")
    
    md_content = []
    md_content.append(f"# Reporte de Tendencias Políticas — {date_str}")
    md_content.append("\n**Monitoreo de Tendencias — Guatemala**")
    md_content.append("\n**Resumen del día:** Este reporte identifica las principales tendencias de búsqueda en Guatemala dentro de la categoría de Política y Gobierno en las últimas 24 horas.")
    
    for i, trend in enumerate(trends):
        md_content.append(f"\n## {i+1}. {trend['title']}")
        md_content.append(f"*Tráfico: {trend['traffic']} | Temas: {', '.join(trend['topics'])}*")
        
        # Use the updated summary logic
        summary = generate_ai_summary(trend)
        md_content.append(f"\n{summary}")
        
        if trend.get('news'):
            md_content.append("\n### Fuentes y contexto")
            for item in trend['news']:
                md_content.append(f"- [{item['title']}]({item['url']}) ({item['source']})")
        
        if trend.get('chart_path'):
            # Use relative path for Markdown preview compatibility
            rel_chart_path = os.path.relpath(trend['chart_path'], os.path.dirname(output_md))
            md_content.append(f"\n![Gráfica de interés]({rel_chart_path})")
            
        md_content.append("\n---")
        
    md_content.append("\n### Metodología")
    md_content.append("Datos extraídos de Google Trends para Guatemala. Se priorizan tendencias con crecimiento acelerado en las últimas 24 horas.")
    
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
    
    print(f"Reporte Markdown generado exitosamente: {output_md}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    trends_file = os.path.join(script_dir, "..", "data", "latest_trends.json")
    
    date_suffix = datetime.now().strftime("%Y-%m-%d")
    output_md = os.path.join(script_dir, "..", "outputs", f"reporte_tendencias_{date_suffix}.md")
    
    os.makedirs(os.path.dirname(output_md), exist_ok=True)
    build_markdown_report(trends_file, output_md)
