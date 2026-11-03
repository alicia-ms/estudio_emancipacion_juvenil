import requests, json

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
        with open("mediaRenta.json", "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)
        
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
        with open("activosMunicipio.json", "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)


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
        with open("asalariadosTipoContrato.json", "w", encoding="utf-8") as file_json:
            json.dump(datos, file_json, indent=4, ensure_ascii=False)
    else:
        print("Mensaje del servidor:", r.text)
