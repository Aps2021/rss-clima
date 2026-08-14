from fastapi import FastAPI, Response
import requests
from datetime import datetime
from xml.sax.saxutils import escape

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
    now = datetime.now()
    last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
    pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

    for city, lat, lon in CITIES:
        url = f"https://openweathermap.org{lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
        
        try:
            r = requests.get(url, timeout=4)
            
            if r.status_code == 200:
                data = r.json()
                temp = round(data["main"]["temp"])
                
                # Leitura simplificada e direta da descrição do tempo
                condicao = "Disponível"
                if "weather" in data and len(data["weather"]) > 0:
                    condicao = data["weather"][0]["description"].capitalize()
                
                title = f"{city} – {temp}°C – {condicao}"
                desc = f"Umidade: {data['main']['humidity']}% | Vento: {round(data['wind']['speed'])} km/h"
            else:
                # Se a API rejeitar, exibe a cidade com aviso em vez de sumir com ela
                title = f"{city} – Dados Indisponíveis"
                desc = f"Erro na API externa (Status {r.status_code}). Atualizado em: {last_updated}"

        except Exception as e:
            title = f"{city} – Erro de Conexão"
            desc = f"Não foi possível conectar à API de clima: {str(e)}"

        # Garante a inserção do item no XML de qualquer forma
        items.append(f"""
<item>
  <title>{escape(title)}</title>
  <description>{escape(desc)} | Atualizado: {last_updated}</description>
  <pubDate>{pub_date}</pubDate>
</item>""")

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
