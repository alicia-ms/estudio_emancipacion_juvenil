from bs4 import BeautifulSoup
import json
import csv
import requests

def extract_page_info(html_content):
     div_por_formacion = soup.find_all("div", class_= "row gx-5 pt-4 pb-4")
     datosFormacion = []
     for f in div_por_formacion:
           datosFormacion.append({
                   "Nivel de formación": f.find("h3", class_= "font-weight-bold text-primary pb-3").getText(),
                   "Formaciones": [
                       {
                           "Formación": formacion["title"]
                       }
                       for formacion in f.find_all("a")[1:]
                   ]
               })
     return datosFormacion

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

new_html = new_html(soup)
url = new_html
response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

cursos = extract_page_info(soup)

with open("cursos.json", "w", encoding="utf-8") as f:
    json.dump(cursos, f, indent=4, ensure_ascii=False)

with open("cursos.csv", "w", newline="", encoding="utf-8") as f:
    campos = ["Nivel de formación","Formaciones"]
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(cursos)
