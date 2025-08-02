import feedparser
from fastapi import FastAPI
from fastapi.responses import Response
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape
import html
import re
import requests

app = FastAPI()

# Função de tradução com LibreTranslate (gratuito)
def translate_text(text, target_lang="pt"):
    try:
        response = requests.post(
            "https://libretranslate.com/translate",
            data={
                "q": text,
                "source": "en",
                "target": target_lang,
                "format": "text"
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()["translatedText"]
    except Exception:
        pass
    return text  # fallback

# Função para limpar HTML da descrição do NME
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', html.unescape(raw_html))
    return cleantext.strip()

# Hora de Brasília
def brasilia_now():
    return datetime.now(timezone(timedelta(hours=-3)))

@app.get("/news")
def news_feed():
    feeds = [
        ("Billboard", "https://www.billboard.com/c/music/music-news/feed/"),
        ("NME", "https://www.nme.com/news/music/feed")
    ]

    now = brasilia_now()
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    items = []

    for source_name, url in feeds:
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:30]:
            title = translate_text(entry.title)
            description = entry.get("description", "")
            if source_name == "NME":
                description = clean_html(description)
            else:
                description = html.unescape(description)

            description = translate_text(description)
            full_description = f"{source_name}: {description}"

            pub = now.strftime("%a, %d %b %Y %H:%M:%S %z")

            items.append(f"""
            <item>
                <title>{escape(title)}</title>
                <description>{escape(full_description)}</description>
                <pubDate>{pub}</pubDate>
            </item>
            """)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Notícias musicais – Billboard e NME</title>
    <link>https://rss-clima.onrender.com/news</link>
    <description>Últimas notícias musicais traduzidas para português</description>
    <language>pt-br</language>
    <lastBuildDate>{pub_date}</lastBuildDate>
    {''.join(items[:60])}
  </channel>
</rss>
"""
    return Response(content=rss, media_type="application/xml")
