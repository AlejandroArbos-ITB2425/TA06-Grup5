import os
import re
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import csv

# ------------------------------
# CÓDIGO 1: Validación de archivos .dat y cálculo de -999
# ------------------------------
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
    """Valida que los archivos .dat cumplan con el formato especificado."""
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
                error_message = f"ERROR: {file} MOTIVO: La segunda línea no cumple el formato."
                log_error(error_message)
                all_valid = False

            if second_line[0][1:] != expected_prefix:
                error_message = f"ERROR: {file} MOTIVO: El prefijo no coincide con el nombre del archivo."
                log_error(error_message)
                all_valid = False

            expected_year = 2006
            expected_month = 1
            sequence_errors = 0
            invalid_day_errors = 0
            detailed_errors = []

            for i, line in enumerate(lines[2:], start=3):
                columns = line.strip().split()
                line_errors = []

                if len(columns) < 34:
                    line_errors.append(f"Línea {i}: Columnas insuficientes.")
                else:
                    try:
                        year = int(columns[1])
                        month = int(columns[2])
                    except (ValueError, IndexError):
                        line_errors.append(f"Línea {i}: Error en año/mes.")
                        year, month = None, None

                    if year is not None and month is not None:
                        valid_days = get_days_in_month(year, month)

                        if len(columns) > 0 and columns[0][1:] != expected_prefix:
                            line_errors.append(f"Línea {i}: Prefijo incorrecto.")

                        if not columns[1].isdigit() or not (2006 <= int(columns[1]) <= 2100):
                            line_errors.append(f"Línea {i}: Año fuera de rango.")
                        elif int(columns[1]) != expected_year:
                            sequence_errors += 1

                        if not columns[2].isdigit() or not (1 <= int(columns[2]) <= 12):
                            line_errors.append(f"Línea {i}: Mes inválido.")
                        elif int(columns[2]) != expected_month:
                            sequence_errors += 1

                        if expected_month == 12:
                            expected_month = 1
                            expected_year += 1
                        else:
                            expected_month += 1

                        for day_index, value in enumerate(columns[3:], start=1):
                            if day_index > valid_days and value != '-999':
                                invalid_day_errors += 1
                            elif day_index <= valid_days and value == '-999':
                                if not (month == 2 and day_index > 28 and valid_days == 29):
                                    invalid_day_errors += 1

                if line_errors:
                    detailed_errors.extend(line_errors)
                    all_valid = False

            if sequence_errors > 0:
                detailed_errors.append(f"{sequence_errors} errores de secuencia.")
            if invalid_day_errors > 0:
                detailed_errors.append(f"{invalid_day_errors} días inválidos.")

            if detailed_errors:
                log_error(f"ERROR: {file} MOTIVO: Errores detectados.")
                for error in detailed_errors:
                    log_error(f"{error}")

        except Exception as e:
            error_message = f"ERROR: {file} MOTIVO: Error inesperado. Detalles: {str(e)}"
            log_error(error_message)
            all_valid = False

    if not all_valid:
        print("\033[31mSe encontraron errores en los archivos .dat.\033[0m")
    else:
        print("\033[32mValidación exitosa: Todos los archivos son válidos.\033[0m")

def count_values_in_file(file_path):
    """Cuenta -999 y otros valores en un archivo."""
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
    """Calcula el porcentaje de una parte respecto al total."""
    return (part / total * 100) if total > 0 else 0

def count_values_in_directory(directory_path):
    """Calcula estadísticas de -999 en el directorio."""
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
    print(f"Archivos procesados: {file_count}")
    print(f"Total de -999: {total_negative_999}")
    print(f"Otros valores: {total_other_numbers}")
    print(f"Porcentaje de -999: {percentage_negative_999:.2f}%")

    return percentage_negative_999

