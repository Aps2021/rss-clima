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
    ("Mucuri", -18.0965, -39.5569)
]


@app.get("/clima/")
def clima_rss():

    items = []

    for city, lat, lon in CITIES:

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}"
            f"&lon={lon}"
            f"&appid={API_KEY}"
            f"&units=metric"
            f"&lang=pt_br"
        )

        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            continue

        data = r.json()

        now = datetime.now()

        last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
        pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        title = (
            f"{city} – "
            f"{round(data['main']['temp'])}°C – "
            f"{data['weather'][0]['description'].capitalize()}"
        )

        wind_kmh = round(data["wind"]["speed"] * 3.6)

        desc = (
            f"Umidade: {data['main']['humidity']}%<br>"
            f"Vento: {wind_kmh} km/h<br>"
            f"Máxima: {round(data['main']['temp_max'])}°C<br>"
            f"Mínima: {round(data['main']['temp_min'])}°C<br>"
            f"Last Updated: {last_updated}"
        )

        items.append(
            "<item>"
            f"<title>{escape(title)}</title>"
            f"<description><![CDATA[{desc}]]></description>"
            f"<pubDate>{pub_date}</pubDate>"
            "</item>"
        )

    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0">'
        '<channel>'
        '<title>Previsão do Tempo – Extremo Sul da Bahia</title>'
        '<link>https://openweathermap.org/</link>'
        '<description>Clima atualizado para 9 cidades da Bahia</description>'
        + "".join(items)
        + "</channel>"
        + "</rss>"
    )

    return Response(
        content=rss,
        media_type="application/xml"
    )from fastapi import FastAPI, Response
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
    ("Mucuri", -18.0965, -39.5569)
]


@app.get("/clima/")
def clima_rss():

    items = []

    for city, lat, lon in CITIES:

        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}"
            f"&lon={lon}"
            f"&appid={API_KEY}"
            f"&units=metric"
            f"&lang=pt_br"
        )

        r = requests.get(url)

        if r.status_code != 200:
            continue

        data = r.json()

        now = datetime.now()

        last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
        pub_date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

        title = (
            f"{city} – "
            f"{round(data['main']['temp'])}°C – "
            f"{data['weather'][0]['description'].capitalize()}"
        )

        wind_kmh = round(data["wind"]["speed"] * 3.6)

        desc = (
            f"Umidade: {data['main']['humidity']}%<br>"
            f"Vento: {wind_kmh} km/h<br>"
            f"Máxima: {round(data['main']['temp_max'])}°C<br>"
            f"Mínima: {round(data['main']['temp_min'])}°C<br>"
            f"Last Updated: {last_updated}"
        )

        items.append(
            f"""
            <item>
                <title>{escape(title)}</title>
                <description><![CDATA[{desc}]]></description>
                <pubDate>{pub_date}</pubDate>
            </item>
            """
        )

    rss = f"""
    <?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Previsão do Tempo – Extremo Sul da Bahia</title>
            <link>https://openweathermap.org/</link>
            <description>Clima atualizado para 9 cidades da Bahia</description>
            {''.join(items)}
        </channel>
    </rss>
    """

    return Response(
        content=rss,
        media_type="application/xml"
    )
