    from fastapi import FastAPI
    from fastapi.responses import Response
    import requests
    from xml.sax.saxutils import escape
    from datetime import datetime
    import pytz

    app = FastAPI()

    API_KEY = "SUA_API_AQUI"
    CIDADES = {
        "Itamaraju": "-17.0377,-39.5386",
        "Prado": "-17.3365,-39.2221",
        "Teixeira de Freitas": "-17.5399,-39.7400",
        "Alcobaça": "-17.5197,-39.2033",
        "Itabela": "-16.5732,-39.5594",
        "Itabatã": "-18.9886,-39.5441"
    }

    def graus_para_direcao(graus):
        direcoes = [
            "Norte", "Nordeste", "Leste", "Sudeste",
            "Sul", "Sudoeste", "Oeste", "Noroeste"
        ]
        setores = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]
        for i, lim in enumerate(setores):
            if graus < lim:
                return direcoes[i]
        return "Norte"

    @app.get("/clima/")
    def clima_rss():
        items = []
        for city, coord in CIDADES.items():
            lat, lon = coord.split(',')
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&lang=pt_br&units=metric"
            try:
                data = requests.get(url).json()
                temp = data["main"]["temp"]
                temp_min = data["main"]["temp_min"]
                temp_max = data["main"]["temp_max"]
                feels = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                wind_deg = data["wind"].get("deg", 0)
                wind_dir = graus_para_direcao(wind_deg)
                cond = data["weather"][0]["description"].capitalize()
                rain = data.get("rain", {}).get("1h", 0.0)
                chuva_str = f"{rain:.1f} mm" if rain else "Sem chuva"
                now = datetime.now(pytz.timezone("America/Bahia"))
                last_updated = now.strftime("%d/%m/%Y %H:%M:%S")
                pub_date = now.strftime("%a, %d %b %Y %H:%M:%S %z")

                desc = (
                    f"Temperatura: {temp}°C; Mín: {temp_min}°C; Máx: {temp_max}°C; "
                    f"Sensação: {feels}°C; Umidade: {humidity}%; Vento: {wind_speed} km/h ({wind_dir}); "
                    f"Chuva: {chuva_str}; Condições: {cond}; Atualizado: {last_updated}"
                )

                items.append(f"""
<item>
  <title>{escape(city)}</title>
  <description>{escape(desc)}</description>
  <pubDate>{pub_date}</pubDate>
</item>
""")
            except Exception as e:
                continue

        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Clima - Cidades</title>
  <link>https://rss-clima.onrender.com/clima/</link>
  <description>Previsão atualizada do tempo</description>
  <language>pt-br</language>
  {''.join(items)}
</channel>
</rss>
"""
        return Response(content=rss, media_type="application/xml")
