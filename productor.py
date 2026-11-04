from hdfs import InsecureClient
from confluent_kafka import Producer
import json
import time
import os

client = InsecureClient("http://10.22.87.215:50070", user="iabd-user10")
RAW = "/user/iabd-user10/reto_vivienda/raw"
TOPIC = "anuncios_vivienda"
producer = Producer({"bootstrap.servers": "10.22.87.215:9092"})

def leer_json(ruta_hdfs):
    with client.read(ruta_hdfs, encoding="utf-8") as f:
        return json.load(f)

def entregado(err, msg):
    if err:
        print(f"Error al enviar: {err}")

enviados = 0

for carpeta, _, ficheros in client.walk(RAW):

    for fichero in ficheros:
        ruta_hdfs = f"{carpeta}/{fichero}"
        fuente = os.path.basename(carpeta)
        datos = leer_json(ruta_hdfs)

        if fuente == "Pisos":
            partes = fichero.replace(".json", "").split("_")
            municipio = partes[0].replace("Casas", "")

            for anuncio in datos:
                anuncio["municipio"] = municipio
                anuncio["fuente"] = fuente
                producer.produce(
                    TOPIC,
                    key=municipio,
                    value=json.dumps(anuncio, ensure_ascii=False).encode("utf-8"),
                    callback=entregado,
                )
                producer.poll(0)
                enviados += 1
                time.sleep(0.05)
        elif fuente == "Api":
            for persona in datos:

                mensaje = {
                    "persona": persona,
                    "fuente": fuente
                }

                producer.produce(
                    TOPIC,
                    key="Api",
                    value=json.dumps(mensaje, ensure_ascii=False).encode("utf-8"),
                    callback=entregado,
                )

                producer.poll(0)

                enviados += 1

                time.sleep(0.05)

        print(f"Enviado: {fichero} | Fuente: {fuente}")

producer.flush()

print(f"\nTotal de mensajes enviados: {enviados}")
