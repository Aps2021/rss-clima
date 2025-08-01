from fastapi import FastAPI
from fastapi.responses import Response
import requests
from datetime import datetime
import pytz
from xml.sax.saxutils import escape

app = FastAPI()

API_KEY = "2e8ac43f3a1290868e551e0cffadf135"  # <— substitua pela sua chave

# Cidades (Itamaraju deve vir primeiro para ser o sumário)
CITIES = [
    ("Itamaraju", -17.0404, -39.5389),
    ("Prado", -17.3366, -39.2226),
    ("Teixeira de Freitas", -17.5399, -39.7422),
    ("Alcobaça", -17.5194, -39.2036),
    ("Itabela", -16.5732, -39.5593),
    ("Itabatã", -18.0001, -39.8489)
]

# Mapeamento simplificado das 8 direções principais
DIRECTIONS_8 = [
    "Norte", "Nordeste", "Leste", "Sudeste",
    "Sul", "Sudoeste", "Oeste", "Noroeste"
]

def wind_direction_8(deg):
    """Converte grau em uma das 8 direções principais (português)."""
    try:
        idx = int((deg + 22.5) / 45) % 8
        return DIRECTIONS_8[idx]
    except Exception:
        return ""

def brasilia_now():
    tz = pytz.timezone("America/Sao_Paulo")
    return datetime.now(tz)

@app.get("/clima")
def clima_rss():
    now = brasilia_now()
    # pubDate padrão para RSS (com offset -0300)
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")
    updated_str = now.strftime("%d/%m/%Y %H:%M:%S")

    items_xml = []
    for city, lat, lon in CITIES:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        )
        r = requests.get(url)
        if r.status_code != 200:
            continue
        data = r.json()

        temp = round(data["main"]["temp"])
        temp_min = round(data["main"]["temp_min"])
        temp_max = round(data["main"]["temp_max"])
        feels_like = round(data["main"]["feels_like"])
        humidity = data["main"]["humidity"]
        rain = data.get("rain", {}).get("1h", 0)
        wind_speed_ms = data["wind"].get("speed", 0)
        wind_speed_kmh = round(wind_speed_ms * 3.6)
        wind_deg = data["wind"].get("deg", 0)
        direction = wind_direction_8(wind_deg)
        condition = data["weather"][0]["description"].capitalize()

        title = f"{city} – {temp}°C"
        description = (
            f"Temp mínima: {temp_min}°C; Temp máxima: {temp_max}°C; "
            f"Sensação térmica: {feels_like}°C; Condições: {condition}; "
            f"Umidade: {humidity}%; Volume de chuva: {rain} mm; "
            f"Vento: {wind_speed_kmh} km/h; Direção: {direction}; "
            f"Atualizado: {updated_str}"
        )

        item_xml = f"""
        <item>
            <title>{escape(title)}</title>
            <description>{escape(description)}</description>
            <pubDate>{pub_date}</pubDate>
        </item>
        """
        items_xml.append(item_xml)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Clima – Extremo Sul da Bahia</title>
    <link>https://rss-clima.onrender.com/clima</link>
    <description>Previsão do tempo para cidades selecionadas</description>
    <language>pt-br</language>
    <lastBuildDate>{pub_date}</lastBuildDate>
    {''.join(items_xml)}
  </channel>
</rss>
"""

    return Response(content=rss, media_type="application/xml")
