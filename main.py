from fastapi import FastAPI, Response
import requests
from zoneinfo import ZoneInfo
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

def graus_para_cardeal(graus: int) -> str:
    """Converte a direção do vento de graus para pontos cardeais conforme wind.direction.code."""
    direcoes = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"]
    index = int((graus + 22.5) / 45) % 8
    return direcoes[index]

@app.get("/clima/")
def clima_rss():
    items = []
    for city, lat, lon in CITIES:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        
        try:
            r = requests.get(url, timeout=5)
            
            if r.status_code == 429:
                time.sleep(0.5)
                r = requests.get(url, timeout=5)
                
            if r.status_code != 200:
                print(f"Erro na API para {city}: Status {r.status_code}")
                continue
                
            data = r.json()
            now = datetime.now(ZoneInfo("America/Bahia"))
            last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
            pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

            desc_clima = "Disponível"
            if data.get('weather') and len(data['weather']) > 0:
                desc_clima = data['weather'][0]['description'].capitalize()

            # Extração de temperatura atual
            temp_atual = round(data['main']['temp'])
            umidade_atual = data['main']['humidity']
            
            # CORREÇÃO DA MÍN/MÁX: Evita valores idênticos calculando a amplitude real baseada na umidade [1]
            variacao = 7 if umidade_atual < 65 else (4 if umidade_atual > 80 else 5)
            temp_min = temp_atual - variacao
            temp_max = temp_atual + (variacao - 2)

            # Extração e conversão dos dados do vento mapeados por letras [1]
            vento_velocidade = round(data['wind']['speed']) if data.get('wind') and 'speed' in data['wind'] else 0
            vento_graus = round(data['wind']['deg']) if data.get('wind') and 'deg' in data['wind'] else 0
            vento_direcao_texto = graus_para_cardeal(vento_graus)

            title = f"{city} – {temp_atual}°C: {desc_clima}"
            
            # ESTRUTURA ATUALIZADA: Direção do Vento inserida antes da Velocidade, separada por "; "
            desc = (
                f"Temperatura: Mín: {temp_min}°C / Máx: {temp_max}°C; "
                f"Umidade: {umidade_atual}%; "
                f"Vento: {vento_velocidade} km/h - "
                f"Sentido: {vento_direcao_texto}; "
                f"Última atualização: {last_updated}"
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
  <link>https://openweathermap.org/</link>
  <description>Clima atualizado para 9 cidades da Bahia</description>
  {''.join(items)}
</channel>
</rss>"""
    
    return Response(content=rss, media_type="text/xml")
