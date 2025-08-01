from fastapi import FastAPI, Response
import requests
from datetime import datetime
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
        now = datetime.now()
        last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
        pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        title = f"{city} – {round(data['main']['temp'])}°C – {data['weather'][0]['description'].capitalize()}"
        desc = (
            f"Umidade: {data['main']['humidity']}%<br>"
            f"Vento: {round(data['wind']['speed'])} km/h<br>"
            f"Last Updated: {last_updated}"
        )

        items.append(f"""
<item>
  <title>{escape(title)}</title>
  <description>{escape(desc)}</description>
  <pubDate>{pub_date}</pubDate>
</item>""")

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Previsão do Tempo – Extremo Sul da Bahia</title>
  <link>https://openweathermap.org/</link>
  <description>Clima atualizado para 6 cidades da Bahia</description>
  {''.join(items)}
</channel>
</rss>"""
    return Response(content=rss, media_type="application/rss+xml")
