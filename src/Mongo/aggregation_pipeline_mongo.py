from pymongo import MongoClient, ASCENDING, DESCENDING

cliente = MongoClient("mongodb://localhost:27017/")

bd = cliente["emancipacion_euskadi"]

pisos = bd["pisos"]


def estadisticas_municipios():

    resultado = pisos.aggregate([
#Filtra los anuncios que valgan
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Municipio": {"$ne": None},
                "TipoContrato": "Temporada"
            }
        },

#Agrupar por municipio
        {
            "$group": {
                "_id": "$Municipio",

                "precio_medio": {
                    "$avg": "$Precio"
                },

                "precio_minimo": {
                    "$min": "$Precio"
                },

                "precio_maximo": {
                    "$max": "$Precio"
                },

                "metros_medios": {
                    "$avg": "$Metros"
                },

                "total_anuncios": {
                    "$sum": 1
                }
            }
        },

#Seleccionar los campos que queremos coger
        {
            "$project": {
                "_id": 0,
                "municipio": "$_id",
                "precio_medio": 1,
                "precio_minimo": 1,
                "precio_maximo": 1,
                "metros_medios": 1,
                "total_anuncios": 1
            }
        },

#Ordena por precio medio
        {
            "$sort": {
                "precio_medio": 1
            }
        }

    ])

    for municipio in resultado:
        print(municipio)




def estadisticas_contrato():

    resultado = pisos.aggregate([

#Filtrar anuncios con precio válido
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Municipio": {"$ne": None},
                "TipoContrato": {"$ne": None}
            }
        },

#Agrupar por municipio y tipo de contrato
        {
            "$group": {
                "_id": {
                    "municipio": "$Municipio",
                    "contrato": "$TipoContrato"
                },

                "total_anuncios": {"$sum": 1},
                "precio_medio": {"$avg": "$Precio"}
            }
        },

#Seleccionar campos
        {
            "$project": {
                "_id": 0,
                "municipio": "$_id.municipio",
                "tipo_contrato": "$_id.contrato",
                "total_anuncios": 1,
                "precio_medio": 1
            }
        },

#Ordenar por municipio
        {
            "$sort": {
                "municipio": 1,
                "precio_medio": 1
            }
        }

    ])

    for documento in resultado:
        print(documento)


def municipios_economicos():

    resultado = pisos.aggregate([

#Filtrar anuncios válidos
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Municipio": {"$ne": None}
            }
        },

#Agrupar por municipio
        {
            "$group": {
                "_id": "$Municipio",

                "precio_medio": {
                    "$avg": "$Precio"
                },

                "total_anuncios": {
                    "$sum": 1
                }
            }
        },

#Necesitar un mínimo de anuncios
        {
            "$match": {
                "total_anuncios": {"$gte": 3}
            }
        },

#Ordenar de menor a mayor
        {
            "$sort": {
                "precio_medio": 1
            }
        },

#Mostrar los cinco primeros
        {
            "$limit": 5
        }

    ])

    for municipio in resultado:
        print(municipio)


def precio_metro_municipio():

    resultado = pisos.aggregate([

#Filtrar viviendas con superficie y precio válidos
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Metros": {"$gt": 0},
                "Municipio": {"$ne": None}
            }
        },

#Agrupar por municipio
        {
            "$group": {
                "_id": "$Municipio",

                "precio_m2_medio": {
                    "$avg": "$PrecioM2"
                },

                "metros_medios": {
                    "$avg": "$Metros"
                },

                "total_anuncios": {
                    "$sum": 1
                }
            }
        },

#Crear y seleccionar resultados
        {
            "$project": {
                "_id": 0,
                "municipio": "$_id",
                "precio_m2_medio": {
                    "$round": ["$precio_m2_medio", 2]
                },
                "metros_medios": {
                    "$round": ["$metros_medios", 2]
                },
                "total_anuncios": 1
            }
        },

#Ordenar por precio por metro cuadrado
        {
            "$sort": {
                "precio_m2_medio": 1
            }
        }

    ])

    for municipio in resultado:
        print(municipio)



def precios_por_municipio_y_contrato():
    resultado = pisos.aggregate([
#Filtrar anuncios válidos
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Municipio": {"$ne": None},
                "TipoContrato": {"$in": ["Larga estancia", "Temporada"]}
            }
        },

#Agrupar por municipio y tipo de contrato
        {
            "$group": {
                "_id": {
                    "municipio": "$Municipio",
                    "contrato": "$TipoContrato"
                },
                "precio_medio": {"$avg": "$Precio"},
                "precio_minimo": {"$min": "$Precio"},
                "precio_maximo": {"$max": "$Precio"},
                "total_anuncios": {"$sum": 1}
            }
        },

# Dar nombres claros a los campos
        {
            "$project": {
                "_id": 0,
                "municipio": "$_id.municipio",
                "tipo_contrato": "$_id.contrato",
                "precio_medio": {"$round": ["$precio_medio", 2]},
                "precio_minimo": 1,
                "precio_maximo": 1,
                "total_anuncios": 1
            }
        },

#Ordenar por municipio y precio
        {
            "$sort": {
                "municipio": 1,
                "precio_medio": 1
            }
        }
    ])

    return list(resultado)


for dato in precios_por_municipio_y_contrato():
    print(dato)


def municipios_mas_economicos():
    resultado = pisos.aggregate([
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Municipio": {"$ne": None},
                "TipoContrato": "Larga estancia"
            }
        },
        {
            "$group": {
                "_id": "$Municipio",
                "precio_medio": {"$avg": "$Precio"},
                "total_anuncios": {"$sum": 1}
            }
        },
        {
            "$match": {
                "total_anuncios": {"$gte": 3}
            }
        },
        {
            "$sort": {
                "precio_medio": 1
            }
        },
        {
            "$limit": 5
        }
    ])

    return list(resultado)


def precio_m2_por_municipio():
    resultado = pisos.aggregate([
        {
            "$match": {
                "Precio": {"$gt": 0},
                "Metros": {"$gt": 0},
                "Municipio": {"$ne": None},
                "TipoContrato": "Larga estancia"
            }
        },
        {
            "$group": {
                "_id": "$Municipio",
                "precio_m2_medio": {"$avg": "$PrecioM2"},
                "metros_medios": {"$avg": "$Metros"},
                "total_anuncios": {"$sum": 1}
            }
        },
        {
            "$project": {
                "_id": 0,
                "municipio": "$_id",
                "precio_m2_medio": {
                    "$round": ["$precio_m2_medio", 2]
                },
                "metros_medios": {
                    "$round": ["$metros_medios", 2]
                },
                "total_anuncios": 1
            }
        },
        {
            "$sort": {
                "precio_m2_medio": 1
            }
        }
    ])

    return list(resultado)



if __name__ == "__main__":  
    for dato in precio_m2_por_municipio():
        print(dato)

    for dato in municipios_mas_economicos():
        print(dato)

    precio_metro_municipio()

    municipios_economicos()

    estadisticas_contrato()

    estadisticas_municipios()

