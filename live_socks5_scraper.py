import requests
from bs4 import BeautifulSoup
import random

def obtener_proxies_socks5():
    """Extrae proxies gratuitos SOCKS5 de freeproxylists.net"""
    print("Obteniendo proxies SOCKS5...")
    url = "https://freeproxylists.net/es/?c=&pt=&pr=SOCKS5&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    proxies_encontrados = []
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        filas = soup.find_all('tr', class_=['DataRow', 'Odd'])
        
        for fila in filas:
            datos = fila.find_all('td')
            if len(datos) > 1:
                # El script de freeproxylists.net oculta la IP en javascript, pero BeautifulSoup
                # puede leer el texto si el sitio no lo ofusca bien.
                # Como alternativa, scrapearemos de proxyscrape API que es más directa y confiable.
                pass
    except Exception:
        pass

    # Usaremos Proxyscrape API para SOCKS5 crudos, es mucho más rápido y estable para scripts
    url_api = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all&ssl=all&anonymity=all"
    try:
        r = requests.get(url_api, timeout=10)
        if r.status_code == 200:
            lista_cruda = r.text.strip().split('\r\n')
            proxies_encontrados = [p for p in lista_cruda if ':' in p]
            print(f"Se obtuvieron {len(proxies_encontrados)} proxies SOCKS5 de la API.")
            return proxies_encontrados
    except Exception as e:
        print("Error obteniendo proxies SOCKS5 por API:", e)
        return []

def obtener_proxy_valido_socks5(proxies_lista):
    """Valida los SOCKS5 probando la conexión a httpbin."""
    random.shuffle(proxies_lista)
    print("Validando proxies SOCKS5...")
    for proxy_str in proxies_lista:
        proxies = {
            "http": f"socks5://{proxy_str}",
            "https": f"socks5://{proxy_str}"
        }
        try:
            # Timeout corto de 5s para descartar lentos
            r = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=5)
            if r.status_code == 200:
                print(f"SOCKS5 válido encontrado: {proxy_str}")
                return proxy_str
        except:
            continue
            
    print("Ningún proxy SOCKS5 válido encontrado.")
    return None

if __name__ == "__main__":
    lista = obtener_proxies_socks5()
    if lista:
        proxy = obtener_proxy_valido_socks5(lista)
        if proxy:
            print(f"Proxy SOCKS5 listo: {proxy}")

