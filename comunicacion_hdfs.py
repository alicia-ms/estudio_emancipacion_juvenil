from hdfs import InsecureClient
import json

client = InsecureClient("http://10.22.87.215:50070", user="iabd-user10")

BASE = "/user/iabd-user10/reto_vivienda"
RAW = f"{BASE}/raw"
PROCESED = f"{BASE}/procesed"

client.makedirs(RAW)
client.makedirs(PROCESED)


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
        ruta = f"{carpeta}/{fichero}"
        fila = {"fichero": fichero, "bytes": client.status(ruta)["length"]}
        if fichero.endswith(".json"):
            fila["registros"] = len(leer_json(ruta))
        resumen.append(fila)

guardar_json(f"{PROCESED}/resumen_raw.json", resumen)


print("\nEstructura en HDFS:")
for carpeta, _, ficheros in client.walk(BASE):
    for fichero in ficheros:
        print(f"  {carpeta}/{fichero}")

print("\nRecuperado de RAW:")
for fila in resumen:
    print(f"  {fila['fichero']} -> {fila.get('registros', '-')} registros, {fila['bytes']} bytes")

print("\nRecuperado de PROCESED:")
for fila in leer_json(f"{PROCESED}/resumen_raw.json"):
    print(f"  {fila['fichero']} -> {fila.get('registros', '-')} registros")