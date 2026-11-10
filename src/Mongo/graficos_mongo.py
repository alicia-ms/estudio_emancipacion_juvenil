
from pymongo import MongoClient
import matplotlib.pyplot as plt
import os
import statistics
import re

cliente = MongoClient("mongodb://localhost:27017/")

bd = cliente["emancipacion_euskadi"]
pisos = bd["pisos"]
rentas = bd["rentas_jovenes"]

CARPETA_GRAFICOS = os.path.join(
    os.path.dirname(__file__),
    "graficos"
)

os.makedirs(CARPETA_GRAFICOS, exist_ok=True)

MINIMO_ANUNCIOS = 3


def obtener_filtro(contrato):
    return {
        "TipoContrato": contrato,
        "Municipio": {"$ne": None},
        "Precio": {
            "$type": "number",
            "$gt": 0
        }
    }


def grafico_precio_medio(contrato):

    filtro = obtener_filtro(contrato)

    resultado = pisos.aggregate([

        {
            "$match": filtro
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
                "total_anuncios": {
                    "$gte": MINIMO_ANUNCIOS
                }
            }
        },

        {
            "$project": {
                "_id": 0,
                "municipio": "$_id",
                "precio_medio": {
                    "$round": ["$precio_medio", 2]
                },
                "total_anuncios": 1
            }
        },

        {
            "$sort": {
                "precio_medio": 1
            }
        }

    ])

    datos = list(resultado)

    if not datos:
        print(f"No hay datos suficientes para el precio medio de {contrato}.")
        return

    municipios = [d["municipio"] for d in datos]
    precios = [d["precio_medio"] for d in datos]
    cantidades = [d["total_anuncios"] for d in datos]

    plt.figure(figsize=(11, 6))

    barras = plt.bar(municipios, precios)

    plt.title(
        f"Precio medio del alquiler por municipio - {contrato}",
        fontsize=14
    )

    plt.xlabel("Municipio")
    plt.ylabel("Precio medio mensual (€)")

    plt.xticks(rotation=30, ha="right")

    for barra, cantidad in zip(barras, cantidades):

        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{cantidad} anuncios",
            ha="center",
            va="bottom",
            fontsize=8
        )

    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    nombre = f"grafico1_precio_medio_{contrato.replace(' ', '_')}.png"
    ruta = os.path.join(CARPETA_GRAFICOS, nombre)

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico guardado en:", ruta)


def grafico_distribucion_precios(contrato):

    filtro = obtener_filtro(contrato)

    resultado = pisos.find(
        filtro,
        {
            "_id": 0,
            "Municipio": 1,
            "Precio": 1
        }
    )

    precios_por_municipio = {}

    for piso in resultado:

        municipio = piso["Municipio"]
        precio = float(piso["Precio"])

        if municipio not in precios_por_municipio:
            precios_por_municipio[municipio] = []

        precios_por_municipio[municipio].append(precio)

    precios_por_municipio = {
        municipio: precios
        for municipio, precios in precios_por_municipio.items()
        if len(precios) >= MINIMO_ANUNCIOS
    }

    if len(precios_por_municipio) < 2:
        print(f"No hay suficientes municipios para la distribución de {contrato}.")
        return

    municipios = sorted(precios_por_municipio.keys())

    datos = [
        precios_por_municipio[municipio]
        for municipio in municipios
    ]

    plt.figure(figsize=(12, 7))

    plt.boxplot(
        datos,
        tick_labels=municipios,
        showmeans=True
    )

    plt.title(
        f"Distribución de precios del alquiler por municipio - {contrato}",
        fontsize=14
    )

    plt.xlabel("Municipio")
    plt.ylabel("Precio mensual (€)")

    plt.xticks(rotation=30, ha="right")

    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    nombre = f"grafico2_distribucion_precios_{contrato.replace(' ', '_')}.png"
    ruta = os.path.join(CARPETA_GRAFICOS, nombre)

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico guardado en:", ruta)


