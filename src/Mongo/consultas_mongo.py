from pymongo import MongoClient, ASCENDING, DESCENDING

cliente = MongoClient("mongodb://localhost:27017/")

bd = cliente["emancipacion_euskadi"]

pisos = bd["pisos"]
poblacion = bd["poblacion_demografia"]
activa = bd["poblacion_activa"]
rentas = bd["rentas_jovenes"]
salarios = bd["asalariados_contrato"]
tenencia = bd["vivienda_tenencia"]

#Mostrar todos los pisos
resultado = pisos.find()

for piso in resultado:
    print(piso)


#Mostrar los pisos de Bilbao
resultado = pisos.find({
    "Municipio": "Bilbao"
})

for piso in resultado:
    print(piso)

#Buscar pisos de 850 €
resultado = pisos.find({
    "Precio": 850
})

for piso in resultado:
    print(piso)

#Alquileres por debajo de 700 €
resultado = pisos.find({
    "Precio": {"$lt": 700}
})

for piso in resultado:
    print(piso)

#Pisos con al menos 3 hab
resultado = pisos.find({
    "Habitaciones": {"$gte": 3}
})

for piso in resultado:
    print(piso)

#Pisos en los municipos Bilbao o Barakaldo
resultado = pisos.find({
    "Municipio": {
        "$in": ["Bilbao", "Barakaldo"]
    }
})

for piso in resultado:
    print(piso)

#Pisos con 2 hab y precio por debajo de 900€
resultado = pisos.find({
    "Habitaciones": {"$gt": 2},
    "Precio": {"$lt": 900}
})

for piso in resultado:
    print(piso)

#Pisos de Bilbao o pisos por debajo de 500€
resultado = pisos.find({
    "$or": [
        {"Municipio": "Bilbao"},
        {"Precio": {"$lt": 500}}
    ]
})

for piso in resultado:
    print(piso)

#Proyección de datos (mostrar solo los que tienen 1)
resultado = pisos.find(
    {},
    {
        "_id": 0,
        "Municipio": 1,
        "Precio": 1,
        "Habitaciones": 1
    }
)

for piso in resultado:
    print(piso)

resultado = pisos.find(
    {
        "Municipio": "Bilbao",
        "Precio": {"$lt": 800}
    },
    {
        "_id": 0,
        "Municipio": 1,
        "Precio": 1,
        "Metros": 1,
        "Habitaciones": 1
    }
)

for piso in resultado:
    print(piso)

#Ordenar datos con sort
resultado = pisos.find().sort(
    "Precio", ASCENDING
)

for piso in resultado:
    print(piso)

#Mostrar los 10 pisos más baratos
resultado = pisos.find(
    {},
    {
        "_id": 0,
        "Municipio": 1,
        "Precio": 1,
        "Habitaciones": 1
    }
).sort(
    "Precio", ASCENDING
).limit(10)

for piso in resultado:
    print(piso)

#Contar documentos(objetos que cuamplan los filtros)
cantidad = pisos.count_documents({
    "Municipio": "Bilbao"
})

print("Número de pisos:", cantidad)

#Obtener todos los municipios diferentes
municipios = pisos.distinct("Municipio")

for municipio in municipios:
    print(municipio)

resultado = pisos.find({
    "Metros": {"$exists": True}
})

for piso in resultado:
    print(piso)

#Buscar los pisos que sean de temporada
resultado = pisos.find({
    "TipoContrato": "Temporada"
})

for piso in resultado:
    print(piso)


#Rentas de jóvenes 18 a 19
resultado = rentas.find({
    "edad": "18 - 19 años",
    "sexo": "Total"
})

for jovenes in resultado:
    print(jovenes)

#Poblacion activa 2024, Vitoria
resultado = activa.find({
    "municipio (> 40.000 habitantes)": "Vitoria-Gasteiz",
    "periodo": 2024
})

for activos in resultado:
    print(activos)

#Poblacion en Euskadi en un periodo 
resultado = poblacion.find({
    "ámbitos territoriales": "C.A. de Euskadi",
    "periodo": "2023/07/01"
})

for poblacion in resultado:
    print(activos)

