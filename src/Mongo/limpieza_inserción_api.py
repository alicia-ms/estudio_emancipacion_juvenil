import json
import os
import itertools
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["emancipacion_euskadi"]  

def limpiar_einsertar_coleccion(nombre_archivo_json, nombre_coleccion):
    print(f"\n--- Procesando: {nombre_archivo_json} para la colección '{nombre_coleccion}' ---")
    
    if not os.path.exists(nombre_archivo_json):
        print(f"El archivo {nombre_archivo_json} no existe. Saltando este archivo.")

    with open(nombre_archivo_json, "r", encoding="utf-8") as f:
        bruto = json.load(f)

    planos = aplanar_json_stat(bruto)
    limpios = limpiar_datos(planos)
  
    if limpios:
        coleccion = db[nombre_coleccion]
        coleccion.delete_many({})
        coleccion.insert_many(limpios)
    else:
        print(f"No se encontraron registros válidos para insertar en la colección '{nombre_coleccion}'.")
    

def aplanar_json_stat(datos_brutos):
    dataset = datos_brutos.get("dataset", {})
    
    dimensiones_ids = dataset.get("dimension", {}).get("id", [])
    tamanios = dataset.get("dimension", {}).get("size", [])
    
    if not dimensiones_ids or not tamanios:
        return []

    etiquetas_dimensiones = []
    for dim_id in dimensiones_ids:
        cat_labels = dataset["dimension"][dim_id]["category"]["label"]
        etiquetas_dimensiones.append(list(cat_labels.values()))
        
    valores = dataset.get("value", [])
    
    if isinstance(valores, dict):
        total_elementos = 1
        for s in tamanios:
            total_elementos *= s
        lista_valores = [None] * total_elementos
        for idx_str, val in valores.items():
            lista_valores[int(idx_str)] = val
        valores = lista_valores

    combinaciones = list(itertools.product(*etiquetas_dimensiones))
    
    registros_planos = []
    for idx, combinacion in enumerate(combinaciones):
        valor_actual = valores[idx] if idx < len(valores) else None
        
        registro = {}
        for i, dim_id in enumerate(dimensiones_ids):
            registro[dim_id] = combinacion[i]
            
        registro["valor"] = valor_actual
        registros_planos.append(registro)
        
    return registros_planos

      
def limpiar_datos(registros_planos):
    registros_limpios = []
    
    for item in registros_planos:
        valor_bruto = item.get("valor")
        
        if valor_bruto in [".", "..", "", None]:
            continue
            
        try:
            valor_limpio = float(valor_bruto)
        except (ValueError, TypeError):
            continue  
            
        documento = {}
        for k, v in item.items():
            if k == "valor":
                documento["valor"] = valor_limpio
            elif k == "periodo":
                try:
                    documento["periodo"] = int(v)
                except (ValueError, TypeError):
                    documento["periodo"] = v
            else:
                documento[k] = v
                
        registros_limpios.append(documento)

    unicos = {}
    for doc in registros_limpios:
        clave_unica = tuple(val for k, val in doc.items() if k != "valor")
        unicos[clave_unica] = doc 
        
    return list(unicos.values())       

ficheros_a_limpiar = [
    ("datos/raw/Api/mediaRenta.json", "rentas_jovenes"),
    ("datos/raw/Api/activosMunicipio.json", "poblacion_activa"),
    ("datos/raw/Api/asalariadosTipoContrato.json", "asalariados_contrato"),
    ("datos/raw/Api/poblacionEuskadi.json", "poblacion_demografia"),
    ("datos/raw/Api/viviendasEuskadi.json", "vivienda_tenencia")
]

for archivo, col_name in ficheros_a_limpiar:
    limpiar_einsertar_coleccion(archivo, col_name)

print("\n¡Proceso de limpieza y carga en MongoDB completado con éxito!")