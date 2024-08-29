import requests
from bs4 import BeautifulSoup
import pyppeteer
import chardet
import asyncio
import json

baseURL = "https://srienlinea.sri.gob.ec/facturacion-internet/consultas/publico/ruc-datos2.jspa?ruc="
baseUrlIdentification = "https://srienlinea.sri.gob.ec/movil-servicios/api/v1.0/deudas/porIdentificacion/"


async def sriIdentification(identification):
    data_info = {}

    # Construir la URL con la identificación
    url = baseUrlIdentification + identification

    try:
        # Realizar la solicitud GET a la página
        response = requests.get(url)
        response.raise_for_status()

        # Obtener la respuesta en formato JSON
        data_info = response.json()

        if 'contribuyente' in data_info and data_info['contribuyente']['tipoIdentificacion'] == 'R':
            data_info['infoRuc'] = await scrapeRUCData(identification)

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        data_info['infoRuc'] = {'error': 'Error al acceder a la página. Ruc no valido'}

    return {'data': data_info}


async def scrapeRUCData(ruc):
    url = baseURL + ruc

    try:
        # Realizar la solicitud GET
        response = requests.get(url)
        response.raise_for_status()

        # Detectar la codificación y decodificar la respuesta en ISO-8859-1
        encoding = chardet.detect(response.content)['encoding']
        html = response.content.decode(encoding or 'ISO-8859-1')

        # Analizar el HTML usando BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Extraer los datos de la tabla
        data = {}
        regex = soup.find_all('th')
        for th in regex:
            td = th.find_next_sibling('td')
            key = normalizeText(th.text.strip())
            value = td.text.strip() if td else ''
            data[key] = replaceHTMLEntities(value)

        # Verificar si se encontraron datos
        if not data:
            raise ValueError("No se encontró la información del contribuyente.")

        # Usar Puppeteer para navegar en la segunda página
        browser = await pyppeteer.launch(headless=True, executablePath="../archivos_necesarios/chromedriver.exe")
        page = await browser.newPage()

        await page.goto(url, {'waitUntil': 'networkidle2', 'timeout': 10000})

        # Hacer clic en el enlace específico
        link_selector = 'a[href="/facturacion-internet/consultas/publico/ruc-establec.jspa"]'
        await page.waitForSelector(link_selector, {'timeout': 10000})
        await page.click(link_selector)

        await page.waitForTimeout(1000)

        # Obtener el contenido de la nueva página
        content = await page.content()

        await browser.close()

        # Procesar la segunda página
        second_soup = BeautifulSoup(content, 'html.parser')
        second_data = extractTableData(second_soup, ".reporte")

        data['establecimiento'] = [second_data]

        return json.dumps(data, indent=2)

    except Exception as e:
        print(f"Error al procesar la solicitud: {e}")
        return json.dumps({'error': 'Error al acceder a la página. Ruc no valido'})


def replaceHTMLEntities(text):
    replacements = {
        "&aacute;": "á", "&eacute;": "é", "&iacute;": "í", "&oacute;": "ó", "&uacute;": "ú",
        "&ntilde;": "ñ", "&Aacute;": "Á", "&Eacute;": "É", "&Iacute;": "Í", "&Oacute;": "Ó",
        "&Uacute;": "Ú", "&Ntilde;": "Ñ"
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def normalizeText(text):
    return text.lower().replace('ñ', 'n')


def extractTableData(soup, selector):
    data = {}
    rows = soup.select(selector + ' tr.impar')
    for index, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) == 4:
            row_data = {
                "numero_establecimiento": cols[0].text.strip(),
                "nombre_comercial": cols[1].text.strip(),
                "ubicacion_establecimiento": cols[2].text.strip(),
                "estado_establecimiento": cols[3].text.strip()
            }
            data[f'establecimiento_{index}'] = row_data
    return data


# Ejecutar la función principal
if __name__ == '__main__':
    identification = '0930808662001'  # Ejemplo
    data = asyncio.run(sriIdentification(identification))
    print(json.dumps(data, indent=2, ensure_ascii=False))  # Imprimir resultados con indentación

