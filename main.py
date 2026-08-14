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

# ALTERAÇÃO DETECTORA DE CACHE: Mudamos o endpoint para /previsao/ 
# Isso obriga o Render a compilar o arquivo novo do zero
@app.get("/previsao/")
def clima_rss():
    items = []
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    for city, lat, lon in CITIES:
        # Rota de previsão oficial /forecast que entrega os extremos exatos reais do dia
        url = f"https://openweathermap.org{lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        
        try:
            r = requests.get(url, timeout=6)
            
            if r.status_code == 429:
                time.sleep(1.0)
                r = requests.get(url, timeout=6)
                
            if r.status_code != 200:
                print(f"Erro na API para {city}: Status {r.status_code}")
                continue
                
            data = r.json()
            now = datetime.now()
            last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
            pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

            # Separa os blocos de previsão do dia de hoje
            today_forecasts = [f for f in data.get('list', []) if f.get('dt_txt', '').startswith(today_str)]
            
            if not today_forecasts:
                today_forecasts = data.get('list', [])[:8]

            # Coleta os dados do momento (Primeiro bloco indexado)
            current_block = today_forecasts[0]
            temp_atual = round(current_block['main']['temp'])
            umidade_atual = current_block['main']['humidity']
            vento = round(current_block['wind']['speed'])
            
            desc_clima = "Disponível"
            if current_block.get('weather') and len(current_block['weather']) > 0:
                desc_clima = current_block['weather'][0]['description'].capitalize()

            # EXATIDÃO REAL DA API: Filtra os menores e maiores valores reais registrados nas tabelas
            all_temps = [f['main']['temp'] for f in today_forecasts]
            temp_min = round(min(all_temps))
            temp_max = round(max(all_temps))

            all_humidities = [f['main']['humidity'] for f in today_forecasts]
            umidade_min = min(all_humidities)
            umidade_max = max(all_humidities)

            title = f"{city} – {temp_atual}°C – {desc_clima}"
            desc = (
                f"Temperatura: {temp_atual}°C (Mín: {temp_min}°C / Máx: {temp_max}°C); "
                f"Umidade Atual: {umidade_atual}% (Mín: {umidade_min}% / Máx: {umidade_max}%); "
                f"Vento: {vento} km/h; "
                f"Last Updated: {last_updated}"
            )

            items.append(f"""
<item>
  <title>{escape(title)}</title>
  <description>{escape(desc)}</description>
  <pubDate>{pub_date}</pubDate>
</item>""")

        except Exception as e:
            print(f"Erro real no processamento de {city}: {e}")
            
        time.sleep(0.4)

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Previsão do Tempo – Extremo Sul da Bahia</title>
  <link>https://openweathermap.org</link>
  <description>Clima atualizado para 9 cidades da Bahia</description>
  {''.join(items)}
</channel>
</rss>"""
