import json
import os
import random
import time
import pandas as pd
import re
import unicodedata

from playwright.sync_api import sync_playwright

BASE = "https://www.fotocasa.es"
MIN_ANUNCIOS = 3

SUBTIPOS = {
    "Flat": "Piso",
    "Apartment": "Apartamento",
    "Duplex": "Dúplex",
    "Penthouse": "Ático",
    "Studio": "Estudio",
    "Loft": "Loft",
    "House": "Casa",
}

PLANTAS_FIJAS = {
    1: "Sótano",
    2: "Subsótano",
    3: "Bajos",
    4: "Entresuelo",
    5: "Principal",
    31: "Otros",
    32: "Ático",
}


def get_feature(features, clave):
    for f in features or []:
        if f.get("key") == clave:
            return f.get("value")
    return None


def traducir_planta(codigo):
    if codigo is None:
        return None
    if codigo in PLANTAS_FIJAS:
        return PLANTAS_FIJAS[codigo]
    if 6 <= codigo <= 20:
        return f"{codigo - 5}ª Planta"
    return str(codigo)


def tipo_contrato(item):
    descripcion = (item.get("description") or "").lower()
    if (
        item.get("isTemporaryRental")
        or "IS_TEMPORARY" in (item.get("dynamicFeatures") or [])
        or "contrato de temporada" in descripcion
    ):
        return "Temporada"
    return "Larga estancia"


def parsear_anuncio(item):
    direccion = item.get("address", {})
    features = item.get("features", [])

    precio = item.get("rawPrice")
    metros = get_feature(features, "surface")
    precio_m2 = round(precio / metros, 2) if precio and metros else None

    subtipo = SUBTIPOS.get(item.get("buildingSubtype"), item.get("buildingSubtype"))
    ubicacion = item.get("location") or direccion.get("neighborhood")
    detalle = (item.get("detail") or {}).get("es-ES")

    return {
        "Id": item.get("id"),
        "Titulo": f"{subtipo} en {ubicacion}",
        "Barrio": direccion.get("neighborhood"),
        "Distrito": direccion.get("district"),
        "Precio": precio if isinstance(precio, (int, float)) else None,
        "TipoContrato": tipo_contrato(item),
        "Habitaciones": get_feature(features, "rooms"),
        "Banos": get_feature(features, "bathrooms"),
        "Metros": metros,
        "Planta": traducir_planta(get_feature(features, "floor")),
        "PrecioM2": precio_m2,
        "Url": BASE + detalle if detalle else None,
    }


def leer_estado(pagina):
    pagina.wait_for_selector("script#__initial_props__", state="attached", timeout=30000)
    texto = pagina.locator("script#__initial_props__").text_content()
    return json.loads(texto)["initialSearch"]["result"]


def scrape_ciudad(pagina, url_base):
    viviendas = {}
    numero = 1
    total = None

    while True:
        url = url_base if numero == 1 else f"{url_base}/{numero}"
        print(f"Página {numero}: {url}")
        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)

        try:
            resultado = leer_estado(pagina)
        except Exception as e:
            print(f"  No se pudo leer el JSON ({e}). Paro aquí.")
            break

        total = resultado.get("count", total)
        anuncios = resultado.get("realEstates", [])
        if not anuncios:
            break

        nuevos = 0
        for item in anuncios:
            if item["id"] not in viviendas:
                viviendas[item["id"]] = parsear_anuncio(item)
                nuevos += 1

        print(f"  {nuevos} nuevos ({len(viviendas)}/{total})")

        if nuevos == 0 or (total and len(viviendas) >= total):
            break

        numero += 1
        time.sleep(random.uniform(2, 4))

    return list(viviendas.values())


def cargar_datos(url_zona, nombre):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        contexto = navegador.new_context(
            locale="es-ES",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
            ),
        )
        pagina = contexto.new_page()
        viviendas = scrape_ciudad(pagina, url_zona)
        navegador.close()

    if len(viviendas) < MIN_ANUNCIOS:
        print(f"{nombre}: solo {len(viviendas)} anuncios (mínimo {MIN_ANUNCIOS}). No se guarda.")
        return

    os.makedirs("datos/raw/Pisos", exist_ok=True)
    with open(f"datos/raw/Pisos/{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(viviendas, f, indent=4, ensure_ascii=False)
    print(f"Guardado datos/raw/Pisos/{nombre}.json ({len(viviendas)} anuncios)")


def extraer_municipios():
    df = pd.read_csv(
    "datos/raw/mediaPoblacionEmpleo.csv",
    skiprows=2,
    encoding="latin1"
    )
    municipios = df["municipio (> 40.000 habitantes)"].unique()
    return municipios

if __name__ == "__main__":
    municipios = extraer_municipios()
    for municipio in municipios:
        url_zona = f"https://www.fotocasa.es/es/alquiler/viviendas/{municipio.lower().replace(' ', '-')}/todas-las-zonas/l"

        nombre_municipio = unicodedata.normalize("NFKD", municipio)
        nombre_municipio = "".join(
            c for c in nombre_municipio
            if not unicodedata.combining(c)
        )
        nombre_municipio = re.sub(r'[<>:"/\\|?*]', "_", nombre_municipio)
        nombre_municipio = nombre_municipio.replace(" ", "")

        nombre = f"Casas{nombre_municipio}_Fotocasa"

        cargar_datos(url_zona, nombre)