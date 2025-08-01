from fastapi import FastAPI 
from fastapi.responses import Response 
import requests 
import xml.etree.ElementTree as ET 
from datetime import datetime, timedelta 
import pytz

app = FastAPI()

Conversão das direções do vento

DIRECOES_PT = { "N": "Norte", "NNE": "Norte-Nordeste", "NE": "Nordeste", "ENE": "Leste-Nordeste", "E": "Leste", "ESE": "Leste-Sudeste", "SE": "Sudeste", "SSE": "Sul-Sudeste", "S": "Sul", "SSW": "Sul-Sudoeste", "SW": "Sudoeste", "WSW": "Oeste-Sudoeste", "W": "Oeste", "WNW": "Oeste-Noroeste", "NW": "Noroeste", "NNW": "Norte-Noroeste" }

CIDADES = [ {"nome": "Itamaraju", "lat": -17.0378, "lon": -39.5386}, {"nome": "Prado", "lat": -17.3400, "lon": -39.2200}, {"nome": "Teixeira de Freitas", "lat": -17.5399, "lon": -39.7412}, {"nome": "Alcobaça", "lat": -17.5194, "lon": -39.2033}, {"nome": "Itabela", "lat": -16.5732, "lon": -39.5594}, {"nome": "Itabatã", "lat": -18.0315, "lon": -39.5308} ]

API_KEY = "2e8ac43f3a1290868e551e0cffadf135"

@app.get("/clima.xml") def clima_rss(): tz_brasilia = pytz.timezone("America/Sao_Paulo") agora = datetime.now(tz_brasilia) pub_date = agora.strftime("%a, %d %b %Y %H:%M:%S %z")

rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "Clima Atualizado - Cidades"
ET.SubElement(channel, "link").text = "https://rss-clima.onrender.com/clima.xml"
ET.SubElement(channel, "description").text = f"Atualizado em {pub_date}"
ET.SubElement(channel, "language").text = "pt-br"

for cidade in CIDADES:
    nome = cidade["nome"]
    lat = cidade["lat"]
    lon = cidade["lon"]

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
    resp = requests.get(url).json()

    temp = round(resp['main']['temp'])
    temp_min = round(resp['main']['temp_min'])
    temp_max = round(resp['main']['temp_max'])
    feels_like = round(resp['main']['feels_like'])
    descricao = resp['weather'][0]['description'].capitalize()
    umidade = resp['main']['humidity']
    vento_vel = round(resp['wind']['speed'] * 3.6)
    vento_dir = DIRECOES_PT.get(resp['wind'].get('deg', 0), "")
    deg = resp['wind'].get('deg')

    # Conversão de graus para texto
    def direcao_texto(deg):
        direcoes = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"]
        idx = int((deg + 22.5) % 360 / 45)
        return direcoes[idx]

    if deg is not None:
        vento_dir = direcao_texto(deg)

    chuva = resp.get('rain', {}).get('1h', 0)

    titulo = f"{nome} - {temp}°C"
    descricao_txt = f"Temperatura mínima: {temp_min}°C; Temperatura máxima: {temp_max}°C; Sensação térmica: {feels_like}°C; Condições do tempo: {descricao}; Umidade: {umidade}%; Volume de chuva: {chuva}mm; Vento: {vento_vel} km/h; Direção do vento: {vento_dir}."

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = f"{nome}"
    ET.SubElement(item, "description").text = descricao_txt
    ET.SubElement(item, "pubDate").text = pub_date

xml_str = ET.tostring(rss, encoding='utf-8')
return Response(content=xml_str, media_type="application/xml")
