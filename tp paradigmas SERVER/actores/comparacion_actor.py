import pykka

class ComparacionActor(pykka.ThreadingActor):
    def on_receive(self, message):
        if message['command'] == 'comparar':
            resultados = message['resultados']
            nombre_producto_buscado = message.get('nombre_producto_buscado', '').lower()

            mejor_opcion_mercadolibre = None
            mejor_opcion_fravega = None
            mejor_opcion_garbarino = None
            menor_precio_mercadolibre = float('inf')
            menor_precio_fravega = float('inf')
            menor_precio_garbarino = float('inf')

            # Filtrar resultados de MercadoLibre, Fravega y Garbarino
            for i, resultado in enumerate(resultados):
                if isinstance(resultado, list):  # Si es una lista de resultados
                    for item in resultado:
                        titulo = item['titulo'].lower()
                        precio = float(item['precio'].replace('.', '').replace(',', '.'))

                        palabras_clave = nombre_producto_buscado.split()
                        if all(palabra in titulo for palabra in palabras_clave):
                            if i == 0:  # Primer conjunto de resultados es MercadoLibre
                                if precio < menor_precio_mercadolibre:
                                    mejor_opcion_mercadolibre = item
                                    menor_precio_mercadolibre = precio
                            elif i == 1:  # Segundo conjunto es Fravega
                                if precio < menor_precio_fravega:
                                    mejor_opcion_fravega = item
                                    menor_precio_fravega = precio
                            elif i == 2:  # Tercer conjunto es Garbarino
                                if precio < menor_precio_garbarino:
                                    mejor_opcion_garbarino = item
                                    menor_precio_garbarino = precio

            # Si no hay coincidencias exactas, devolvemos el más barato sin filtrar estrictamente por el nombre del producto
            if not mejor_opcion_mercadolibre:
                for item in resultados[0]:
                    precio = float(item['precio'].replace('.', '').replace(',', '.'))
                    if precio < menor_precio_mercadolibre:
                        mejor_opcion_mercadolibre = item
                        menor_precio_mercadolibre = precio

            if not mejor_opcion_fravega:
                for item in resultados[1]:
                    precio = float(item['precio'].replace('.', '').replace(',', '.'))
                    if precio < menor_precio_fravega:
                        mejor_opcion_fravega = item
                        menor_precio_fravega = precio

            if not mejor_opcion_garbarino:
                for item in resultados[2]:
                    precio = float(item['precio'].replace('.', '').replace(',', '.'))
                    if precio < menor_precio_garbarino:
                        mejor_opcion_garbarino = item
                        menor_precio_garbarino = precio

            # Comparar cuál es la mejor opción entre las tres páginas
            mejor_opcion = mejor_opcion_mercadolibre
            menor_precio_general = menor_precio_mercadolibre

            if menor_precio_fravega < menor_precio_general:
                mejor_opcion = mejor_opcion_fravega
                menor_precio_general = menor_precio_fravega

            if menor_precio_garbarino < menor_precio_general:
                mejor_opcion = mejor_opcion_garbarino
                menor_precio_general = menor_precio_garbarino

            return {
                "mejor_opcion_mercadolibre": mejor_opcion_mercadolibre,
                "mejor_opcion_fravega": mejor_opcion_fravega,
                "mejor_opcion_garbarino": mejor_opcion_garbarino,
                "mejor_opcion_general": mejor_opcion
            }
