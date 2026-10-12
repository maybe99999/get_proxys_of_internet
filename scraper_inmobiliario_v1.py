import requests
from bs4 import BeautifulSoup
import time
import random
import csv

def obtener_proxies_frescos():
    """Extrae proxies gratuitos de free-proxy-list.net"""
    print("Obteniendo proxies frescos...")
    url = "https://free-proxy-list.net/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    proxies_encontrados = []
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        filas = soup.find('tbody').find_all('tr')
        
        for fila in filas:
            datos = fila.find_all('td')
            if len(datos) > 1 and datos[6].text == "yes":
                proxies_encontrados.append(f"{datos[0].text}:{datos[1].text}")
        print(f"Se encontraron {len(proxies_encontrados)} proxies HTTPS.")
        return proxies_encontrados
    except Exception as e:
        print("Error obteniendo proxies:", e)
        return []

def obtener_proxy_valido(proxies_lista):
    """Selecciona un proxy al azar y lo prueba rápido."""
    random.shuffle(proxies_lista) 
    print("Validando proxies...")
    for proxy_str in proxies_lista:
        proxies = {
            "http": f"http://{proxy_str}",
            "https": f"http://{proxy_str}"
        }
        try:
            r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
            if r.status_code == 200:
                print(f"Proxy válido encontrado: {proxy_str}")
                return proxies
        except:
            continue
            
    print("Ningún proxy válido encontrado.")
    return None

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "es-AR,es;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def obtener_html(url, proxy):
    try:
        time.sleep(random.uniform(1.5, 3.5)) 
        response = requests.get(url, headers=HEADERS, proxies=proxy, timeout=10)
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
        print(f"Error {response.status_code} en {url}")
    except Exception as e:
        print(f"Error de conexión: {e}")
    return None

def extraer_detalles(url, proxy):
    soup = obtener_html(url, proxy)
    if not soup: return None

    datos = {
        "Precio": "", "Tipo": "", "Ubicacion": "", "Localidad": "", "Provincia": "",
        "Contacto": "Requiere clic/API", "Mtrs2": "", "Ambientes": "", "Baños": "", 
        "Dormitorios": "", "Cochera": "0", "Antiguedad": "", "URL": url
    }

    precio_tag = soup.find('span', class_='andes-money-amount__fraction')
    if precio_tag: datos["Precio"] = precio_tag.text.strip()

    breadcrumbs = soup.find_all('a', class_='andes-breadcrumb__link')
    if len(breadcrumbs) >= 5:
        datos["Tipo"] = breadcrumbs[1].text.strip()
        datos["Provincia"] = breadcrumbs[3].text.strip()
        datos["Localidad"] = breadcrumbs[4].text.strip()
    
    ubicacion_tag = soup.find('p', class_='ui-pdp-color--BLACK ui-pdp-size--SMALL ui-pdp-family--REGULAR ui-pdp-media__title')
    if ubicacion_tag: datos["Ubicacion"] = ubicacion_tag.text.strip()

    tablas = soup.find_all('table', class_='andes-table')
    for tabla in tablas:
        filas = tabla.find_all('tr')
        for fila in filas:
            th = fila.find('th')
            td = fila.find('td')
            if th and td:
                clave = th.text.strip().lower()
                valor = td.text.strip()
                if "superficie total" in clave or "superficie cubierta" in clave: datos["Mtrs2"] = valor
                elif "ambiente" in clave: datos["Ambientes"] = valor
                elif "baño" in clave: datos["Baños"] = valor
                elif "dormitorio" in clave: datos["Dormitorios"] = valor
                elif "cochera" in clave: datos["Cochera"] = valor
                elif "antigüedad" in clave: datos["Antiguedad"] = valor
    
    return datos

def scraper_inmuebles(url_busqueda, archivo_salida='leads_inmobiliarios.csv'):
    lista_proxies = obtener_proxies_frescos()
    proxy = obtener_proxy_valido(lista_proxies) if lista_proxies else None
    
    if not proxy:
        print("Continuando sin proxy (alto riesgo de baneo)")
    
    print(f"Obteniendo listado desde: {url_busqueda}")
    soup = obtener_html(url_busqueda, proxy)
    if not soup: return

    items = soup.find_all('a', class_='ui-search-link')
    links = list(set([item['href'].split('#')[0] for item in items if 'mercadolibre.com.ar/jm/item' not in item['href']]))
    
    print(f"Propiedades encontradas: {len(links)}. Procesando...")

    columnas = ["Precio", "Tipo", "Ubicacion", "Localidad", "Provincia", "Contacto", 
                "Mtrs2", "Ambientes", "Baños", "Dormitorios", "Cochera", "Antiguedad", "URL"]

    with open(archivo_salida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=columnas)
        writer.writeheader()

        for link in links:
            print(f"Extrayendo: {link}")
            detalles = extraer_detalles(link, proxy)
            if detalles:
                writer.writerow(detalles)

if __name__ == "__main__":
    url_ml = "https://inmuebles.mercadolibre.com.ar/venta/dueno-directo"
    scraper_inmuebles(url_ml)

