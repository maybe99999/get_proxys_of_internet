import requests
from bs4 import BeautifulSoup
import random
import time

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

if __name__ == "__main__":
    lista = obtener_proxies_frescos()
    if lista:
        proxy = obtener_proxy_valido(lista)
        if proxy:
            print(f"Proxy listo para usar: {proxy}")

