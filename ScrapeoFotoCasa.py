from bs4 import BeautifulSoup
import json
import csv
import requests

def extract_page_info(html_content):

     div_anuncios = soup.find_all("div", class_= "flex flex-col overflow-hidden rounded-lg shadow-md w-full @md:flex-row @md:flex-wrap")
     datosCasaBilbao = []
     for anuncios in div_anuncios:
        p_anuncios_ubicaciones = anuncios.find("p", class_= "text-body-1 text-on-surface opacity-75 truncate mt-sm mb-md")
        div_anuncios_precio = anuncios.find("div", class_= "flex items-center gap-mdp text-display-3").getText()
        datosCasaBilbao.append({
            "Ubicacion": p_anuncios_ubicaciones,
            "Precio": div_anuncios_precio
            
            })
     return datosCasaBilbao

def new_html(soup):
    boton = soup.find("img", alt="Icono-FORMACIÓN")
    html = boton.find_parent("a")
    return html["href"]


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'} 
urlCasaBilbao = "https://www.fotocasa.es/es/alquiler/viviendas/bilbao/todas-las-zonas/l"
urlCasaDonos = "https://www.fotocasa.es/es/alquiler/viviendas/donostia-san-sebastian/todas-las-zonas/l"
urlCasaVito = "https://www.fotocasa.es/es/alquiler/viviendas/vitoria-gasteiz/todas-las-zonas/l"
viviendasBilbao = []
viviendasDonos = []
viviendasVito = []

response = requests.get(urlCasaBilbao, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

cursos = extract_page_info(soup)

with open("CasasBilbao.json", "w", encoding="utf-8") as f:
    json.dump(cursos, f, indent=4, ensure_ascii=False)

# with open("cursos.csv", "w", newline="", encoding="utf-8") as f:
#     campos = ["Nivel de formación","Formaciones"]
#     escritor = csv.DictWriter(f, fieldnames=campos)
#     escritor.writeheader()
#     escritor.writerows(cursos)
