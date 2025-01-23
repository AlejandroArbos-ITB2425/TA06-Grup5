import os
import numpy as np
from collections import defaultdict

def calculate_precipitation_summary(file_path):
    """
    Calcula el total y el promedio mensual de los valores de precipitación por año en un archivo.
    Ignora las columnas iniciales que no son precipitaciones (P1, año, mes).
    """
    yearly_precipitation = defaultdict(list)

    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Dividir la línea en valores
                values = line.split()
                # Ignorar líneas que no contienen datos de precipitaciones
                if len(values) > 3 and values[0].startswith("P"):
                    year = values[1]  # El segundo valor es el año
                    # Extraer solo los valores de precipitación (después de las 3 primeras columnas)
                    precipitation_values = [float(v) for v in values[3:] if v.replace('.', '', 1).isdigit()]
                    yearly_precipitation[year].extend(precipitation_values)
    except Exception as e:
        print(f"Error al procesar el archivo {file_path}: {e}")
        return None

    # Calcular el total y el promedio mensual de las precipitaciones por año
    summary = {}
    for year, values in yearly_precipitation.items():
        total_precipitation = sum(values)
        monthly_average = total_precipitation / 12  # Asumimos 12 meses
        summary[year] = {
            "total_precipitation": total_precipitation,
            "monthly_average": monthly_average
        }

    return summary

def process_directory(directory_path):
    """
    Procesa todos los archivos en un directorio y calcula el resumen anual de precipitaciones por archivo.
    """
    results = {}

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):  # Asegurarse de que sea un archivo
                print(f"Procesando archivo: {file_name}")
                yearly_summary = calculate_precipitation_summary(file_path)
                if yearly_summary is not None:
                    results[file_name] = yearly_summary
                else:
                    results[file_name] = "Error al calcular"

    # Mostrar resultados
    print("\nResumen por archivo:")
    for file_name, yearly_data in results.items():
        if isinstance(yearly_data, dict):
            print(f"Resumen para el archivo {file_name}:")
            for year, data in sorted(yearly_data.items()):
                print(f"Resumen para el año {year}:")
                print(f"Total de precipitación en {year}: {data['total_precipitation']:.1f}")
                print(f"Promedio mensual en {year}: {data['monthly_average']:.2f}")
                print(f"Tasa de variación anual en {year}: ---")  # Placeholder para tasa de variación si se requiere
            print("\n")
        else:
            print(f"{file_name}: {yearly_data}")

    return results

# Directorio donde están los archivos de ejemplo
directory_path = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
process_directory(directory_path)
