from pymongo import MongoClient
from bson import json_util
import os

cliente = MongoClient("mongodb://localhost:27017/")

nombre_bd = "emancipacion_euskadi"

bd = cliente[nombre_bd]

carpeta = os.path.join(os.path.expanduser("~"), "Downloads", nombre_bd)

os.makedirs(carpeta, exist_ok=True)

for nombre_coleccion in bd.list_collection_names():
    coleccion = bd[nombre_coleccion]

    documentos = list(coleccion.find())

    ruta = os.path.join(carpeta, nombre_coleccion + ".json")

    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(json_util.dumps(documentos, indent=4, ensure_ascii=False))

    print(f"Exportada: {nombre_coleccion}")

print("Exportación completada")
cliente.close()
