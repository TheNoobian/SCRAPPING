import pykka
import requests
from bs4 import BeautifulSoup

class BusquedaGarbarinoActor(pykka.ThreadingActor):
    def __init__(self, producto):
        super().__init__()
        self.producto = producto.replace(" ", "%20").lower()
        self.base_url = "https://www.garbarino.com/shop?search="

    def on_receive(self, message):
        if message.get('command') == 'buscar':
            return self.scrapear_producto()

    def scrapear_producto(self):
        url = f"{self.base_url}{self.producto}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        resultados = []
        productos = soup.find_all('div', class_='d-flex justify-center col-sm-3 col-12')  # Cada tarjeta de producto

        for producto in productos:
            try:
                # Extraer el título (nombre del producto)
                titulo_element = producto.find('div', class_='product-card-design6-vertical__name line-clamp-2 font-2 px-1 header text-center')
                titulo = titulo_element.text.strip() if titulo_element else "Sin título"

                # Extraer el precio
                # Usamos el div con la clase y luego seleccionamos el tercer span dentro
                precio_element = producto.find('div', class_='text-no-wrap product-card-design6-vertical__price price font-6 line-clamp-1 mt-2 px-1 text-center')
                if precio_element:
                    # Seleccionar todos los spans dentro del div y tomar el tercero
                    spans = precio_element.find_all('span')
                    if len(spans) >= 3:
                        precio = spans[2].text.strip().replace("$", "").replace(".", "")
                    else:
                        precio = "0"
                else:
                    precio = "0"

                # Extraer la URL del producto
                url_producto_element = producto.find('a', href=True)
                url_producto = "https://www.garbarino.com" + url_producto_element['href'] if url_producto_element else "Sin URL"

                # Agregar el producto a la lista de resultados
                resultados.append({
                    "titulo": titulo,
                    "precio": precio,
                    "url": url_producto
                })
            except AttributeError:
                continue  # Si no se encuentra algún campo, omitir ese producto

        return resultados
