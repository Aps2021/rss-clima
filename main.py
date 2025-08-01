from fastapi import FastAPI, Response 
import requests 
from datetime import datetime 

app = FastAPI()

API_KEY = "2e8ac43f3a1290868e551e0cffadf135"  # Substitua pela sua chave do OpenWeatherMap CITIES = [ ("Itamaraju", -17.0401, -39.5389), ("Prado", -17.3366, -39.2226), ("Teixeira de Freitas", -17.5399, -39.7422), ("Alcobaça", -17.5194, -39.2036), ("Itabela", -16.5732, -39.5593), ("Itabatã", -18.0001, -39.8489), ]

DIRECOES = ["Norte", "NNE", "Nordeste", "ENE", "Leste", "ESE", "Sudeste", "SSE", "Sul", "SSO", "Sudoeste", "OSO", "Oeste", "ONO", "Noroeste", "NNO"]

def direcao_vento(deg): idx = int((deg + 11.25) / 22.5) % 16 return DIRECOES[idx]

@app.get("/clima") def clima_rss(): items = [] for city, lat, lon in CITIES: url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br" r = requests.get(url) if r.status_code != 200: continue

data = r.json()
    now = datetime.utcnow()
    last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    temp = round(data['main']['temp'])
    temp_min = round(data['main']['temp_min'])
    temp_max = round(data['main']['temp_max'])
    feels = round(data['main']['feels_like'])
    cond = data['weather'][0]['description'].capitalize()
    humidity = data['main']['humidity']
    wind_speed = round(data['wind']['speed'])
    wind_dir = direcao_vento(data['wind']['deg']) if 'deg' in data['wind'] else ""
    rain = data.get('rain', {}).get('1h', 0)

    title = f"{city} – {temp}°C"
    desc = (
        f"Temperatura mínima: {temp_min}°C; "
        f"Temperatura máxima: {temp_max}°C; "
        f"Sensação térmica: {feels}°C; "
        f"Condições: {cond}; "
        f"Umidade: {humidity}%; "
        f"Chuva: {rain} mm; "
        f"Vento: {wind_speed} km/h; "
        f"Direção do vento: {wind_dir}; "
        f"Atualizado: {last_updated}"
    )

    items.append(f"""
        <item>
            <title>{escape(title)}</title>
            <description>{escape(desc)}</description>
            <pubDate>{pub_date}</pubDate>
        </item>
    """)

rss = f"""
<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>Previsão do Tempo – Extremo Sul da Bahia</title>
        <link>https://openweathermap.org</link>
        <description>Clima atualizado para 6 cidades da Bahia</description>
        {''.join(items)}
    </channel>
</rss>
"""

return Response(content=rss, media_type="application/rss+xml")
