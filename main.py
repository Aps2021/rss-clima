from fastapi import FastAPI, Response
import requests
from datetime import datetime
from xml.sax.saxutils import escape

app = FastAPI()

# Substitua pela sua chave da OpenWeatherMap
API_KEY = "2e8ac43f3a1290868e551e0cffadf135"

# Direções do vento por graus
DIRECOES = ["Norte", "NNE", "Nordeste", "ENE", "Leste", "ESE", "Sudeste", "SSE",
            "Sul", "SSO", "Sudoeste", "OSO", "Oeste", "ONO", "Noroeste", "NNO"]

# Lista de cidades com nome e coordenadas
CITIES = [
    ("Itamaraju", -17.0404, -39.5389),
    ("Prado", -17.3400, -39.2200),
    ("Teixeira de Freitas", -17.5392, -39.7400),
    ("Alcobaça", -17.5193, -39.2036),
    ("Itabela", -16.5732, -39.5592),
    ("Itabatã", -18.5712, -39.5478)
]

def direcao_vento(deg):
    idx = int((deg + 11.25) / 22.5) % 16
    return DIRECOES[idx]

@app.get("/clima")
def clima_rss():
    items = []
    for city, lat, lon in CITIES:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&lang=pt_br&appid={API_KEY}"
        r = requests.get(url)
        data = r.json()

        now = datetime.utcnow()
        last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
        pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        temp = round(data['main']['temp'])
        temp_min = round(data['main']['temp_min'])
        temp_max = round(data['main']['temp_max'])
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']
        rain = data.get('rain', {}).get('1h', 0)
        wind_speed = round(data['wind']['speed'])
        wind_deg = data['wind'].get('deg', 0)
        wind_dir = direcao_vento(wind_deg)
        condicao = data['weather'][0]['description'].capitalize()

        title = f"{city} – {temp}°C"
        description = (
            f"Temperatura mínima: {temp_min}°C; "
            f"Temperatura máxima: {temp_max}°C; "
            f"Sensação térmica: {feels_like}°C; "
            f"Condições: {condicao}; "
            f"Umidade: {humidity}%; "
            f"Chuva: {rain} mm; "
            f"Vento: {wind_speed} km/h ({wind_dir}); "
            f"Atualizado: {last_updated}"
        )

        items.append(f"""
        <item>
            <title>{escape(title)}</title>
            <description>{escape(description)}</description>
            <pubDate>{pub_date}</pubDate>
        </item>
        """)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
        <title>Previsão do Tempo</title>
        <link>https://rss-clima.onrender.com/clima</link>
        <description>Feed RSS com o clima de várias cidades</description>
        {''.join(items)}
    </channel>
    </rss>
    """

    return Response(content=rss, media_type="application/xml")
