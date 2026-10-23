from bs4 import BeautifulSoup
import json
from playwright.sync_api import sync_playwright


def extract_page_info(soup):

    div_anuncios = soup.find_all(
        "div",
        class_="flex flex-col overflow-hidden rounded-lg shadow-md w-full @md:flex-row @md:flex-wrap"
    )

    datosCasaBilbao = []

    for anuncios in div_anuncios:

        # Extraer ubicación
        p_anuncios_ubicaciones = anuncios.find(
            "p",
            class_="text-body-1 text-on-surface opacity-75 truncate mt-sm mb-md"
        )

        ubicacion = (
            p_anuncios_ubicaciones.get_text(strip=True)
            if p_anuncios_ubicaciones else ""
        )

        # Extraer precio
        div_anuncios_precio = anuncios.find(
            "div",
            class_="flex items-center gap-mdp text-display-3"
        )

        precio = ""

        if div_anuncios_precio:
            precio = div_anuncios_precio.get_text(
                " ",
                strip=True
            )

            # Detectar si sigue siendo el elemento provisional
            if precio == "\u200c":
                precio = ""

        print("Ubicación:", repr(ubicacion))
        print("Precio:", repr(precio))

        datosCasaBilbao.append({
            "Ubicacion": ubicacion,
            "Precio": precio
        })

    return datosCasaBilbao


urlCasaBilbao = (
    "https://www.fotocasa.es/es/alquiler/viviendas/"
    "bilbao/todas-las-zonas/l"
)

urlCasaDonos = (
    "https://www.fotocasa.es/es/alquiler/viviendas/"
    "donostia-san-sebastian/todas-las-zonas/l"
)

urlCasaVito = (
    "https://www.fotocasa.es/es/alquiler/viviendas/"
    "vitoria-gasteiz/todas-las-zonas/l"
)

viviendasBilbao = []
viviendasDonos = []
viviendasVito = []


# Abrir Fotocasa con un navegador que ejecuta JavaScript
with sync_playwright() as p:

    navegador = p.chromium.launch(headless=True)

    pagina = navegador.new_page()

    pagina.goto(
        urlCasaBilbao,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Esperar a que la página tenga tiempo de cargar los precios
    pagina.wait_for_timeout(7000)

    # Obtener el HTML actualizado
    html = pagina.content()

    soup = BeautifulSoup(html, "html.parser")

    print(
        "Elementos skeleton:",
        len(soup.select('[data-panot-component="skeleton"]'))
    )

    cursos = extract_page_info(soup)

    navegador.close()


# Guardar los datos en JSON
with open("CasasBilbao.json", "w", encoding="utf-8") as f:
    json.dump(cursos, f, indent=4, ensure_ascii=False)

print("\nDatos guardados en CasasBilbao.json")
print("Anuncios encontrados:", len(cursos))
