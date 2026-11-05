from confluent_kafka import Consumer
from hdfs import InsecureClient
import json

TOPIC = "datos_vivienda"
RAW = "/user/iabd-user10/reto_vivienda/raw"

client = InsecureClient("http://10.22.87.215:50070", user="iabd-user10")

consumer = Consumer({
    "bootstrap.servers": "10.22.87.215:9092",
    "group.id": "grupo_hdfs",
    "auto.offset.reset": "earliest",   
})
consumer.subscribe([TOPIC])

recibidos = 0
vacios = 0

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            if recibidos > 0:
                vacios += 1
                if vacios >= 10:
                    break
            continue

        if msg.error():
            print("Error:", msg.error())
            continue

        vacios = 0
        mensaje = json.loads(msg.value().decode("utf-8"))

        carpeta = f"{RAW}/{mensaje['fuente']}"
        client.makedirs(carpeta)
        client.write(f"{carpeta}/{mensaje['fichero']}",
                     data=mensaje["contenido"], encoding="utf-8", overwrite=True)

        recibidos += 1
        print(f"Guardado en HDFS: {mensaje['fuente']}/{mensaje['fichero']}")

except KeyboardInterrupt:
    pass
finally:
    consumer.close()

print(f"\nTotal de ficheros guardados en HDFS: {recibidos}")