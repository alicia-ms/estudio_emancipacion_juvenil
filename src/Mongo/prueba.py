
from pymongo import MongoClient
import re

cliente = MongoClient("mongodb://localhost:27017/")
bd = cliente["emancipacion_euskadi"]
pisos = bd["pisos"]

def convertir_precio(precio):
    if precio is None:
        return None

    texto = str(precio).strip()

    if texto.lower() == "a consultar":
        return None

    texto = re.sub(r"[^\d,.]", "", texto)

    if "," in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")
    else:
        texto = texto.replace(".", "")

    return float(texto)


# Buscar los anuncios de Donos
anuncios = pisos.find({
    "Municipio": "Donos",
    "PrecioOriginal": {"$type": "string"}
})

actualizados = 0

for anuncio in anuncios:
    precio_original = anuncio["PrecioOriginal"]
    precio_nuevo = convertir_precio(precio_original)

    # Actualizar solamente si tenemos un precio válido
    if precio_nuevo is not None:
        pisos.update_one(
            {"_id": anuncio["_id"]},
            {"$set": {"Precio": precio_nuevo}}
        )

        actualizados += 1

print(f"Anuncios actualizados: {actualizados}")

cliente.close()
