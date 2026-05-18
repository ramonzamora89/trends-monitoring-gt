import json
import os
import matplotlib.pyplot as plt
from trendspy import Trends
import pandas as pd

def generate_trend_charts(trends_path, output_dir):
    if not os.path.exists(trends_path):
        print(f"Trends file not found: {trends_path}")
        return

    with open(trends_path, 'r', encoding='utf-8') as f:
        trends = json.load(f)

    if not trends:
        print("No trends to visualize.")
        return

    os.makedirs(output_dir, exist_ok=True)
    try:
        tr = Trends()
    except Exception as e:
        print(f"Failed to initialize Trends: {e}")
        return

    for i, trend in enumerate(trends):
        title = trend['title']
        print(f"Generating chart for: {title}")
        
        try:
            # interest_over_time in Trends class
            # Returns a dict or dataframe depending on version, usually dataframe
            df = tr.interest_over_time([title], timeframe='now 1-d', geo='GT')

            if df is not None and not df.empty:
                plt.figure(figsize=(10, 4))
                # Ensure we use the correct column
                col = title if title in df.columns else df.columns[0]
                plt.plot(df.index, df[col], color='#1a73e8', linewidth=2)
                plt.fill_between(df.index, df[col], color='#1a73e8', alpha=0.1)
                
                plt.title(f"Interés en el tiempo: {title}", fontsize=14, pad=20)
                plt.xlabel("Tiempo", fontsize=10)
                plt.ylabel("Interés", fontsize=10)
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                plt.tight_layout()
                
                chart_path = os.path.join(output_dir, f"trend_{i+1}.png")
                plt.savefig(chart_path, dpi=150)
                plt.close()
                print(f"Chart saved: {chart_path}")
                trend['chart_path'] = os.path.abspath(chart_path)
            else:
                print(f"No historical data found for: {title}")

        except Exception as e:
            print(f"Error visualizing {title}: {e}")

    # Update trends JSON with absolute chart paths
    with open(trends_path, 'w', encoding='utf-8') as f:
        json.dump(trends, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    trends_file = os.path.join(script_dir, "..", "data", "latest_trends.json")
    charts_output = os.path.join(script_dir, "..", "outputs", "charts")
    
    generate_trend_charts(trends_file, charts_output)
