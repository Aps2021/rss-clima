from fastapi import FastAPI
from fastapi.responses import Response
import requests
from datetime import datetime, timezone, timedelta
from xml.sax.saxutils import escape
import feedparser
from deep_translator import GoogleTranslator

app = FastAPI()

API_KEY = "1c115bd918454725b52191344250208"  # Chave da WeatherAPI

CITIES = [
    ("Itamaraju", -17.0404, -39.5389),
    ("Prado", -17.3366, -39.2226),
    ("Teixeira de Freitas", -17.5399, -39.7422),
    ("Alcobaça", -17.5194, -39.2036),
    ("Itabela", -16.5732, -39.5593),
    ("Itabatã", -18.0001, -39.8489)
]

DIRECTIONS_8 = [
    "Norte", "Nordeste", "Leste", "Sudeste",
    "Sul", "Sudoeste", "Oeste", "Noroeste"
]

def wind_direction_8(deg):
    try:
        idx = int((deg + 22.5) / 45) % 8
        return DIRECTIONS_8[idx]
    except Exception:
        return ""

def brasilia_now():
    tz = timezone(timedelta(hours=-3))
    return datetime.now(tz)

@app.get("/clima")
def clima_rss():
    now = brasilia_now()
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    updated_str = now.strftime("%d/%m/%Y %H:%M:%S")

    items_xml = []
    for city, lat, lon in CITIES:
        url = (
            f"http://api.weatherapi.com/v1/forecast.json"
            f"?key={API_KEY}&q={lat},{lon}&days=1&lang=pt"
        )
        r = requests.get(url)
        if r.status_code != 200:
            continue
        data = r.json()
        current = data["current"]
        forecast = data["forecast"]["forecastday"][0]["day"]

        temp = round(current["temp_c"])
        feels_like = round(current["feelslike_c"])
        condition = current["condition"]["text"]
        humidity = current["humidity"]
        wind_kph = current["wind_kph"]
        wind_deg = current["wind_degree"]
        direction = wind_direction_8(wind_deg)

        temp_min = round(forecast["mintemp_c"])
        temp_max = round(forecast["maxtemp_c"])
        rain = forecast.get("daily_chance_of_rain", 0)

        title = f"{city} – {temp}°C (última leitura)"
        description = (
            f"Temp mínima: {temp_min}°C; Temp máxima: {temp_max}°C; "
            f"Sensação térmica: {feels_like}°C; Condições: {condition}; "
            f"Umidade: {humidity}%; Volume de chuva: {rain}%; "
            f"Vento: {wind_kph} km/h; Direção: {direction}; "
            f"Atualizado: {updated_str}"
        )

        item_xml = f"<item><title>{escape(title)}</title><description>{escape(description)}</description><pubDate>{pub_date}</pubDate></item>"
        items_xml.append(item_xml)

    rss = f"<?xml version='1.0' encoding='UTF-8' ?><rss version='2.0'><channel><title>Clima – Extremo Sul da Bahia</title><link>https://rss-clima.onrender.com/clima</link><description>Previsão do tempo para cidades selecionadas</description><language>pt-br</language><lastBuildDate>{pub_date}</lastBuildDate>{''.join(items_xml)}</channel></rss>"
    return Response(content=rss, media_type="application/xml")

@app.get("/news")
def news_rss():
    now = brasilia_now()
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")

    feeds = [
        ("Billboard", "https://www.billboard.com/c/music/music-news/feed/"),
        ("NME", "https://www.nme.com/news/music/feed")
    ]

    items = []
    translator = GoogleTranslator(source="en", target="pt")

    for source_name, url in feeds:
        d = feedparser.parse(url)
        for entry in d.entries[:30]:
            try:
                title = translator.translate(entry.title)
                description_raw = entry.description
                description_clean = translator.translate(description_raw.split("<")[0])  # remove HTML
                description = f"{source_name}: {description_clean}"
                pub = entry.published
                item = f"<item><title>{escape(title)}</title><description>{escape(description)}</description><pubDate>{pub}</pubDate></item>"
                items.append(item)
            except Exception:
                continue

    rss = f"<?xml version='1.0' encoding='UTF-8' ?><rss version='2.0'><channel><title>Notícias de Música – Billboard e NME</title><link>https://rss-clima.onrender.com/news</link><description>Últimas notícias musicais traduzidas para o português</description><language>pt-br</language><lastBuildDate>{pub_date}</lastBuildDate>{''.join(items)}</channel></rss>"
    return Response(content=rss, media_type="application/xml")
