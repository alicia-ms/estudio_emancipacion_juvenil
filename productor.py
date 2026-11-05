from confluent_kafka import Producer
import json
import glob
import os
import time

TOPIC = "datos_vivienda"
producer = Producer({"bootstrap.servers": "10.22.87.215:9092"})


def entregado(err, msg):
    if err:
        print(f"Error al enviar: {err}")


enviados = 0
for ruta_local in sorted(glob.glob("datos/raw/*/*.*")):
    fuente = os.path.basename(os.path.dirname(ruta_local))   # nombre de la carpeta
    fichero = os.path.basename(ruta_local)

    with open(ruta_local, encoding="utf-8") as f:
        contenido = f.read()

    mensaje = {"fuente": fuente, "fichero": fichero, "contenido": contenido}

    producer.produce(
        TOPIC,
        key=fuente,
        value=json.dumps(mensaje, ensure_ascii=False).encode("utf-8"),
        callback=entregado,
    )
    producer.poll(0)
    enviados += 1
    print(f"Enviado: {fuente}/{fichero}")
    time.sleep(0.05)

producer.flush(10)
print(f"\nTotal de ficheros enviados: {enviados}")