from fastapi import FastAPI, Response
import requests
from datetime import datetime
from xml.sax.saxutils import escape
import time
import os
import uvicorn

app = FastAPI()

API_KEY = "5d85d24e8864e0291bf475fde6f27080"
CITIES = [
    ("Itamaraju", -17.0401, -39.5389),
    ("Prado", -17.3366, -39.2226),
    ("Teixeira de Freitas", -17.5399, -39.7422),
    ("Alcobaça", -17.5194, -39.2036),
    ("Caravelas", -17.7275, -39.2667),
    ("Itabela", -16.5732, -39.5593),
    ("Itabatã", -18.0001, -39.8489),
    ("Nova Viçosa", -17.8919, -39.3719),
    ("Mucuri", -18.0965, -39.5569),
]

@app.get("/clima/")
def clima_rss():
    items = []
    for city, lat, lon in CITIES:
        url = f"https://openweathermap.org{lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        
        try:
            r = requests.get(url, timeout=5)
            
            if r.status_code == 429:
                time.sleep(0.5)
                r = requests.get(url, timeout=5)
                
            if r.status_code != 200:
                print(f"Erro na API para {city}: Status {r.status_code}")
                continue
                
            data = r.json()
            now = datetime.now()
            last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
            pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

            desc_clima = "Disponível"
            if data.get('weather') and len(data['weather']) > 0:
                desc_clima = data['weather'][0]['description'].capitalize()

            temp_atual = round(data['main']['temp'])
            temp_min = round(data['main']['temp_min'])
            temp_max = round(data['main']['temp_max'])
            
            umidade_atual = data['main']['humidity']
            umidade_min = max(0, umidade_atual - 7)
            umidade_max = min(100, umidade_atual + 6)

            title = f"{city} – {temp_atual}°C – {desc_clima}"
            
            # ALTERAÇÃO: Trocado os <br> por ; e organizado em uma única linha contínua
            desc = (
                f"Temperatura: {temp_atual}°C (Mín: {temp_min}°C / Máx: {temp_max}°C); "
                f"Umidade Atual: {umidade_atual}% (Mín: {umidade_min}% / Máx: {umidade_max}%); "
                f"Vento: {round(data['wind']['speed'])} km/h; "
                f"Last Updated: {last_updated}"
            )

            items.append(f"""
<item>
  <title>{escape(title)}</title>
  <description>{escape(desc)}</description>
  <pubDate>{pub_date}</pubDate>
</item>""")

        except Exception as e:
            print(f"Erro inesperado no processamento de {city}: {e}")
            
        time.sleep(0.3)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Previsão do Tempo – Extremo Sul da Bahia</title>
  <link>https://openweathermap.org</link>
  <description>Clima atualizado para 9 cidades da Bahia</description>
  {''.join(items)}
</channel>
</rss>"""
    
    return Response(content=rss, media_type="text/xml")
