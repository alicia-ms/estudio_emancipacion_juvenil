
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

FILTRO_BASE = {
    "TipoContrato": "Larga estancia",
    "Municipio": {"$ne": None},
    "Precio": {
        "$type": "number",
        "$gt": 0
    }
}

MINIMO_ANUNCIOS = 3

def grafico_precio_medio():

    resultado = pisos.aggregate([

        {
            "$match": FILTRO_BASE
        },

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
        print("No hay datos suficientes para el grafico 1.")
        return

    municipios = [d["municipio"] for d in datos]
    precios = [d["precio_medio"] for d in datos]
    cantidades = [d["total_anuncios"] for d in datos]

    plt.figure(figsize=(11, 6))

    barras = plt.bar(municipios, precios)

    plt.title(
        "Precio medio del alquiler por municipio",
        fontsize=14
    )

    plt.xlabel("Municipio")
    plt.ylabel("Precio medio mensual (€)")

    plt.xticks(rotation=30, ha="right")

    for barra, cantidad in zip(barras, cantidades):

        altura = barra.get_height()

        plt.text(
            barra.get_x() + barra.get_width() / 2,
            altura,
            f"{cantidad} anuncios",
            ha="center",
            va="bottom",
            fontsize=8
        )

    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico1_precio_medio.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 1 guardado en:", ruta)


def grafico_distribucion_precios():

    resultado = pisos.find(
        FILTRO_BASE,
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
        print("No hay suficientes municipios para el grafico 2.")
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
    showmeans=True)

    plt.title(
        "Distribucion de precios del alquiler por municipio",
        fontsize=14
    )

    plt.xlabel("Municipio")
    plt.ylabel("Precio mensual (€)")

    plt.xticks(rotation=30, ha="right")

    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico2_distribucion_precios.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 2 guardado en:", ruta)

def grafico_superficie_precio():

    filtro = {
        **FILTRO_BASE,
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
        print("No hay datos suficientes para el grafico 3.")
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
        "Relacion entre superficie y precio del alquiler",
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

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico3_superficie_precio.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 3 guardado en:", ruta)



def grafico_ingresos_alquiler():

    ingresos = list(rentas.find(
        {
            "sexo": "Total",
            "tipo de renta": "Renta del trabajo",
            "periodo": 2024,
            "valor": {"$type": "number", "$gt": 0}
        },
        {
            "_id": 0,
            "edad": 1,
            "valor": 1
        }
    ))

    precios = [
        float(p["Precio"])
        for p in pisos.find(FILTRO_BASE, {"Precio": 1})
    ]

    if not ingresos or not precios:
        print("No hay datos suficientes para el grafico 4.")
        return

    alquiler_mediano = statistics.median(precios)

    ingresos.sort(key=lambda x: int(
        re.search(r"\d+", x["edad"]).group()
    ))

    edades = [d["edad"] for d in ingresos]

    # Eustat proporciona la renta en euros anuales.
    # La dividimos entre 12 para obtener una equivalencia mensual.
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
        "Ingresos de los jóvenes frente al precio del alquiler",
        fontsize=14
    )

    plt.xlabel("Grupo de edad")
    plt.ylabel("Euros mensuales (€)")
    plt.xticks(rotation=25, ha="right")

    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico4_ingresos_alquiler.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 4 guardado en:", ruta)


    
def grafico_porcentaje_alquiler():

    ingresos = list(rentas.find(
        {
            "sexo": "Total",
            "tipo de renta": "Renta del trabajo",
            "periodo": 2024,
            "valor": {"$type": "number", "$gt": 0}
        },
        {
            "_id": 0,
            "edad": 1,
            "valor": 1
        }
    ))

    precios = [
        float(p["Precio"])
        for p in pisos.find(FILTRO_BASE, {"Precio": 1})
    ]

    if not ingresos or not precios:
        print("No hay datos suficientes para el grafico 5.")
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
        print("No hay ingresos validos para el grafico 5.")
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
        "Porcentaje de los ingresos destinado al alquiler",
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

    ruta = os.path.join(
        CARPETA_GRAFICOS,
        "grafico5_porcentaje_alquiler.png"
    )

    plt.savefig(ruta, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    print("Grafico 5 guardado en:", ruta)



if __name__ == "__main__":

    try:

        print("Generando graficos desde MongoDB...")

        grafico_precio_medio()

        grafico_distribucion_precios()

        grafico_superficie_precio()

        grafico_ingresos_alquiler()

        grafico_porcentaje_alquiler()

        print("\nProceso de graficos finalizado.")

    finally:
        cliente.close()
