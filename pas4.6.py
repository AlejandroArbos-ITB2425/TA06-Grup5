import os
import numpy as np
import pandas as pd

def calculate_annual_precipitation(input_dir, output_file):
    """
    Calcula la media anual de precipitación para cada estación meteorológica.

    Args:
        input_dir (str): Directorio donde se encuentran los archivos.
        output_file (str): Archivo donde se guardarán los resultados.
    """
    # Crear un diccionario para almacenar los resultados
    results = []

    # Iterar sobre cada archivo en el directorio
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        # Comprobar que es un archivo válido
        if os.path.isfile(file_path) and file_name.endswith(".dat"):
            with open(file_path, "r") as file:
                lines = file.readlines()

            # Ignorar las dos primeras filas
            data_lines = lines[2:]

            # Procesar cada fila (mes)
            station_results = {}
            for line in data_lines:
                parts = line.split()

                # Extraer información de la fila
                station_id = parts[0]  # Ejemplo: P3, P4...
                year = int(parts[1])
                month = int(parts[2])
                precipitation = np.array([float(x) for x in parts[3:] if x != "-999" and x != "-999.0"])

                # Calcular la suma mensual válida
                if year not in station_results:
                    station_results[year] = []
                station_results[year].append(precipitation.sum())

            # Calcular la media anual por estación
            for year, monthly_precip in station_results.items():
                annual_mean = sum(monthly_precip) / len(monthly_precip)  # Media anual
                results.append({"Station": station_id, "Year": year, "AnnualMean": annual_mean})

    # Guardar los resultados en un archivo CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)

# Configuración
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
output_filename = "annual_precipitation_results.csv"

# Ejecutar la función
calculate_annual_precipitation(input_directory, output_filename)

print(f"Los resultados han sido guardados en {output_filename}.")
