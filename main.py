from fastapi import FastAPI, Response
import requests
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

app = FastAPI()

API_KEY = "2e8ac43f3a1290868e551e0cffadf135"
CITIES = [
    ("Itamaraju", -17.0401, -39.5389),
    ("Prado", -17.3366, -39.2226),
    ("Teixeira de Freitas", -17.5399, -39.7422),
    ("Alcobaça", -17.5194, -39.2036),
    ("Itabela", -16.5732, -39.5593),
    ("Itabatã", -18.0001, -39.8489),
]

@app.get("/clima/")
def clima_rss():
    items = []
    for city, lat, lon in CITIES:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        r = requests.get(url)
        if r.status_code != 200:
            continue

        data = r.json()
        now = datetime.utcnow() - timedelta(hours=3)  # Ajuste para horário de Brasília
        last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
        pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        temp = round(data["main"]["temp"])
        humidity = data["main"]["humidity"]
        wind = round(data["wind"]["speed"])
        weather = data["weather"][0]["description"].capitalize()
        rain = data.get("rain", {}).get("1h", 0)

        title = f"{city} – {temp}°C – {weather}"
        desc = (
            f"Temperatura: {temp}°C<br>"
            f"Umidade: {humidity}%<br>"
            f"Vento: {wind} km/h<br>"
            f"Chuva: {rain} mm<br>"
            f"Condições: {weather}<br>"
            f"Atualizado: {last_updated}"
        )

        items.append(f"""
        <item>
            <title>{escape(title)}</title>
            <description>{escape(desc)}</description>
            <pubDate>{pub_date}</pubDate>
        </item>
        """)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
        <title>Clima – Extremo Sul da Bahia</title>
        <link>https://openweathermap.org/</link>
        <description>Boletim meteorológico atualizado</description>
        {''.join(items)}
    </channel>
    </rss>
    """

    return Response(content=rss, media_type="application/rss+xml")
