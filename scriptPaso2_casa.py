import os
import re
from datetime import datetime
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ----------------------- FUNCIONES DEL PRIMER SCRIPT (X) ----------------------- #
def log_error(message, is_terminal=False):
    """Guarda el mensaje de error en el archivo errores.log y muestra en terminal si es necesario."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{timestamp}: {message}"
    with open("errores.log", "a") as log_file:
        log_file.write(formatted_message + "\n")

    if is_terminal:
        print(f"\033[31m{message}\033[0m")

def is_leap_year(year):
    """Determina si un año es bisiesto."""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def get_days_in_month(year, month):
    """Devuelve el número de días en un mes dado, considerando si el año es bisiesto."""
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    if month == 2 and is_leap_year(year):
        return 29
    return days_in_month.get(month, 0)

def validate_dat_files(directory):
    """Valida que los archivos .dat cumplan con el formato especificado y que todos los archivos sean .dat."""
    try:
        files = os.listdir(directory)
    except FileNotFoundError:
        log_error("No se ha podido encontrar el directorio.", is_terminal=True)
        return

    if not files:
        log_error("No se encontraron archivos en el directorio.", is_terminal=True)
        return

    all_valid = True

    non_dat_files = [f for f in files if not f.endswith('.dat')]
    if non_dat_files:
        for file in non_dat_files:
            error_message = f"ERROR: {file} MOTIVO: No es un archivo .dat."
            log_error(error_message)
            all_valid = False

    files = [f for f in files if f.endswith('.dat')]

    if not files:
        log_error("No se encontraron archivos .dat en el directorio.", is_terminal=True)
        return

    for file in files:
        file_path = os.path.join(directory, file)

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            if len(lines) < 2:
                error_message = f"ERROR: {file} MOTIVO: No tiene suficientes líneas para ser procesado."
                log_error(error_message)
                all_valid = False
                continue

            header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
            if not lines[0].strip() == header:
                error_message = f"ERROR: {file} MOTIVO: La cabecera no coincide con el formato esperado."
                log_error(error_message)
                all_valid = False

            file_prefix = file.split('.')[1]
            expected_prefix = file_prefix[1:]

            second_line = lines[1].strip().split('\t')
            if len(second_line) != 8 or not second_line[0].startswith('P'):
                error_message = (
                    f"ERROR: {file} MOTIVO: La segunda línea no cumple el formato. "
                    f"Esperado prefijo 'P' y 8 columnas, encontrado: {len(second_line)} columnas."
                )
                log_error(error_message)
                all_valid = False

            if second_line[0][1:] != expected_prefix:
                error_message = f"ERROR: {file} MOTIVO: El prefijo en la segunda línea ({second_line[0]}) no coincide con el nombre del archivo ({file_prefix})."
                log_error(error_message)
                all_valid = False

        except Exception as e:
            error_message = f"ERROR: {file} MOTIVO: Error inesperado durante el procesamiento. Detalles: {str(e)}"
            log_error(error_message)
            all_valid = False

    if not all_valid:
        print("\033[31mSe encontraron errores en uno o más archivos .dat.\033[0m")
    else:
        print("\033[32mValidación completada: Todos los archivos .dat están en el formato esperado.\033[0m")

# ----------------------- FUNCIONES DEL SEGUNDO SCRIPT (Y) ----------------------- #
def process_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file.readlines()[2:]:
            parts = line.strip().split()
            if len(parts) > 3:
                data.append(parts)

    columns = ["Region", "Year", "Month"] + [f"Day_{i + 1}" for i in range(31)]
    df = pd.DataFrame(data, columns=columns)
    df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    return df

def analyze_data(directory):
    missing_value = -999
    all_data = []

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            try:
                df = process_file(file_path)
                df["Source_File"] = filename
                all_data.append(df)
            except Exception as e:
                print(f"Error procesando el archivo {filename}: {e}")

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].applymap(lambda x: np.nan if x == missing_value else x)

    # Asegurarse de que todas las columnas relevantes sean numéricas
    numeric_cols = combined_df.columns[3:]
    combined_df[numeric_cols] = combined_df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    combined_df["Annual_Total"] = combined_df.iloc[:, 3:].sum(axis=1, skipna=True)
    combined_df["Annual_Mean"] = combined_df.iloc[:, 3:].mean(axis=1, skipna=True)

    annual_stats = combined_df.groupby("Year")["Annual_Total"].agg(['sum', 'mean'])
    annual_stats["Change_Rate"] = annual_stats["sum"].pct_change() * 100

    most_rainy_year = annual_stats["sum"].idxmax()
    least_rainy_year = annual_stats["sum"].idxmin()

    print("\n" + "-" * 40)
    print(f"Año más lluvioso: {most_rainy_year}, Precipitación total: {annual_stats.loc[most_rainy_year, 'sum']}")
    print(f"Año más seco: {least_rainy_year}, Precipitación total: {annual_stats.loc[least_rainy_year, 'sum']}")

    annual_stats.to_csv("resultados_annual_stats.csv", index=True)
    with open("resultados_annual_stats.txt", "w") as f:
        f.write(annual_stats.to_string())

# ----------------------- EJECUCIÓN SECUENCIAL ----------------------- #

directory_x = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
directory_y = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
print("Iniciando validación de archivos .dat...")
validate_dat_files(directory_x)

print("\nIniciando análisis de datos...")
analyze_data(directory_y)

print("\nProceso completo.")
