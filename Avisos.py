import os, json, urllib.request, urllib.parse
import xml.etree.ElementTree as ET

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
BUSQUEDA = "Boca entradas socios venta"
URL = ("https://news.google.com/rss/search?q="
       + urllib.parse.quote(BUSQUEDA)
       + "&hl=es-419&gl=AR&ceid=AR:es-419")
ARCHIVO = "vistos.json"

def avisar(texto):
    datos = urllib.parse.urlencode({"chat_id": CHAT, "text": texto}).encode()
    urllib.request.urlopen("https://api.telegram.org/bot" + TOKEN + "/sendMessage", datos)

try:
    vistos = json.load(open(ARCHIVO))
except Exception:
    vistos = None

primera = vistos is None
vistos = set(vistos or [])

pedido = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
items = ET.fromstring(urllib.request.urlopen(pedido).read()).findall("./channel/item")

for it in items:
    titulo = it.findtext("title", "")
    link = it.findtext("link", "")
    if link in vistos:
        continue
    vistos.add(link)
    t = titulo.lower()
    if not primera and "boca" in t and "entrada" in t:
        avisar("🎟 Novedad de entradas Boca:\n" + titulo + "\n" + link)

if primera:
    avisar("✅ Bot de avisos Boca funcionando")

json.dump(list(vistos)[-500:], open(ARCHIVO, "w"))
