from pymongo import MongoClient, ASCENDING

cliente = MongoClient("mongodb://localhost:27017/")

bd = cliente["emancipacion_euskadi"]

def crear_indices():

    pisos = bd["pisos"]

    pisos.create_index(
        [("Municipio", ASCENDING)]
    )

    pisos.create_index(
        [("Precio", ASCENDING)]
    )

    pisos.create_index(
        [("TipoContrato", ASCENDING)]
        
    )

    pisos.create_index([
        ("Municipio", ASCENDING),
        ("TipoContrato", ASCENDING)
    ])

    poblacion = bd["poblacion_demografia"]

    poblacion.create_index([
        ("ámbitos territoriales", ASCENDING),
        ("periodo", ASCENDING)
    ])

    activa = bd["poblacion_activa"]

    activa.create_index([
        ("municipio (> 40.000 habitantes)", ASCENDING),
        ("periodo", ASCENDING)
    ])

    asalariados = bd["asalariados_contrato"]

    asalariados.create_index([
        ("territorio histórico", ASCENDING),
        ("periodo", ASCENDING)
    ])

    rentas = bd["rentas_jovenes"]

    rentas.create_index([
        ("edad", ASCENDING),
        ("periodo", ASCENDING)
    ])

    tenencia = bd["vivienda_tenencia"]

    tenencia.create_index([
        ("ámbito territorial", ASCENDING),
        ("periodo", ASCENDING)
    ])

    print("Índices creados correctamente")

crear_indices()





