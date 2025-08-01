from fastapi import FastAPI, Response
import requests
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

app = FastAPI()

API_KEY = "2e8ac43f3a1290868e551e0cffadf135"  # 🔁 Substitua pela sua chave do OpenWeatherMap

CITIES = [
    ("Itamaraju", -17.0404, -39.5389),
    ("Prado", -17.3365, -39.2226),
    ("Teixeira de Freitas", -17.5399, -39.7412),
    ("Alcobaça", -17.5196, -39.2036),
    ("Itabela", -16.5732, -39.5597),
    ("Itabatã", -17.7796, -39.8999)
]

# ✅ Direção do vento: 8 pontos principais
DIRECOES = [
    "Norte", "Nordeste", "Leste", "Sudeste",
    "Sul", "Sudoeste", "Oeste", "Noroeste"
]

def direcao_vento(deg):
    idx = int((deg + 22.5) / 45) % 8
    return DIRECOES[idx]

@app.get("/clima")
def clima_rss():
    items = []
    now = datetime.utcnow() - timedelta(hours=3)  # UTC-3
    last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S BRT")

    for city, lat, lon in CITIES:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        r = requests.get(url)
        data = r.json()

        temp = round(data['main']['temp'])
        temp_min = round(data['main']['temp_min'])
        temp_max = round(data['main']['temp_max'])
        feels_like = round(data['main']['feels_like'])
        humidity = data['main']['humidity']
        wind_speed = round(data['wind']['speed'])
        wind_deg = data['wind']['deg']
        vento_dir = direcao_vento(wind_deg)
        chuva = data.get('rain', {}).get('1h', 0)
        condicoes = data['weather'][0]['description'].capitalize()

        titulo = f"{city} – {temp}°C"
        descricao = (
            f"Temperatura mínima: {temp_min}°C; "
            f"Temperatura máxima: {temp_max}°C; "
            f"Sensação térmica: {feels_like}°C; "
            f"Condições: {condicoes}; "
            f"Umidade: {humidity}%; "
            f"Chuva: {chuva} mm; "
            f"Vento: {wind_speed} km/h ({vento_dir}); "
            f"Atualizado: {last_updated}"
        )

        items.append((titulo, descricao))

    # Sumário: apenas com a primeira cidade
    summary = escape(items[0][1])

    # XML RSS
    xml = f'''<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
<title>Clima das Cidades</title>
<link>https://rss-clima.onrender.com/clima</link>
<description>{summary}</description>
<pubDate>{pub_date}</pubDate>
'''

    for titulo, descricao in items:
        xml += f'''
<item>
<title>{escape(titulo)}</title>
<description>{escape(descricao)}</description>
<pubDate>{pub_date}</pubDate>
</item>
'''

    xml += '''
</channel>
</rss>
'''

    return Response(content=xml, media_type="application/xml")
