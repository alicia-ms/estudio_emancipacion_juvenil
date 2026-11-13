
import json
import re
import hashlib
import os
import unicodedata
from pathlib import Path
from pymongo import MongoClient, UpdateOne

CARPETA_DATOS = (
    Path(__file__).resolve().parent
    / "../../datos/raw/Pisos"
).resolve()

MONGO_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017/"
)

DB_NAME = "emancipacion_euskadi"
COLECCION = "pisos"

def limpiar_texto(valor):
    if valor is None:
        return None
    return re.sub(r"\s+", " ", str(valor)).strip() or None


def numero(valor):
    if valor is None or isinstance(valor, bool):
        return None

    if isinstance(valor, (int, float)):
        return valor

    valor = str(valor).strip()

    if not valor or valor.lower() in ("null", "none", "nan", "a consultar"):
        return None

    valor = re.sub(r"[^0-9,.\-]", "", valor)

    if "," in valor and "." in valor:
        if valor.rfind(",") > valor.rfind("."):
            valor = valor.replace(".", "").replace(",", ".")
        else:
            valor = valor.replace(",", "")

    elif "," in valor:
        valor = valor.replace(",", ".")

    elif "." in valor:
        partes = valor.split(".")

        if len(partes) == 2 and len(partes[1]) == 3:
            valor = valor.replace(".", "")

    try:
        n = float(valor)
        return int(n) if n.is_integer() else n
    except ValueError:
        return None


def normalizar(valor):
    valor = str(valor or "").lower()
    valor = unicodedata.normalize("NFKD", valor)
    valor = "".join(
        c for c in valor if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]", " ", valor)).strip()

def obtener_municipio(nombre):
    resultado = re.match(r"^Casas(.+?)_.+$", nombre)
    if not resultado:
        raise ValueError(f"Nombre no válido: {nombre}")
    return resultado.group(1).strip()

def limpiar_piso(piso, municipio, fuente):

    limpio = {
        "Id": limpiar_texto(piso.get("Id")),
        "Titulo": limpiar_texto(piso.get("Titulo")),
        "Barrio": limpiar_texto(piso.get("Barrio")),
        "Distrito": limpiar_texto(piso.get("Distrito")),
        "TipoContrato": limpiar_texto(piso.get("TipoContrato")),
        "Url": limpiar_texto(piso.get("Url")),
        "Habitaciones": numero(piso.get("Habitaciones")),
        "Banos": numero(piso.get("Banos")),
        "Metros": numero(piso.get("Metros")),
        "Planta": numero(piso.get("Planta")),
        "Precio": numero(piso.get("Precio")),
        "PrecioM2": numero(piso.get("PrecioM2")),
        "Municipio": municipio,
        "Fuentes": [fuente]
    }
    limpio["PrecioOriginal"] = limpiar_texto(piso.get("Precio"))

    if limpio["Precio"] is not None and limpio["Metros"]:
        if limpio["Metros"] > 0:
            limpio["PrecioM2"] = round(
                limpio["Precio"] / limpio["Metros"], 2
            )

    campos = [
        normalizar(limpio["Municipio"]),
        normalizar(limpio["Titulo"]),
        normalizar(limpio["Barrio"]),
        str(limpio["Habitaciones"] or ""),
        str(limpio["Banos"] or ""),
        str(limpio["Metros"] or "")
    ]

    limpio["Hash"] = hashlib.sha256(
        "|".join(campos).encode("utf-8")
    ).hexdigest()
    return limpio

def cargar_archivos():

    pisos = {}
    archivos = sorted(CARPETA_DATOS.glob("*.json"))

    print(f"Carpeta: {CARPETA_DATOS}")
    print(f"Archivos encontrados: {len(archivos)}")

    if not archivos:
        raise FileNotFoundError(
            f"No hay archivos JSON en {CARPETA_DATOS}"
        )

    for archivo in archivos:
        municipio = obtener_municipio(archivo.stem)
        fuente = archivo.stem.rsplit("_", 1)[1]

        with open(archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)

        for piso_original in datos:
            piso = limpiar_piso(piso_original, municipio, fuente)
            hash_piso = piso["Hash"]

            if hash_piso not in pisos:
                pisos[hash_piso] = piso
            else:
                for fuente in piso["Fuentes"]:
                    if fuente not in pisos[hash_piso]["Fuentes"]:
                        pisos[hash_piso]["Fuentes"].append(fuente)

    return list(pisos.values())

def guardar_mongodb(pisos):

    if not pisos:
        return

    with MongoClient(MONGO_URI) as cliente:
        coleccion = cliente[DB_NAME][COLECCION]
        coleccion.create_index("Hash", unique=True)

        operaciones = []

        for piso in pisos:
            datos = piso.copy()
            fuentes = datos.pop("Fuentes")

            operaciones.append(
                UpdateOne(
                    {"Hash": piso["Hash"]},
                    {
                        "$set": datos,
                        "$addToSet": {
                            "Fuentes": {"$each": fuentes}
                        }
                    },
                    upsert=True
                )
            )

        resultado = coleccion.bulk_write(
            operaciones,
            ordered=False
        )

        print("Pisos insertados:", resultado.upserted_count)
        print("Pisos modificados:", resultado.modified_count)
        print("Pisos coincidentes:", resultado.matched_count)

def main():
    pisos = cargar_archivos()
    guardar_mongodb(pisos)

if __name__ == "__main__":
    main()