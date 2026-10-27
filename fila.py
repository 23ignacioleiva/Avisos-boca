import os, time, json, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT = os.environ["TELEGRAM_CHAT_ID"]
OFICIAL = "https://soysocio.bocajuniors.com.ar/"
OK = ("bocajuniors.com.ar", "queue-it.net")
AR = timezone(timedelta(hours=-3))
API = "https://api.telegram.org/bot" + TOKEN + "/"
offset = 0

def tg(metodo, datos):
    d = urllib.parse.urlencode(datos).encode()
    with urllib.request.urlopen(API + metodo, d, timeout=30) as r:
        return json.load(r)

def avisar(t):
    tg("sendMessage", {"chat_id": CHAT, "text": t})

def parar():
    global offset
    pedido = False
    for u in tg("getUpdates", {"offset": offset, "timeout": 0}).get("result", []):
        offset = u["update_id"] + 1
        m = u.get("message") or {}
        if str(m.get("chat", {}).get("id")) == CHAT and m.get("text", "").strip().lower() == "/parar":
            pedido = True
    return pedido

def estado():
    try:
        req = urllib.request.Request(OFICIAL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            host = urllib.parse.urlparse(r.geturl()).hostname or ""
            texto = r.read().decode("utf-8", "ignore").lower()
        if not host.endswith(OK):
            return "redirige a un sitio no oficial, no lo uso"
        if "queue-it" in host or "queue-it" in texto:
            return "fila virtual ACTIVA"
        return "pagina abierta, sin fila detectada"
    except urllib.error.HTTPError as e:
        return "la pagina respondio error " + str(e.code)
    except Exception:
        return "no se pudo comprobar"

def ahora():
    return datetime.now(AR)

h, m = map(int, os.environ.get("HORA_INICIO", "16:30").split(":"))
inicio = ahora().replace(hour=h, minute=m, second=0, microsecond=0)
fin = inicio + timedelta(hours=min(float(os.environ.get("HORAS", "2")), 5))
parar()
avisar("🤖 Listo. Empiezo a las " + inicio.strftime("%H:%M") + ". Para cortar mandame /parar")

while ahora() < inicio:
    if parar():
        avisar("⏹ Cancelado")
        raise SystemExit
    time.sleep(60)

anterior, proximo = None, 0
while ahora() < fin:
    if parar():
        avisar("⏹ Avisos detenidos")
        break
    e = estado()
    if anterior and e != anterior:
        avisar("🚨 Cambio el estado: " + e + "\n" + OFICIAL)
    if time.time() >= proximo:
        avisar("⏱ " + ahora().strftime("%H:%M") + " · " + e + "\n" + OFICIAL)
        proximo = time.time() + 300
    anterior = e
    time.sleep(60)
else:
    avisar("✅ Termino el horario de avisos")
