import json
import os
import random
import re
import time
import unicodedata

import pandas as pd
from playwright.sync_api import sync_playwright

BASE = "https://www.habitaclia.com"
MIN_ANUNCIOS = 3

SUBTIPOS = {
    "planta-intermedia": "Piso",
    "atico": "Ático",
    "apartamento": "Apartamento",
    "duplex": "Dúplex",
    "estudio": "Estudio",
    "loft": "Loft",
    "casa": "Casa",
    "chalet": "Chalet",
}

JS_EXTRAER = """
() => [...document.querySelectorAll('ul[aria-label="Resultados de búsqueda"] article')].map(a => {
    const link = a.querySelector('h3 a');
    const feats = {};
    a.querySelectorAll('[aria-label="Características del anuncio"] > span').forEach(s => {
        const icono = s.querySelector('svg')?.getAttribute('data-title');
        feats[icono] = s.querySelector('span')?.textContent.trim() ?? null;
    });
    return {
        titulo: link?.getAttribute('title') ?? null,
        href: link?.getAttribute('href') ?? null,
        precio: a.querySelector('span.text-display-4')?.textContent.trim() ?? null,
        ubicacion: a.querySelector('p span.truncate')?.textContent.trim() ?? null,
        feats: feats,
    };
})
"""


def solo_numero(texto):
    if not texto:
        return None
    digitos = re.sub(r"[^\d]", "", texto)
    return int(digitos) if digitos else None


def traducir_planta(texto):
    if not texto:
        return None
    if "bajo" in texto.lower():
        return "Bajos"
    m = re.match(r"(\d+)º", texto)
    if m:
        return f"{m.group(1)}ª Planta"
    return texto


def parsear_anuncio(item, municipio):
    href = item.get("href") or ""
    partes = [p for p in href.split("/") if p]
    tipo_slug = partes[1] if len(partes) > 1 else None
    distrito_slug = partes[3] if len(partes) > 3 else None

    m_id = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", href)
    id_anuncio = m_id.group(0) if m_id else None

    ubicacion = item.get("ubicacion") or ""
    primera = ubicacion.split(",")[0].strip()
    if primera and primera.lower() != municipio.lower():
        distrito = primera
    elif distrito_slug:
        distrito = distrito_slug.replace("-", " ").title()
    else:
        distrito = None

    titulo_raw = item.get("titulo") or ""
    calle = titulo_raw.split(" en alquiler en ")[-1] if " en alquiler en " in titulo_raw else distrito

    subtipo = SUBTIPOS.get(tipo_slug, (tipo_slug or "Vivienda").replace("-", " ").title())

    feats = item.get("feats") or {}
    precio = solo_numero(item.get("precio"))
    metros = solo_numero(feats.get("dimensions_outline"))
    precio_m2 = round(precio / metros, 2) if precio and metros else None

    return {
        "Id": id_anuncio,
        "Titulo": f"{subtipo} en {calle}",
        "Barrio": None, 
        "Distrito": distrito,
        "Precio": precio,
        "TipoContrato": None, 
        "Habitaciones": solo_numero(feats.get("double_bed_outline")),
        "Banos": solo_numero(feats.get("shower_outline")),
        "Metros": metros,
        "Planta": traducir_planta(feats.get("floor_outline")),
        "PrecioM2": precio_m2,
        "Url": BASE + href if href else None,
    }


def leer_total(pagina):
    try:
        texto = pagina.locator('button[aria-current="page"]').first.text_content(timeout=3000)
        return solo_numero(re.search(r"\((.*?)\)", texto).group(1))
    except Exception:
        return None


def scrape_ciudad(pagina, url_base, municipio):
    viviendas = {}
    numero = 1
    total = None

    while True:
        url = url_base if numero == 1 else f"{url_base}/{numero}"
        print(f"Página {numero}: {url}")
        pagina.goto(url, wait_until="domcontentloaded", timeout=60000)

        try:
            pagina.wait_for_selector(
                'ul[aria-label="Resultados de búsqueda"] article', timeout=20000
            )
        except Exception:
            print("  No hay tarjetas en esta página. Paro aquí.")
            break

        if total is None:
            total = leer_total(pagina)

        anuncios = pagina.evaluate(JS_EXTRAER)
        if not anuncios:
            break

        nuevos = 0
        for item in anuncios:
            parsed = parsear_anuncio(item, municipio)
            if parsed["Id"] and parsed["Id"] not in viviendas:
                viviendas[parsed["Id"]] = parsed
                nuevos += 1

        print(f"  {nuevos} nuevos ({len(viviendas)}/{total})")

        if nuevos == 0 or (total and len(viviendas) >= total):
            break

        numero += 1
        time.sleep(random.uniform(2, 4))

    return list(viviendas.values())


def cargar_datos(url_zona, nombre, municipio):
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
        viviendas = scrape_ciudad(pagina, url_zona, municipio)
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
        encoding="latin1",
    )
    return df["municipio (> 40.000 habitantes)"].unique()

if __name__ == "__main__":
    municipios = extraer_municipios()
    for municipio in municipios:
        
        if "Donostia" in municipio:
            municipio = "Donostia San Sebastian"
            url_zona = f"{BASE}/alquiler/viviendas/{municipio.lower().replace(' ', '-')}/s"
        else:
            url_zona = f"{BASE}/alquiler/viviendas/{municipio.lower().replace(' ', '-')}/s"
        
        nombre_municipio = unicodedata.normalize("NFKD", municipio)
        nombre_municipio = "".join(c for c in nombre_municipio if not unicodedata.combining(c))
        nombre_municipio = re.sub(r'[<>:"/\\|?*]', "_", nombre_municipio).replace(" ", "")

        cargar_datos(url_zona, f"Casas{nombre_municipio}_Habitaclia", municipio)