import pykka
import pandas as pd

class GuardadoActor(pykka.ThreadingActor):
    def on_receive(self, message):
        if message.get('command') == 'guardar':
            resultado = message.get('resultado')
            self.guardar_resultado(resultado)

    def guardar_resultado(self, resultado):
        df = pd.DataFrame([resultado])
        df.to_csv('resultados_comparacion.csv', index=False)
        print("Resultados guardados en 'resultados_comparacion.csv'.")