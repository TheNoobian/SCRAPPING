import pykka
import requests
from bs4 import BeautifulSoup

class BusquedaFravegaActor(pykka.ThreadingActor):
    def __init__(self, producto):
        super().__init__()
        self.producto = producto.replace(" ", "%20").lower()
        self.base_url = "https://www.fravega.com/l/?keyword="

    def on_receive(self, message):
        if message.get('command') == 'buscar':
            return self.scrapear_producto()

    def scrapear_producto(self):
        url = f"{self.base_url}{self.producto}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        resultados = []
        productos = soup.find_all('li')  # Encontrar cada <li> que contenga un producto

        for producto in productos:
            try:
                # Extraer el título (nombre del producto)
                titulo_element = producto.find('span', class_='sc-ca346929-0')
                titulo = titulo_element.text.strip() if titulo_element else "Sin título"

                # Extraer el precio
                # Buscamos dentro del div con data-test-id="product-price"
                precio_element = producto.find('div', {'data-test-id': 'product-price'})
                if precio_element:
                    precio_span = precio_element.find('span', class_='sc-1d9b1d9e-0')
                    precio = precio_span.text.strip().replace("$", "").replace(".", "") if precio_span else "0"
                else:
                    precio = "0"

                # Extraer la URL del producto
                url_producto_element = producto.find('a', href=True)
                url_producto = "https://www.fravega.com" + url_producto_element['href'] if url_producto_element else "Sin URL"

                # Agregar el producto a la lista de resultados
                resultados.append({
                    "titulo": titulo,
                    "precio": precio,
                    "url": url_producto
                })
            except AttributeError:
                continue  # Si no se encuentra algún campo, omitir ese producto

        return resultados
