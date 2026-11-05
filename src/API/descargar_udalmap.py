
from pathlib import Path
from io import BytesIO

import pandas as pd
import requests

CARPETA = Path("datos_udalmap")
CARPETA.mkdir(exist_ok=True)

INDICADORES = {
    "renta_personal_disponible": (
        "https://opendata.euskadi.eus/contenidos/"
        "estadistica/udalmap_indicador_61/es_def/"
        "adjuntos/indicator.csv"
    ),
    "renta_derivada_trabajo": (
        "https://opendata.euskadi.eus/contenidos/"
        "estadistica/udalmap_indicador_64/es_def/"
        "adjuntos/indicator.csv"
    ),
    "renta_personal_total_indice": (
        "https://opendata.euskadi.eus/contenidos/"
        "estadistica/udalmap_indicador_166/es_def/"
        "adjuntos/indicator.csv"
    ),
}

def descargar_csv(nombre, url):
    print(f"\nDescargando: {nombre}")

    respuesta = requests.get(url, timeout=60)
    respuesta.raise_for_status()

    contenido = BytesIO(respuesta.content)

    # Detecta automáticamente separador y codificación habitual.
    try:
        df = pd.read_csv(
            contenido,
            sep=None,
            engine="python",
            encoding="utf-8-sig"
        )
    except UnicodeDecodeError:
        contenido.seek(0)
        df = pd.read_csv(
            contenido,
            sep=None,
            engine="python",
            encoding="latin-1"
        )

    destino = CARPETA / f"{nombre}.csv"
    df.to_csv(destino, index=False, encoding="utf-8-sig")

    print("Columnas:", df.columns.tolist())
    print("Filas:", len(df))
    print(df.head(5).to_string(index=False))
    print("Guardado en:", destino.resolve())

    return df


def main():
    tablas = {}

    for nombre, url in INDICADORES.items():
        try:
            tablas[nombre] = descargar_csv(nombre, url)
        except Exception as error:
            print(f"Error descargando {nombre}: {error}")

    print("\nDescarga terminada.")
    print("Archivos guardados en:", CARPETA.resolve())

    # No combinamos automáticamente las tablas:
    # pueden tener escalas, años y unidades diferentes.
    # Primero hay que inspeccionar sus columnas.


if __name__ == "__main__":
    main()
