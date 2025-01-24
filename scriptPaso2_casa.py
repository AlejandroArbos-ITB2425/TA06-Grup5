import os
import re
from datetime import datetime
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Primera parte: Validación de archivos .dat
def log_error(message, is_terminal=False):
    """Guarda el mensaje de error en el archivo errores.log y muestra en terminal si es necesario."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{timestamp}: {message}"
    with open("errores.log", "a") as log_file:
        log_file.write(formatted_message + "\n")

    if is_terminal:
        print(f"\033[31m{message}\033[0m")

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
        except Exception as e:
            error_message = f"ERROR: {file} MOTIVO: Error inesperado durante el procesamiento. Detalles: {str(e)}"
            log_error(error_message)
            all_valid = False

    if not all_valid:
        print("\033[31mSe encontraron errores en uno o más archivos .dat.\033[0m")
    else:
        print("\033[32mValidación completada: Todos los archivos .dat están en el formato esperado.\033[0m")

# Cambia el directorio según sea necesario
directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
validate_dat_files(directory)

# Segunda parte: Calcular el porcentaje de datos faltantes (-999)
def count_values_in_file(file_path):
    """Cuenta las ocurrencias de '-999' y otros números."""
    count_negative_999 = 0
    count_other_numbers = 0
    try:
        with open(file_path, 'r') as file:
            for row_index, line in enumerate(file, start=1):
                if row_index <= 2:
                    continue
                values = line.split()
                values_to_count = values[3:]
                count_negative_999 += values_to_count.count("-999")
                count_other_numbers += sum(
                    1 for value in values_to_count if value != "-999" and value.replace('.', '', 1).lstrip('-').isdigit()
                )
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")
    return count_negative_999, count_other_numbers

def calculate_percentage(part, total):
    return (part / total * 100) if total > 0 else 0

def count_values_in_directory(directory_path):
    total_negative_999 = 0
    total_other_numbers = 0
    file_count = 0

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):
                file_count += 1
                file_negative_999, file_other_numbers = count_values_in_file(file_path)
                total_negative_999 += file_negative_999
                total_other_numbers += file_other_numbers

    total_values = total_negative_999 + total_other_numbers
    percentage_negative_999 = calculate_percentage(total_negative_999, total_values)

    print(f"\nRevisión completada.")
    print(f"Total de archivos procesados: {file_count}")
    print(f"Total de ocurrencias de -999: {total_negative_999}")
    print(f"Total de ocurrencias de otros números: {total_other_numbers}")
    print(f"Porcentaje de -999 respecto al total: {percentage_negative_999:.2f}%")

    return percentage_negative_999

count_values_in_directory(directory)

# Tercera parte: Procesamiento y análisis estadístico
data_folder = "./preci_prova"  # Carpeta que contiene los archivos
missing_value = -999  # Valor que representa datos faltantes

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

all_data = []
for filename in os.listdir(data_folder):
    file_path = os.path.join(data_folder, filename)
    if os.path.isfile(file_path):
        try:
            df = process_file(file_path)
            df["Source_File"] = filename
            all_data.append(df)
        except Exception as e:
            print(f"Error procesando el archivo {filename}: {e}")

combined_df = pd.concat(all_data, ignore_index=True)
combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].apply(pd.to_numeric, errors='coerce')
combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].applymap(lambda x: np.nan if x == missing_value else x)

combined_df["Annual_Total"] = combined_df.iloc[:, 3:].sum(axis=1, skipna=True)
combined_df["Annual_Mean"] = combined_df.iloc[:, 3:].mean(axis=1, skipna=True)

annual_stats = combined_df.groupby("Year")["Annual_Total"].agg(['sum', 'mean'])
annual_stats["Change_Rate"] = annual_stats["sum"].pct_change() * 100

most_rainy_year = annual_stats["sum"].idxmax()
least_rainy_year = annual_stats["sum"].idxmin()

max_daily_precip = combined_df.iloc[:, 3:].max(axis=1).groupby(combined_df['Year']).max()
min_daily_precip = combined_df.iloc[:, 3:].min(axis=1).groupby(combined_df['Year']).min()
annual_stats["Max_Daily"] = max_daily_precip
annual_stats["Min_Daily"] = min_daily_precip

for year in annual_stats.index:
    print(f"\nResumen para el año {year}:")
    print(f"Total de precipitación en {year}: {annual_stats.loc[year, 'sum']}")
    print(f"Promedio anual en {year}: {annual_stats.loc[year, 'mean']:.2f}")
    change_rate = annual_stats.loc[year, "Change_Rate"]
    print(f"Tasa de variación anual en {year}: {change_rate:.2f}%")
    print(f"Precipitación diaria máxima en {year}: {annual_stats.loc[year, 'Max_Daily']}")
    print(f"Precipitación diaria mínima en {year}: {annual_stats.loc[year, 'Min_Daily']}")

print("\n" + "-"*40)
print(f"Año más lluvioso: {most_rainy_year}, Precipitación total: {annual_stats.loc[most_rainy_year, 'sum']}")
print(f"Año más seco: {least_rainy_year}, Precipitación total: {annual_stats.loc[least_rainy_year, 'sum']}")

annual_stats.to_csv("resultados_annual_stats.csv", index=True)
with open("resultados_annual_stats.txt", "w") as f:
    f.write(annual_stats.to_string())
