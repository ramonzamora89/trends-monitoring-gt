import json
import os
import re
import unicodedata
import pandas as pd
import feedparser
from trendspy import Trends

def normalize_text(text):
    """
    Normalizes text for robust comparison: lowercase, remove accents, and strip special chars.
    """
    if not text:
        return ""
    # Lowercase
    text = text.lower()
    # Remove accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text)
                  if unicodedata.category(c) != 'Mn')
    # Remove special chars but keep spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text.strip()

def get_trending_rss(geo='GT'):
    """
    Fetches trending searches using the stable 2026 RSS feed.
    """
    print(f"Fetching trending searches via RSS for {geo}...")
    # Updated URL for 2026
    url = f"https://trends.google.com/trending/rss?geo={geo}&hl=es-{geo}"
    feed = feedparser.parse(url)
    
    trends = []
    if not feed.entries:
        print(f"No RSS entries found for {geo} at {url}.")
        return []

    for entry in feed.entries[:10]: # Look at top 10 to allow for filtering
        traffic = getattr(entry, 'ht_approx_traffic', 'N/A')
        
        # Parse news items
        news_items = []
        if 'ht_news_item' in entry:
            # feedparser might put multiple items in a list or single dict
            items = entry['ht_news_item']
            if isinstance(items, dict): items = [items]
            for item in items:
                news_items.append({
                    "title": item.get('ht_news_item_title'),
                    "url": item.get('ht_news_item_url'),
                    "source": item.get('ht_news_item_source')
                })

        trend_data = {
            "title": entry.title,
            "traffic": traffic,
            "news": news_items,
            "timestamp": pd.Timestamp.now().isoformat(),
            "topics": [] # RSS doesn't give topics directly
        }
        trends.append(trend_data)
    return trends

def fetch_guatemala_trends():
    """
    Fetches trending searches for Guatemala.
    Combines Trendspy for filtering and news extraction.
    """
    print("Connecting to Trendspy API for real-time trends...")
    rss_trends = get_trending_rss('GT')

    try:
        tr = Trends()
        trend_list = tr.trending_now(geo='GT')

        if trend_list:
            top_trends = []
            categories_of_interest = ["Politics", "Law and Government"]
            categories_to_exclude = ["Sports", "Entertainment"]

            # 1. Try to find filtered trends
            for trend in trend_list:
                is_relevant = any(cat in trend.topic_names for cat in categories_of_interest)
                is_excluded = any(cat in trend.topic_names for cat in categories_to_exclude)
                
                if is_relevant and not is_excluded:
                    # A. Primary: Get news directly via API tokens
                    news = []
                    if hasattr(trend, 'news_tokens') and trend.news_tokens:
                        try:
                            api_news = tr.trending_now_news_by_ids(trend.news_tokens)
                            for item in api_news:
                                news.append({
                                    "title": item.title,
                                    "url": item.url,
                                    "source": item.source
                                })
                        except Exception as e:
                            print(f"Warning: Failed to fetch direct news for '{trend.keyword}': {e}")

                    # B. Secondary: Fallback to RSS with normalized matching
                    if not news:
                        norm_keyword = normalize_text(trend.keyword)
                        for rt in rss_trends:
                            norm_rss_title = normalize_text(rt['title'])
                            if norm_keyword in norm_rss_title or norm_rss_title in norm_keyword:
                                news = rt['news']
                                break

                    trend_data = {
                        "title": trend.keyword,
                        "traffic": f"{trend.volume}+",
                        "growth": f"{trend.volume_growth_pct}%" if hasattr(trend, 'volume_growth_pct') and trend.volume_growth_pct else "crecimiento acelerado",
                        "activity_time": f"{round(trend.hours_since_started(), 1)} horas" if hasattr(trend, 'hours_since_started') and callable(trend.hours_since_started) else "reciente",
                        "topics": trend.topic_names,
                        "news": news,
                        "timestamp": pd.Timestamp.now().isoformat()
                    }
                    top_trends.append(trend_data)
                    if len(top_trends) >= 3:
                        break

            # 2. Fallback to top general trends if fewer than 3 political found (EXCLUDING sports/ent)
            if len(top_trends) < 3:
                print(f"Only {len(top_trends)} political trends found. Filling with non-sports general trends...")
                for trend in trend_list:
                    # Skip if already added
                    if any(t['title'] == trend.keyword for t in top_trends):
                        continue
                    
                    # STRICT FILTER: Skip sports and entertainment
                    if any(cat in trend.topic_names for cat in categories_to_exclude):
                        continue
                    
                    news = []
                    # Try API news first
                    if hasattr(trend, 'news_tokens') and trend.news_tokens:
                        try:
                            api_news = tr.trending_now_news_by_ids(trend.news_tokens)
                            news = [{"title": n.title, "url": n.url, "source": n.source} for n in api_news]
                        except: pass

                    # Try RSS fallback
                    if not news:
                        norm_keyword = normalize_text(trend.keyword)
                        for rt in rss_trends:
                            if norm_keyword in normalize_text(rt['title']):
                                news = rt['news']
                                break

                    trend_data = {
                        "title": trend.keyword,
                        "traffic": f"{trend.volume}+",
                        "growth": f"{trend.volume_growth_pct}%" if hasattr(trend, 'volume_growth_pct') and trend.volume_growth_pct else "crecimiento acelerado",
                        "activity_time": f"{round(trend.hours_since_started(), 1)} horas" if hasattr(trend, 'hours_since_started') and callable(trend.hours_since_started) else "reciente",
                        "topics": trend.topic_names,
                        "news": news,
                        "timestamp": pd.Timestamp.now().isoformat()
                    }
                    top_trends.append(trend_data)
                    if len(top_trends) >= 3:
                        break

            return top_trends

    except Exception as e:
        print(f"Trendspy API failed: {e}")

    # 3. Fallback to pure RSS if API fails entirely
    final_rss = []
    for rt in rss_trends[:3]:
        final_rss.append({
            "title": rt['title'],
            "traffic": rt['traffic'],
            "growth": "crecimiento constante",
            "activity_time": "reciente",
            "topics": ["General"],
            "news": rt['news'],
            "timestamp": rt['timestamp']
        })
    return final_rss


def save_trends(trends, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(trends, f, indent=4, ensure_ascii=False)
    print(f"Trends saved to {output_path}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "..", "data", "latest_trends.json")
    
    trends = fetch_guatemala_trends()
    if trends:
        save_trends(trends, output_file)
    else:
        print("Failed to acquire trend data.")