def grafico_superficie_precio(contrato):

    filtro = {
        **obtener_filtro(contrato),
        "Metros": {
            "$type": "number",
            "$gt": 0
        }
    }

    resultado = pisos.find(
        filtro,
        {
            "_id": 0,
            "Municipio": 1,
            "Metros": 1,
            "Precio": 1
        }
    )

    datos_por_municipio = {}

    for piso in resultado:

        municipio = piso["Municipio"]
        metros = float(piso["Metros"])
        precio = float(piso["Precio"])

        if municipio not in datos_por_municipio:
            datos_por_municipio[municipio] = {
                "metros": [],
                "precios": []
            }

        datos_por_municipio[municipio]["metros"].append(metros)
        datos_por_municipio[municipio]["precios"].append(precio)

    datos_por_municipio = {
        municipio: datos
        for municipio, datos in datos_por_municipio.items()
        if len(datos["metros"]) >= MINIMO_ANUNCIOS
    }

    if not datos_por_municipio:
        print(f"No hay datos suficientes para la superficie y precio de {contrato}.")
        return

    plt.figure(figsize=(11, 7))

    for municipio, datos in sorted(datos_por_municipio.items()):

        plt.scatter(
            datos["metros"],
            datos["precios"],
            label=municipio,
            alpha=0.7
        )

    plt.title(
        f"Relación entre superficie y precio - {contrato}",
        fontsize=14
    )

    plt.xlabel("Superficie de la vivienda (m²)")
    plt.ylabel("Precio mensual (€)")

    plt.legend(
        title="Municipios",
        bbox_to_anchor=(1.05, 1),
        loc="upper left"
    )

    plt.grid(alpha=0.3)
    plt.tight_layout()

    nombre = f"grafico3_superficie_precio_{contrato.replace(' ', '_')}.png"
    ruta = os.path.join(CARPETA_GRAFICOS, nombre)

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico guardado en:", ruta)


def grafico_ingresos_alquiler(contrato):

    filtro = obtener_filtro(contrato)

    ingresos = list(rentas.find(
        {
            "sexo": "Total",
            "tipo de renta": "Renta del trabajo",
            "periodo": 2024,
            "valor": {
                "$type": "number",
                "$gt": 0
            }
        },
        {
            "_id": 0,
            "edad": 1,
            "valor": 1
        }
    ))

    precios = [
        float(p["Precio"])
        for p in pisos.find(filtro, {"Precio": 1})
    ]

    if not ingresos or not precios:
        print(f"No hay datos suficientes para ingresos y alquiler de {contrato}.")
        return

    alquiler_mediano = statistics.median(precios)

    ingresos.sort(key=lambda x: int(
        re.search(r"\d+", x["edad"]).group()
    ))

    edades = [d["edad"] for d in ingresos]

    ingresos_mensuales = [
        d["valor"] / 12 for d in ingresos
    ]

    plt.figure(figsize=(11, 6))

    plt.bar(
        edades,
        ingresos_mensuales,
        label="Renta mensual equivalente"
    )

    plt.axhline(
        alquiler_mediano,
        linestyle="--",
        label=f"Alquiler mediano: {alquiler_mediano:.2f} €"
    )

    plt.title(
        f"Ingresos de los jóvenes frente al alquiler - {contrato}",
        fontsize=14
    )

    plt.xlabel("Grupo de edad")
    plt.ylabel("Euros mensuales (€)")

    plt.xticks(rotation=25, ha="right")

    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    nombre = f"grafico4_ingresos_alquiler_{contrato.replace(' ', '_')}.png"
    ruta = os.path.join(CARPETA_GRAFICOS, nombre)

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico guardado en:", ruta)


def grafico_porcentaje_alquiler(contrato):

    filtro = obtener_filtro(contrato)

    ingresos = list(rentas.find(
        {
            "sexo": "Total",
            "tipo de renta": "Renta del trabajo",
            "periodo": 2024,
            "valor": {
                "$type": "number",
                "$gt": 0
            }
        },
        {
            "_id": 0,
            "edad": 1,
            "valor": 1
        }
    ))

    precios = [
        float(p["Precio"])
        for p in pisos.find(filtro, {"Precio": 1})
    ]

    if not ingresos or not precios:
        print(f"No hay datos suficientes para el porcentaje de {contrato}.")
        return

    alquiler_mediano = statistics.median(precios)

    ingresos.sort(key=lambda x: int(
        re.search(r"\d+", x["edad"]).group()
    ))

    edades = []
    porcentajes = []

    for dato in ingresos:

        ingreso_mensual = dato["valor"] / 12

        if ingreso_mensual <= 0:
            continue

        porcentaje = (
            alquiler_mediano / ingreso_mensual
        ) * 100

        edades.append(dato["edad"])
        porcentajes.append(porcentaje)

    if not porcentajes:
        print(f"No hay ingresos válidos para el porcentaje de {contrato}.")
        return

    plt.figure(figsize=(11, 6))

    barras = plt.bar(edades, porcentajes)

    plt.axhline(
        30,
        color="red",
        linestyle="--",
        label="Referencia orientativa del 30%"
    )

    plt.title(
        f"Porcentaje de ingresos destinado al alquiler - {contrato}",
        fontsize=14
    )

    plt.xlabel("Grupo de edad")
    plt.ylabel("Porcentaje de los ingresos (%)")

    plt.xticks(rotation=25, ha="right")

    for barra, porcentaje in zip(barras, porcentajes):

        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height(),
            f"{porcentaje:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9
        )

    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    nombre = f"grafico5_porcentaje_alquiler_{contrato.replace(' ', '_')}.png"
    ruta = os.path.join(CARPETA_GRAFICOS, nombre)

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico guardado en:", ruta)


