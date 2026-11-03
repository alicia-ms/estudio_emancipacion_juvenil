from hdfs import InsecureClient
from confluent_kafka import Producer
import json
import time

client = InsecureClient("http://10.22.87.215:50070", user="iabd-user10")
RAW = "/user/iabd-user10/reto_vivienda/raw"


TOPIC = "anuncios_vivienda"
producer = Producer({"bootstrap.servers": "IP_DE_KAFKA:9092"}) # atencion: sustituir IP_DE_KAFKA por la IP del contenedor de Kafka


def leer_json(ruta_hdfs):
    with client.read(ruta_hdfs, encoding="utf-8") as f:
        return json.load(f)


def entregado(err, msg):
    """Kafka llama a esta función por cada mensaje: confirma si llegó o falló."""
    if err:
        print(f"Error al enviar: {err}")


enviados = 0
for carpeta, _, ficheros in client.walk(RAW):
    for fichero in ficheros:
        partes = fichero.replace(".json", "").split("_")
        municipio = partes[0].replace("Casas", "")
        fuente = partes[-1]

        for anuncio in leer_json(f"{carpeta}/{fichero}"):
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

        print(f"Enviado: {fichero}")

producer.flush()
print(f"\nTotal de anuncios enviados: {enviados}")