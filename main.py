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
    # Identifica o dia de hoje no formato de texto da API (AAAA-MM-DD)
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for city, lat, lon in CITIES:
        # Chamada para a rota /forecast que contém todas as variações e extremos do dia inteiro
        url = url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        
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

            # Filtra os blocos de previsão de 3h pertencentes ao dia de hoje
            today_forecasts = [f for f in data.get('list', []) if f.get('dt_txt', '').startswith(today_str)]
            
            # Margem de segurança caso acesse à noite e restem poucos blocos de hoje
            if not today_forecasts:
                today_forecasts = data.get('list', [])[:8]

            # O primeiro bloco representa as condições do período atual
            current_block = today_forecasts[0]
            temp_atual = round(current_block['main']['temp'])
            umidade_atual = current_block['main']['humidity']
            
            desc_clima = "Disponível"
            if current_block.get('weather') and len(current_block['weather']) > 0:
                desc_clima = current_block['weather'][0]['description'].capitalize()

            # EXTRAÇÃO REAL DA API: Descobre matematicamente a mínima e máxima reais do dia nos blocos
            all_temps = [f['main']['temp'] for f in today_forecasts]
            temp_min = round(min(all_temps))
            temp_max = round(max(all_temps))

            # EXTRAÇÃO REAL DA API: Descobre matematicamente a umidade mínima e máxima reais do dia nos blocos
            all_humidities = [f['main']['humidity'] for f in today_forecasts]
            umidade_min = min(all_humidities)
            umidade_max = max(all_humidities)

            title = f"{city} – {temp_atual}°C – {desc_clima}"
            desc = (
                f"Temperatura: {temp_atual}°C (Mín: {temp_min}°C / Máx: {temp_max}°C); "
                f"Umidade Atual: {umidade_atual}% (Mín: {umidade_min}% / Máx: {umidade_max}%); "
                f"Vento: {round(current_block['wind']['speed'])} km/h; "
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
            
        time.sleep(0.4)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Previsão do Tempo – Extremo Sul da Bahia</title>
  <link>https://openweathermap.org/</link>
  <description>Clima atualizado para 9 cidades da Bahia</description>
  {''.join(items)}
</channel>
</rss>"""
    
    return Response(content=rss, media_type="text/xml")
