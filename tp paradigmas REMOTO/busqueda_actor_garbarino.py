import socket
import requests
from bs4 import BeautifulSoup
import json

class BusquedaGarbarinoActor:
    def __init__(self, producto):
        self.producto = producto.replace(" ", "%20").lower()
        self.base_url = "https://www.garbarino.com/shop?search="

    def scrapear_producto(self):
        url = f"{self.base_url}{self.producto}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        resultados = []
        productos = soup.find_all('div', class_='d-flex justify-center col-sm-3 col-12')

        for producto in productos:
            try:
                titulo_element = producto.find('div', class_='product-card-design6-vertical__name line-clamp-2 font-2 px-1 header text-center')
                titulo = titulo_element.text.strip() if titulo_element else "Sin título"

                precio_element = producto.find('div', class_='text-no-wrap product-card-design6-vertical__price price font-6 line-clamp-1 mt-2 px-1 text-center')
                if precio_element:
                    spans = precio_element.find_all('span')
                    if len(spans) >= 3:
                        precio = spans[2].text.strip().replace("$", "").replace(".", "")
                    else:
                        precio = "0"
                else:
                    precio = "0"

                url_producto_element = producto.find('a', href=True)
                url_producto = "https://www.garbarino.com" + url_producto_element['href'] if url_producto_element else "Sin URL"

                resultados.append({
                    "titulo": titulo,
                    "precio": precio,
                    "url": url_producto
                })
            except AttributeError:
                continue

        return resultados


def start_server():
    # Crear socket TCP/IP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Enlazar socket a la dirección IP y puerto
    server_address = ('0.0.0.0', 6000)  # Acepta conexiones en todas las interfaces de red en el puerto 6000
    server_socket.bind(server_address)

    # Escuchar conexiones entrantes
    server_socket.listen(1)
    print(f"Servidor iniciado en {server_address}")

    while True:
        print('Esperando conexión...')
        connection, client_address = server_socket.accept()

        try:
            print(f"Conexión desde {client_address}")

            # Recibir el producto desde la PC Servidor
            data = connection.recv(1024).decode()
            if data:
                print(f"Producto recibido: {data}")
                # Realizar la búsqueda
                actor = BusquedaGarbarinoActor(data)
                resultados = actor.scrapear_producto()

                # Enviar los resultados de vuelta al cliente
                connection.sendall(json.dumps(resultados).encode())

        finally:
            # Cerrar conexión
            connection.close()


if __name__ == "__main__":
    start_server()