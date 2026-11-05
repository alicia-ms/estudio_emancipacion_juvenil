import os

from bs4 import BeautifulSoup
import json
import re
import unicodedata
import pandas as pd
from playwright.sync_api import sync_playwright

MIN_ANUNCIOS = 3


def limpiar_precio(texto):
    m = re.search(r"([\d.]+)\s*€", texto)
    if not m:
        return None
    return int(m.group(1).replace(".", ""))


def extract_page_info(soup):
    div_anuncios = soup.select("div.ad-preview[id]")

    datos = []

    for anuncio in div_anuncios:

        id_anuncio = anuncio.get("id", "")
        a_titulo = anuncio.select_one("a.ad-preview__title")
        titulo = a_titulo.get_text(strip=True) if a_titulo else ""
        url = (
            "https://www.pisos.com" + a_titulo["href"]
            if a_titulo and a_titulo.get("href")
            else ""
        )

        p_ubicacion = anuncio.select_one("p.ad-preview__subtitle")
        ubicacion = p_ubicacion.get_text(strip=True) if p_ubicacion else ""

        barrio = ubicacion.split("(")[0].strip()
        m_distrito = re.search(r"Distrito ([^.)]+)", ubicacion)
        distrito = m_distrito.group(1).strip() if m_distrito else ""

        span_precio = anuncio.select_one("span.ad-preview__price")
        precio_texto = span_precio.get_text(strip=True) if span_precio else ""
        precio = limpiar_precio(precio_texto) 

        span_tipo = anuncio.select_one("span.ad-preview__type")
        tipo_contrato = span_tipo.get_text(strip=True) if span_tipo else "Larga estancia"

        habitaciones = banos = metros = planta = None

        for p in anuncio.select("p.ad-preview__char"):
            texto = p.get_text(strip=True)

            if "hab" in texto:
                habitaciones = int(re.search(r"\d+", texto).group())
            elif "baño" in texto:
                banos = int(re.search(r"\d+", texto).group())
            elif "m²" in texto:
                metros = int(re.search(r"\d+", texto).group())
            elif "planta" in texto:
                planta = int(re.search(r"\d+", texto).group())

        precio_m2 = round(precio / metros, 2) if precio and metros else None

        datos.append({
            "Id": id_anuncio,
            "Titulo": titulo,
            "Barrio": barrio,
            "Distrito": distrito,
            "Precio": precio_texto,
            "TipoContrato": tipo_contrato,
            "Habitaciones": habitaciones,
            "Banos": banos,
            "Metros": metros,
            "Planta": planta,
            "PrecioM2": precio_m2,
            "Url": url,
        })

    return datos

def scrape_ciudad(pagina, url_base, max_paginas=20):
    resultados = {} 

    for n in range(1, max_paginas + 1):

        url = url_base if n == 1 else f"{url_base}{n}/"
        print(f"Página {n}: {url}")

        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            pagina.wait_for_selector("div.ad-preview", timeout=15000)
        except Exception:
            print("  No hay anuncios, termino.")
            break

        soup = BeautifulSoup(pagina.content(), "html.parser")
        anuncios = extract_page_info(soup)

        nuevos = 0
        for a in anuncios:
            if a["Id"] not in resultados:
                resultados[a["Id"]] = a
                nuevos += 1

        if nuevos == 0 or not soup.select_one("div.pagination__next a"):
            break

        pagina.wait_for_timeout(1500) 

    return list(resultados.values())


def extraer_municipios():
    df = pd.read_csv(
    "datos/raw/mediaPoblacionEmpleo.csv",
    skiprows=2,
    encoding="latin1"
    )
    municipios = df["municipio (> 40.000 habitantes)"].unique()
    return municipios

def cargar_datos(urlZona, nombre):
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()

        viviendas = scrape_ciudad(pagina, urlZona)

        navegador.close()

    if len(viviendas) < MIN_ANUNCIOS:
        print(f"{nombre}: solo {len(viviendas)} anuncios (mínimo {MIN_ANUNCIOS}). No se guarda.")
        return

    os.makedirs("../../datos/raw/Pisos", exist_ok=True)
    with open(f"../../datos/raw/Pisos/{nombre}.json", "w", encoding="utf-8") as f:
        json.dump(viviendas, f, indent=4, ensure_ascii=False)
    print(f"Guardado ../../datos/raw/Pisos/{nombre}.json ({len(viviendas)} anuncios)")
    

if __name__ == "__main__":
    municipios = extraer_municipios()
    for municipio in municipios:
        url_zona = f"https://www.pisos.com/alquiler/{municipio.lower().replace(' ', '-')}/"

        nombre_municipio = unicodedata.normalize("NFKD", municipio)
        nombre_municipio = "".join(
            c for c in nombre_municipio
            if not unicodedata.combining(c)
        )
        nombre_municipio = re.sub(r'[<>:"/\\|?*]', "_", nombre_municipio)
        nombre_municipio = nombre_municipio.replace(" ", "")

        nombre = f"Casas{nombre_municipio}_PisosCom"

        cargar_datos(url_zona, nombre)