def grafico_proporcion_contratos():

    resultado = list(pisos.aggregate([
        {
            "$match": {
                "TipoContrato": {
                    "$in": ["Larga estancia", "Temporada"]
                }
            }
        },
        {
            "$group": {
                "_id": "$TipoContrato",
                "cantidad": {"$sum": 1}
            }
        }
    ]))

    cantidades = {
        dato["_id"]: dato["cantidad"]
        for dato in resultado
    }

    larga = cantidades.get("Larga estancia", 0)
    temporada = cantidades.get("Temporada", 0)

    if larga + temporada == 0:
        print("No hay anuncios para el grafico 6.")
        return

    etiquetas = ["Larga estancia", "Temporada"]
    valores = [larga, temporada]

    plt.figure(figsize=(8, 6))

    plt.pie(
        valores,
        labels=etiquetas,
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Proporción de anuncios por tipo de contrato")
    plt.tight_layout()

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico6_proporcion_contratos.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 6 guardado en:", ruta)


def grafico_cantidad_pisos_contrato():

    resultado = list(pisos.aggregate([
        {
            "$match": {
                "TipoContrato": {
                    "$in": ["Larga estancia", "Temporada"]
                },
                "Municipio": {"$ne": None}
            }
        },
        {
            "$group": {
                "_id": {
                    "municipio": "$Municipio",
                    "contrato": "$TipoContrato"
                },
                "cantidad": {"$sum": 1}
            }
        },
        {
            "$sort": {
                "_id.municipio": 1
            }
        }
    ]))

    if not resultado:
        print("No hay datos suficientes para el grafico 7.")
        return

    datos = {}

    for dato in resultado:

        municipio = dato["_id"]["municipio"]
        contrato = dato["_id"]["contrato"]

        if municipio not in datos:
            datos[municipio] = {
                "Larga estancia": 0,
                "Temporada": 0
            }

        datos[municipio][contrato] = dato["cantidad"]

    municipios = sorted(datos.keys())

    larga = [
        datos[m]["Larga estancia"]
        for m in municipios
    ]

    temporada = [
        datos[m]["Temporada"]
        for m in municipios
    ]

    posiciones = list(range(len(municipios)))
    ancho = 0.35

    plt.figure(figsize=(12, 6))

    plt.bar(
        [p - ancho / 2 for p in posiciones],
        larga,
        width=ancho,
        label="Larga estancia"
    )

    plt.bar(
        [p + ancho / 2 for p in posiciones],
        temporada,
        width=ancho,
        label="Temporada"
    )

    plt.title("Cantidad de pisos por municipio y tipo de contrato")
    plt.xlabel("Municipio")
    plt.ylabel("Número de anuncios")

    plt.xticks(posiciones, municipios, rotation=30, ha="right")

    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico7_cantidad_pisos_contrato.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 7 guardado en:", ruta)


if __name__ == "__main__":

    try:

        print("Generando graficos desde MongoDB...")

        grafico_proporcion_contratos()
        grafico_cantidad_pisos_contrato()

        for contrato in ["Larga estancia", "Temporada"]:

            print(f"\nGenerando graficos de {contrato}...")

            grafico_precio_medio(contrato)
            grafico_distribucion_precios(contrato)
            grafico_superficie_precio(contrato)
            grafico_ingresos_alquiler(contrato)
            grafico_porcentaje_alquiler(contrato)

        print("\nProceso de graficos finalizado.")

    finally:
        cliente.close()
