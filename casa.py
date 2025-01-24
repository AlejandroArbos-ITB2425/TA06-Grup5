import os
import pandas as pd


def calcular_medias_carpeta(carpeta):
    """
    Calcula la precipitación total y promedio por año de todos los archivos en una carpeta.
    Permite consultar la media de un año específico.

    Args:
        carpeta (str): Ruta a la carpeta que contiene los archivos.

    Returns:
        dict: Diccionario con datos anuales agregados para consulta.
    """
    # Crear un dataframe vacío para acumular todos los datos
    datos_acumulados = []

    # Contador de estaciones
    numero_estaciones = 0

    # Iterar sobre todos los archivos en la carpeta
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".dat"):
            ruta_archivo = os.path.join(carpeta, archivo)

            # Leer el archivo y procesarlo
            with open(ruta_archivo, 'r') as f:
                lineas = f.readlines()

            # Eliminar la primera y segunda línea (no necesarias)
            datos = lineas[2:]

            # Crear una lista para almacenar los datos procesados
            datos_procesados = []

            for linea in datos:
                partes = linea.strip().split()

                # Ignorar las 3 primeras columnas y valores -999
                valores = [float(x) for x in partes[3:] if x != "-999"]

                # Agregar los valores procesados si existen
                if valores:
                    datos_procesados.append(valores)

            # Convertir los datos procesados en un DataFrame
            df = pd.DataFrame(datos_procesados)

            # Agregar los datos al acumulador
            datos_acumulados.append(df)
            numero_estaciones += 1

    # Combinar todos los datos en un único DataFrame
    if datos_acumulados:
        datos_todos = pd.concat(datos_acumulados, ignore_index=True)

        # Calcular la media mensual por estación
        media_mensual = datos_todos.mean(axis=1)

        # Agrupar por años (cada 12 filas corresponden a un año)
        media_anual_por_estacion = media_mensual.groupby(datos_todos.index // 12).mean()
        total_anual_por_estacion = media_mensual.groupby(datos_todos.index // 12).sum()

        # Calcular la media anual final dividiendo entre el número de estaciones
        media_anual_final = media_anual_por_estacion / numero_estaciones
        total_anual_final = total_anual_por_estacion

        return {
            "media_anual": media_anual_final,
            "total_anual": total_anual_final
        }

    return None


def consultar_anio(datos_aggregados, anio):
    """
    Consulta la media y total de precipitación para un año específico.

    Args:
        datos_aggregados (dict): Datos anuales agregados (medias y totales).
        anio (int): Año a consultar.

    Returns:
        str: Resultado de la consulta formateado.
    """
    inicio_anio = anio - 2006

    if inicio_anio in datos_aggregados["media_anual"].index:
        media_anual = datos_aggregados["media_anual"][inicio_anio]
        total_anual = datos_aggregados["total_anual"][inicio_anio]
        return (f"Año: {anio}\n"
                f"Precipitación total: {total_anual:.2f}\n"
                f"Precipitación media: {media_anual:.2f}\nEnd")
    else:
        return f"No se encontraron datos para el año {anio}.\nEnd"



carpeta = "preci_prova"

# Ejecutar
datos_aggregados = calcular_medias_carpeta(carpeta)
if datos_aggregados:
    anio = int(input("Año? "))
    print(consultar_anio(datos_aggregados, anio))
else:
    print("No se encontraron datos válidos en la carpeta.")