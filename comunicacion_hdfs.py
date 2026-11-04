from hdfs import InsecureClient
import json
import glob
import os

client = InsecureClient("http://10.22.87.215:50070", user="iabd-user10")

BASE = "/user/iabd-user10/reto_vivienda"
RAW = f"{BASE}/raw"
PROCESED = f"{BASE}/procesed"

client.makedirs(RAW)
client.makedirs(PROCESED)


carpetas = ["Pisos", "Api"]

for carpeta in carpetas:

    ruta_carpeta = f"datos/raw/{carpeta}"

    for ruta_local in glob.glob(f"{ruta_carpeta}/*.json"):

        nombre = os.path.basename(ruta_local)

        fuente = carpeta

        destino = f"{RAW}/{fuente}/{nombre}"

        client.makedirs(f"{RAW}/{fuente}")
        client.upload(destino, ruta_local, overwrite=True)

        ok = client.status(destino)["length"] == os.path.getsize(ruta_local)

        print(f"Subido {destino} -> {'OK' if ok else 'ERROR: tamaño distinto'}")


def leer_json(ruta_hdfs):
    with client.read(ruta_hdfs, encoding="utf-8") as f:
        return json.load(f)


def guardar_json(ruta_hdfs, datos):
    client.write(ruta_hdfs,
                 data=json.dumps(datos, ensure_ascii=False, indent=2),
                 encoding="utf-8", overwrite=True)


resumen = []

for carpeta, _, ficheros in client.walk(RAW):

    for fichero in ficheros:

        datos = leer_json(f"{carpeta}/{fichero}")

        resumen.append({
            "fichero": fichero,
            "registros": len(datos)
        })

guardar_json(f"{PROCESED}/resumen_raw.json", resumen)


print("\nEstructura en HDFS:")

for carpeta, _, ficheros in client.walk(BASE):

    for fichero in ficheros:

        print(f"  {carpeta}/{fichero}")


print("\nRecuperado de RAW:")

for carpeta, _, ficheros in client.walk(RAW):

    for fichero in ficheros:

        datos = leer_json(f"{carpeta}/{fichero}")

        print(f"  {fichero} -> {len(datos)} registros")


print("\nRecuperado de PROCESED:")

for fila in leer_json(f"{PROCESED}/resumen_raw.json"):

    print(f"  {fila['fichero']} -> {fila['registros']} registros")
