import socket
import json
from actores.busqueda_actor import BusquedaMercadoLibreActor
from actores.busqueda_actor_fravega import BusquedaFravegaActor
from actores.comparacion_actor import ComparacionActor
from actores.guardado_actor import GuardadoActor
import pykka

# Función para formatear los precios
def formatear_precio(precio):
    try:
        precio = float(precio.replace(",", "").replace(".", ""))
        return f"${precio:,.0f}".replace(",", ".")
    except ValueError:
        return precio

# Función para imprimir cada resultado con formato
def imprimir_resultado(titulo, precio, url, plataforma):
    print(f"\n{'='*50}")
    print(f"Mejor opción en {plataforma}")
    print(f"{'-'*50}")
    print(f"Producto: {titulo}")
    print(f"Precio: {formatear_precio(precio)}")
    print(f"URL: {url}")
    print(f"{'='*50}")

# Función para conectarse al servidor remoto de Garbarino
def buscar_en_garbarino(producto):
    server_address = ('192.168.0.10', 6000)  # IP de la PC remota y el puerto
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(server_address)
        print(f"Conectado con {server_address}")

        # Enviar el producto a buscar
        client_socket.sendall(producto.encode())

        # Recibir la respuesta (resultados de la búsqueda)
        data = client_socket.recv(4096).decode()
        resultados = json.loads(data)

        return resultados

    finally:
        client_socket.close()

def main():
    # Solicitar al usuario el nombre del producto a buscar
    producto = input("Ingrese el nombre del producto que desea buscar: ")

    # Crear actores de búsqueda para MercadoLibre y Fravega
    actor_mercado_libre = BusquedaMercadoLibreActor.start(producto)
    actor_fravega = BusquedaFravegaActor.start(producto)

    # Buscar en la PC remota (Garbarino)
    resultados_garbarino = buscar_en_garbarino(producto)

    # Crear actor de comparación
    actor_comparacion = ComparacionActor.start()

    # Crear actor de guardado
    actor_guardado = GuardadoActor.start()

    # Enviar mensajes a los actores de búsqueda
    print("\nBuscando productos en las plataformas...\n")
    resultados_mercado_libre = actor_mercado_libre.ask({'command': 'buscar'})
    resultados_fravega = actor_fravega.ask({'command': 'buscar'})

    # Comparar los resultados pasando el nombre del producto buscado
    comparacion_resultados = actor_comparacion.ask({
        'command': 'comparar',
        'resultados': [resultados_mercado_libre, resultados_fravega, resultados_garbarino],
        'nombre_producto_buscado': producto
    })

    mejor_opcion_mercadolibre = comparacion_resultados.get("mejor_opcion_mercadolibre")
    mejor_opcion_fravega = comparacion_resultados.get("mejor_opcion_fravega")
    mejor_opcion_garbarino = comparacion_resultados.get("mejor_opcion_garbarino")
    mejor_opcion_general = comparacion_resultados.get("mejor_opcion_general")

    # Mostrar las mejores opciones de cada página
    if mejor_opcion_mercadolibre:
        imprimir_resultado(
            mejor_opcion_mercadolibre['titulo'],
            mejor_opcion_mercadolibre['precio'],
            mejor_opcion_mercadolibre['url'],
            "MercadoLibre"
        )
    else:
        print("\nNo se encontraron opciones en MercadoLibre.")

    if mejor_opcion_fravega:
        imprimir_resultado(
            mejor_opcion_fravega['titulo'],
            mejor_opcion_fravega['precio'],
            mejor_opcion_fravega['url'],
            "Fravega"
        )
    else:
        print("\nNo se encontraron opciones en Fravega.")

    if mejor_opcion_garbarino:
        imprimir_resultado(
            mejor_opcion_garbarino['titulo'],
            mejor_opcion_garbarino['precio'],
            mejor_opcion_garbarino['url'],
            "Garbarino"
        )
    else:
        print("\nNo se encontraron opciones en Garbarino.")

    # Separador para la mejor opción general
    print("\n" + "="*50)
    print("Mejor opción general (la más barata)")
    print("="*50)

    # Mostrar la mejor opción general
    if mejor_opcion_general:
        print(f"Producto: {mejor_opcion_general['titulo']}")
        print(f"Precio: {formatear_precio(mejor_opcion_general['precio'])}")
        print(f"URL: {mejor_opcion_general['url']}")
    else:
        print("No se encontró ninguna opción general.")

    # Guardar la mejor opción
    if mejor_opcion_general:
        actor_guardado.tell({'command': 'guardar', 'resultado': mejor_opcion_general})

    # Detener los actores
    actor_mercado_libre.stop()
    actor_fravega.stop()
    actor_comparacion.stop()
    actor_guardado.stop()

if __name__ == "__main__":
    main()