# ------------------------------
# CÓDIGO 2: Cálculos de precipitación y CSV
# ------------------------------
def calculate_annual_precipitation(input_dir):
    results = []
    annual_precip = {}

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if file_name.endswith(".dat"):
            with open(file_path, "r") as file:
                lines = file.readlines()[2:]
                for line in lines:
                    parts = line.split()
                    if len(parts) < 4:
                        continue
                    year = int(parts[1])
                    valid_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]
                    valid_days = len(valid_values)
                    if valid_days == 0:
                        continue
                    monthly_precip = sum(valid_values) / valid_days
                    if year not in annual_precip:
                        annual_precip[year] = []
                    annual_precip[year].append(monthly_precip)

    all_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    min_original = min(all_totals, key=lambda x: x[1])[1]
    max_original = max(all_totals, key=lambda x: x[1])[1]
    
    normalize = lambda value: 450 + (value - min_original) / (max_original - min_original) * 450 if max_original > min_original else 450
    
    max_precipitation = float('-inf')
    min_precipitation = float('inf')
    max_precipitation_year = None
    min_precipitation_year = None
    results = []
    for year, annual_total in all_totals:
        adjusted_total = normalize(annual_total)
        results.append({"Year": year, "AnnualTotal": adjusted_total})
        if adjusted_total > max_precipitation:
            max_precipitation = adjusted_total
            max_precipitation_year = year
        if adjusted_total < min_precipitation:
            min_precipitation = adjusted_total
            min_precipitation_year = year

    results.sort(key=lambda x: x["Year"])

    years = [result["Year"] for result in results]
    annual_totals = [result["AnnualTotal"] for result in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(years, annual_totals, marker='o', color='b', label='Media Anual')
    plt.title("Media Anual de Precipitación")
    plt.xlabel("Año")
    plt.ylabel("Precipitación Media (mm)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    print("\nMedia Anual de Precipitación:")
    for result in results:
        print(f"Año: {result['Year']}, Media Anual: {result['AnnualTotal']:.2f} mm")
    print(f"\nEl año más lluvioso fue: {max_precipitation_year} ({max_precipitation:.2f} mm)")
    print(f"El año más seco és: {min_precipitation_year} ({min_precipitation:.2f} mm)")
    
    return results

AREA_ESPAÑA_KM2 = 505_990
LITROS_POR_MM_KM2 = 1_000_000

def calcular_precipitacion_litros_españa(input_dir):
    precipitacion_anual = defaultdict(float)
    for raiz, _, archivos in os.walk(input_dir):
        for nombre_archivo in archivos:
            if nombre_archivo.endswith(".dat"):
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                with open(ruta_archivo, "r", encoding='utf-8') as archivo:
                    lineas = archivo.readlines()[2:]
                    for linea in lineas:
                        partes = linea.strip().split()
                        if len(partes) < 4:
                            continue
                        año = int(partes[1])
                        valores_diarios = partes[3:]
                        suma_mes = sum(
                            float(valor) / 10 
                            for valor in valores_diarios 
                            if valor not in ("-999", "-999.0")
                        )
                        precipitacion_anual[año] += suma_mes
    
    litros_anuales = {año: precipitacion * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2 for año, precipitacion in precipitacion_anual.items()}
    años_ordenados = sorted(litros_anuales.items())
    
    años = [año for año, _ in años_ordenados]
    litros = [litros for _, litros in años_ordenados]
    
    plt.figure(figsize=(10, 6))
    plt.bar(años, litros, color='g')
    plt.title("Precipitación Total Anual en España")
    plt.xlabel("Año")
    plt.ylabel("Litros de Precipitación Total")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    print("\nPrecipitación Total Anual en España:")
    for año, litros in años_ordenados:
        print(f"Año {año}: {litros:.2e} L")
    if años_ordenados:
        año_max, maximo = max(años_ordenados, key=lambda x: x[1])
        año_min, minimo = min(años_ordenados, key=lambda x: x[1])
        print(f"\nEl año más lluvioso fue: {año_max} ({maximo:.2e} L)")
        print(f"El año más seco és: {año_min} ({minimo:.2e} L)")
    
    return años_ordenados

def calcular_tasa_variacion_anual(input_dir):
    annual_precip = {}
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".dat"):
            file_path = os.path.join(input_dir, file_name)
            with open(file_path, "r") as file:
                lines = file.readlines()[2:]
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) < 4:
                        continue
                    year = int(parts[1])
                    valid_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]
                    valid_days = len(valid_values)
                    if valid_days == 0:
                        continue
                    monthly_avg = sum(valid_values) / valid_days
                    if year not in annual_precip:
                        annual_precip[year] = []
                    annual_precip[year].append(monthly_avg)

    annual_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    min_original = min(annual_totals, key=lambda x: x[1])[1]
    max_original = max(annual_totals, key=lambda x: x[1])[1]
    normalize = lambda value: 450 + (value - min_original) * 450 / (max_original - min_original) if max_original != min_original else 450
    sorted_totals = sorted([(year, normalize(total)) for year, total in annual_totals], key=lambda x: x[0])
    
    tasas_variacion = {}
    for i in range(1, len(sorted_totals)):
        año_actual, total_actual = sorted_totals[i]
        año_anterior, total_anterior = sorted_totals[i-1]
        tasa = ((total_actual - total_anterior) / total_anterior) * 100
        tasas_variacion[año_actual] = tasa
    
    años = list(tasas_variacion.keys())
    tasas = list(tasas_variacion.values())
    
    plt.figure(figsize=(10, 6))
    plt.plot(años, tasas, marker='s', color='r', label='Tasa de Variación Anual')
    plt.title("Tasa de Variación Anual de Precipitación")
    plt.xlabel("Año")
    plt.ylabel("Tasa de Variación (%)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    print("\nTasas de Variación Anual (%):")
    for año, tasa in tasas_variacion.items():
        print(f"Año {año}: {tasa:.2f}%")
    
    return tasas_variacion

# ------------------------------
# Ejecución secuencial de ambos códigos
# ------------------------------
if __name__ == "__main__":
    # Ejecutar validación y conteo de -999 (CÓDIGO1)
    directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
    validate_dat_files(directory)
    count_values_in_directory(directory)
    
    # Ejecutar cálculos de precipitación y generar CSV (CÓDIGO2)
    input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
    annual_media = calculate_annual_precipitation(input_directory)
    litros_anuales = calcular_precipitacion_litros_españa(input_directory)
    tasas_variacion = calcular_tasa_variacion_anual(input_directory)
    
    # Generar CSV
    media_dict = {item['Year']: item['AnnualTotal'] for item in annual_media}
    litros_dict = dict(litros_anuales)
    tasa_dict = tasas_variacion
    
    csv_rows = []
    for year in sorted(media_dict.keys()):
        media = media_dict.get(year, None)
        litros = litros_dict.get(year, None)
        tasa = tasa_dict.get(year, None)
        
        csv_rows.append([
            year,
            f"{media:.2f}" if media is not None else '',
            f"{litros:.2e}" if litros is not None else '',
            f"{tasa:.2f}" if tasa is not None else ''
        ])
    
    with open('estadisticas.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['Año', 'Media_Anual', 'Total_Anual', 'Tasa_Variación'])
        writer.writerows(csv_rows)
    
    print("\nArchivo CSV creado: 'estadisticas.csv'")