import os
import sys
import re
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import markdown

def md_to_pdf(input_md, template_dir, output_pdf):
    if not os.path.exists(input_md):
        print(f"Markdown file not found: {input_md}")
        return

    with open(input_md, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert Markdown to HTML components
    # We split by '## ' to extract trends if we want to use the Jinja template structure,
    # or just convert the whole thing to HTML and wrap it.
    
    # Approach: Convert MD to HTML and pass it to a wrapper template
    html_content = markdown.markdown(md_text, extensions=['fenced_code', 'tables'])
    
    # Simple cleanup for images (make them absolute for WeasyPrint)
    base_path = os.path.dirname(os.path.abspath(input_md))
    html_content = html_content.replace('src="charts/', f'src="file://{base_path}/charts/')

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('trends_report.html')
    
    # We need to adapt the template to accept a 'body' variable instead of looping
    # Or we can just use a simple wrapper
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_title = f"Reporte de Tendencias — {date_str}"

    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: letter; margin: 0.5in; }}
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            h1 {{ color: #1a73e8; border-bottom: 2px solid #1a73e8; padding-bottom: 10px; }}
            h2 {{ color: #1a73e8; margin-top: 30px; }}
            h3 {{ color: #555; font-size: 12pt; text-transform: uppercase; margin-top: 20px; }}
            a {{ color: #1a73e8; text-decoration: none; }}
            img {{ width: 100%; max-height: 300px; display: block; margin: 20px 0; }}
            hr {{ border: 0; border-top: 1px solid #eee; margin: 40px 0; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # Generate PDF
    HTML(string=full_html, base_url=base_path).write_pdf(output_pdf)
    print(f"PDF generado desde Markdown: {output_pdf}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        date_suffix = datetime.now().strftime("%Y-%m-%d")
        input_file = os.path.join(script_dir, "..", "outputs", f"reporte_tendencias_{date_suffix}.md")

    output_file = input_file.replace('.md', '.pdf')
    template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates")
    
    md_to_pdf(input_file, template_folder, output_file)
