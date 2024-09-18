import pykka
import requests
from bs4 import BeautifulSoup

class BusquedaMercadoLibreActor(pykka.ThreadingActor):
    def __init__(self, producto):
        super().__init__()
        self.producto = producto.replace(" ", "-").lower()
        self.base_url = "https://listado.mercadolibre.com.ar/"

    def on_receive(self, message):
        if message.get('command') == 'buscar':
            return self.scrapear_producto()

    def scrapear_producto(self):
        url = f"{self.base_url}{self.producto}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        resultados = []
        productos = soup.find_all('li', class_='ui-search-layout__item')

        for producto in productos:
            titulo = producto.find('h2').text
            precio = producto.find('span', class_='andes-money-amount__fraction').text
            url_producto = producto.find("a")["href"]

            resultados.append({
                "titulo": titulo,
                "precio": precio,
                "url": url_producto
            })

        return resultados