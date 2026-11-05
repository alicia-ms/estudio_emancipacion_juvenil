import requests, json, os

# Renta personal media de la C.A. de Euskadi por edad, según sexo y tipo de renta (euros). 2001 - 2024
# De aquí sacamos los datos de la media de los ingresos de la gente de 16-34 años de Euskadi.
def rentaMedia ():
    URL = "https://www.eustat.eus/bankupx/api/v1/es/DB/PX_173402_crpf_rpf_rp03.px"

    consulta = {
        "query": [
            {"code": "tipo de renta", "selection": {"filter": "item", "values": ["110"]}},
            {"code": "edad", "selection": {"filter": "item", "values": ["110", "120", "130", "140"]}},
            {"code": "periodo", "selection": {"filter": "item", "values": ["2024"]}},
        ],
        "response": {"format": "json-stat"}, 
    }

    r = requests.post(URL, json=consulta, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)

    print("Código de estado:", r.status_code)

    if r.status_code == 200:
        print("¡Éxito total! Datos obtenidos de la API de Eustat:")
        datos = r.json()
        print(datos)
        directorio_destino = "datos/raw/Api" 
        nombre_archivo = "mediaRenta.json"
        ruta_completa = os.path.join(directorio_destino, nombre_archivo)
        with open(ruta_completa, "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)
        

# Población de 16 y más años activa de la C.A. de Euskadi por municipio (> 40.000 habitantes), CNEDA (3 grupos), edad, sexo y periodo
# De aquí sacamos la población de 16-34 años que está activa(con trabajo o buscándolo) de Euskadi por municipio.
def poblacionActivaPorMunicipio():
    URL = "https://es.eustat.eus/bankupx/api/v1/es/DB/PX_050407_cempa_empa_pa15b.px"

    consulta = {
    "query": [
        {
        "code": "edad",
        "selection": {
            "filter": "item",
            "values": [
            "110",
            "120",
            "130",
            "140"
            ]
        }
        },
        {
        "code": "periodo",
        "selection": {
            "filter": "item",
            "values": [
            "2024",
            "2025"
            ]
        }
        }
    ],
    "response": {
        "format": "json-stat"
    }
    }

    r = requests.post(URL, json=consulta, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)

    print("Código de estado:", r.status_code)

    if r.status_code == 200:
        print("¡Éxito total! Datos obtenidos de la API de Eustat:")
        datos = r.json()
        print(datos)
        directorio_destino = "datos/raw/Api" 
        nombre_archivo = "activosMunicipio.json"
        ruta_completa = os.path.join(directorio_destino, nombre_archivo)
        with open(ruta_completa, "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)


# Población de 16 y más años ocupada asalariada (miles) de la C.A. de Euskadi por tipo de contrato, territorio histórico, sexo, trimestre y periodo
# De aquí sacamos la población de 16-34 años asalariada(que trabaja por cuenta ajena para un empleador) de Euskadi. Para saber
# si esas personas tienen un trabajo estable o no. 
def asalariadosTipoContrato():
    URL = "https://es.eustat.eus/bankupx/api/v1/es/DB/PX_050403_cpra_tab12.px"

    consulta = {
    "query": [
        {
        "code": "trimestre",
        "selection": {
            "filter": "item",
            "values": [
            "10"
            ]
        }
        },
        {
        "code": "periodo",
        "selection": {
            "filter": "item",
            "values": [
            "2024",
            "2025"
            ]
        }
        }
    ],
    "response": {
        "format": "json-stat"
    }
    }

    r = requests.post(URL, json=consulta, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)

    print("Código de estado:", r.status_code)

    if r.status_code == 200:
        print("¡Éxito total! Datos obtenidos de la API de Eustat:")
        datos = r.json()
        print(datos)
        directorio_destino = "datos/raw/Api" 
        nombre_archivo = "asalariadosTipoContrato.json"
        ruta_completa = os.path.join(directorio_destino, nombre_archivo)
        with open(ruta_completa, "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)

# Población de la C.A. de Euskadi por ámbitos territoriales, año de nacimiento, sexo y periodo
# Para saber si las viviendas principales de Euskadi están en propiedad, alquiler u otras fórmulas.
# Los datos de la última fecha son de 2021 porque estos datos se suelen recoger cada 10 años más o menos.
def poblacionEuskadi():
    URL = "https://es.eustat.eus/bankupx/api/v1/es/DB/PX_010154_cepv1_ep10b.px"

    consulta = {
    "query": [
        {
        "code": "año de nacimiento",
        "selection": {
            "filter": "item",
            "values": [
            "5910",
            "5920",
            "5930",
            "5940",
            "5950",
            "5960",
            "5970",
            "5980",
            "5990",
            "6000",
            "6010",
            "6020",
            "6030",
            "6040",
            "6050",
            "6060",
            "6070",
            "6080",
            "6090"
            ]
        }
        },
        {
        "code": "periodo",
        "selection": {
            "filter": "item",
            "values": [
            "20230701",
            "20240101",
            "20250101"
            ]
        }
        }
    ],
    "response": {
        "format": "json-stat"
    }
    }

    r = requests.post(URL, json=consulta, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)

    print("Código de estado:", r.status_code)

    if r.status_code == 200:
        print("¡Éxito total! Datos obtenidos de la API de Eustat:")
        datos = r.json()
        print(datos)
        directorio_destino = "datos/raw/Api" 
        nombre_archivo = "poblacionEuskadi.json"
        ruta_completa = os.path.join(directorio_destino, nombre_archivo)
        with open(ruta_completa, "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)

# Viviendas familiares principales de la C.A. de Euskadi por ámbito territorial, régimen de tenencia y periodo
def viviendasEuskadi():
    URL = "https://es.eustat.eus/bankupx/api/v1/es/DB/PX_010152_cepv1_v09a.px"

    consulta = {
    "query": [
        {
        "code": "periodo",
        "selection": {
            "filter": "item",
            "values": [
            "2016",
            "2021"
            ]
        }
        }
    ],
    "response": {
        "format": "json-stat"
    }
    }

    r = requests.post(URL, json=consulta, headers={"User-Agent": "Mozilla/5.0"}, timeout=120)

    print("Código de estado:", r.status_code)

    if r.status_code == 200:
        print("¡Éxito total! Datos obtenidos de la API de Eustat:")
        datos = r.json()
        print(datos)
        directorio_destino = "../../datos/raw/Api" 
        nombre_archivo = "viviendasEuskadi.json"
        ruta_completa = os.path.join(directorio_destino, nombre_archivo)
        with open(ruta_completa, "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)



# NumeroDeFianzasDepositadas.csv
# Mide el dinamismo y la rotación del mercado de alquiler. Te permite ver en qué periodos 
# hay más movimiento de nuevos contratos de alquiler y qué peso tiene cada territorio (como Bizkaia) 
# frente al total de Euskadi.

# RentaMensualMediaPorMCuadrado.csv
# Es la variable clave para analizar la intensidad de la presión de precios por superficie. 
# Te muestra cómo se ha encarecido el metro cuadrado en Bizkaia a lo largo de los años, 
# permitiendo detectar qué zonas o tamaños de municipios sufren una mayor burbuja de precios.

# RentaMensualMediaEnEurosmes.csv
# Contiene el coste absoluto medio mensual por vivienda (€/mes) que pagan los inquilinos 
# según el trimestre en que se inició el contrato.

rentaMedia()
poblacionActivaPorMunicipio()
asalariadosTipoContrato()
poblacionEuskadi()
viviendasEuskadi()
