import requests
from selenium.webdriver.common.by import By
import time

API_KEY = 'c85503ddb340a2ab3e552d82f15c1fa2'

def resolver_captcha(driver,site_key):
    # Enviar la solicitud a 2Captcha para resolver el reCAPTCHA
    captcha_id = enviar_solicitud_resolver_captcha(site_key, driver.current_url)
    # Esperar la solución del captcha
    captcha_solution = obtener_solucion_captcha(captcha_id)
    return captcha_solution

def enviar_solicitud_resolver_captcha(site_key, url):
    """
    Enviar solicitud para resolver el captcha a 2Captcha.
    """
    response = requests.post(f"http://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={site_key}&pageurl={url}")
    if response.ok and response.text.startswith("OK|"):
        captcha_id = response.text.split('|')[1]
        return captcha_id
    else:
        raise Exception(f"Error enviando solicitud a 2Captcha: {response.text}")

def obtener_solucion_captcha(captcha_id):
    """
    Espera la solución del captcha y la devuelve.
    """
    solucion = None
    while solucion is None:
        response = requests.get(f"http://2captcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}")
        if response.text == 'CAPCHA_NOT_READY':
            time.sleep(5)
        elif response.text.startswith('OK|'):
            solucion = response.text.split('|')[1]
        else:
            raise Exception(f"Error obteniendo la solución del captcha: {response.text}")
    return solucion
