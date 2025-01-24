import os
import re
from datetime import datetime
import numpy as np

def log_error(message, is_terminal=False):
    """Guarda el mensaje de error en el archivo errores.log y muestra en terminal si es necesario."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"{timestamp}: {message}"
    with open("errores.log", "a") as log_file:
        log_file.write(formatted_message + "\n")

    # Mostrar en terminal si es necesario (con color rojo para errores)
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

    # Comprobamos si hay archivos que no son .dat
    non_dat_files = [f for f in files if not f.endswith('.dat')]
    if non_dat_files:
        for file in non_dat_files:
            error_message = f"ERROR: {file} MOTIVO: No es un archivo .dat."
            log_error(error_message)
            all_valid = False

    # Filtramos solo los archivos .dat
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

            # Verificar la cabecera
            header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
            if not lines[0].strip() == header:
                error_message = f"ERROR: {file} MOTIVO: La cabecera no coincide con el formato esperado."
                log_error(error_message)
                all_valid = False

            file_prefix = file.split('.')[1]  # Esto debería ser "P3" o "P4", dependiendo del archivo
            expected_prefix = file_prefix[1:]  # Extraemos solo el número de "P3", "P4", etc.

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

            expected_year = 2006
            expected_month = 1
            sequence_errors = 0
            invalid_day_errors = 0
            detailed_errors = []

            for i, line in enumerate(lines[2:], start=3):
                columns = line.strip().split()

                line_errors = []

                if len(columns) < 34:
                    line_errors.append(f"Línea {i}: tiene un número insuficiente de columnas ({len(columns)}). Se esperaban 34.")
                else:
                    try:
                        year = int(columns[1])
                    except (ValueError, IndexError):
                        line_errors.append(f"Línea {i}: El año ({columns[1] if len(columns) > 1 else 'N/A'}) no es un valor numérico válido o está ausente.")
                        year = None

                    try:
                        month = int(columns[2])
                    except (ValueError, IndexError):
                        line_errors.append(f"Línea {i}: El mes ({columns[2] if len(columns) > 2 else 'N/A'}) no es un valor numérico válido o está ausente.")
                        month = None

                    if year is not None and month is not None:
                        valid_days = get_days_in_month(year, month)

                        if len(columns) > 0 and columns[0][1:] != expected_prefix:
                            line_errors.append(f"Línea {i}: El prefijo ({columns[0]}) no coincide con el nombre del archivo ({file_prefix}).")

                        if not columns[1].isdigit() or not (2006 <= int(columns[1]) <= 2100):
                            line_errors.append(f"Línea {i}: El año ({columns[1]}) debe estar entre 2006 y 2100.")
                        elif int(columns[1]) != expected_year:
                            sequence_errors += 1

                        if not columns[2].isdigit() or not (1 <= int(columns[2]) <= 12):
                            line_errors.append(f"Línea {i}: El mes ({columns[2]}) debe estar entre 1 y 12.")
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
                detailed_errors.append(f"{sequence_errors} errores de secuencia temporal.")

            if invalid_day_errors > 0:
                detailed_errors.append(f"{invalid_day_errors} valores incorrectos en días inexistentes.")

            if detailed_errors:
                log_error(f"ERROR: {file} MOTIVO: Errores detectados.")
                for error in detailed_errors:
                    log_error(f"{error}")

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
    """
    Cuenta las ocurrencias de '-999' y de otros números en un archivo,
    ignorando las dos primeras filas y las tres primeras columnas de cada fila.
    """
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
    """
    Calcula el porcentaje de una parte respecto al total.
    """
    return (part / total * 100) if total > 0 else 0

def count_values_in_directory(directory_path):
    """
    Recorre todos los archivos en la ruta especificada y cuenta las ocurrencias
    de '-999' y de otros números, ignorando las dos primeras filas y las tres primeras columnas.
    Calcula el porcentaje de '-999'.
    """
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
    print(f"Total de valores: {total_values}")
    print(f"Porcentaje de -999 respecto al total: {percentage_negative_999:.2f}%")

    return percentage_negative_999

count_values_in_directory(directory)

# Tercera parte: Calcular la precipitación
# Función para calcular la media anual de precipitación para todas las estaciones meteorológicas combinadas
def calculate_annual_precipitation_combined(input_dir):
    """
    Calcula la media anual de precipitación para todas las estaciones meteorológicas combinadas,
    y determina el año con mayor y menor precipitación.

    Args:
        input_dir (str): Directorio donde se encuentran los archivos.
    """
    annual_totals = {}
    annual_days = {}

    max_precip_year = None
    max_precip = float('-inf')
    min_precip_year = None
    min_precip = float('inf')

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        if os.path.isfile(file_path) and file_name.endswith(".dat"):
            with open(file_path, "r") as file:
                lines = file.readlines()

            data_lines = lines[2:]

            for line in data_lines:
                parts = line.split()
                year = int(parts[1])
                precipitation = [float(x) for x in parts[3:] if x != "-999"]

                if year not in annual_totals:
                    annual_totals[year] = 0.0
                    annual_days[year] = 0

                annual_totals[year] += sum(precipitation)
                annual_days[year] += len(precipitation)

    for year in sorted(annual_totals.keys()):
        if annual_days[year] > 0:
            annual_mean = annual_totals[year] / annual_days[year]
            print(f"{year}: {annual_mean:.2f}")

            if annual_mean > max_precip:
                max_precip = annual_mean
                max_precip_year = year
            if annual_mean < min_precip:
                min_precip = annual_mean
                min_precip_year = year

    print(f"\nAño con más precipitación: {max_precip_year} ({max_precip:.2f} mm)")
    print(f"Año con menos precipitación: {min_precip_year} ({min_precip:.2f} mm)")

# Función para calcular la media anual de precipitación por año y estación
def calculate_annual_precipitation_separated(input_dir):
    """
    Calcula la media anual de precipitación de cada año y determina el año con mayor y menor precipitación.

    Args:
        input_dir (str): Directorio donde se encuentran los archivos.
    """
    results = []
    max_precipitation_year = None
    min_precipitation_year = None
    max_precipitation = float('-inf')
    min_precipitation = float('inf')

    annual_precip = {}

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        if os.path.isfile(file_path) and file_name.endswith(".dat"):
            with open(file_path, "r") as file:
                lines = file.readlines()

            data_lines = lines[2:]

            for line in data_lines:
                parts = line.split()
                station_id = parts[0]
                year = int(parts[1])

                precipitation_values = [float(x) for x in parts[3:] if x != "-999" and x != "-999.0"]

                if not precipitation_values:
                    continue

                precipitation = np.array(precipitation_values)

                if year not in annual_precip:
                    annual_precip[year] = []

                annual_precip[year].append(precipitation.sum())

    for year, monthly_precip in annual_precip.items():
        annual_mean = sum(monthly_precip) / len(monthly_precip)
        results.append({"Year": year, "AnnualMean": annual_mean})

        if annual_mean > max_precipitation:
            max_precipitation = annual_mean
            max_precipitation_year = year

        if annual_mean < min_precipitation:
            min_precipitation = annual_mean
            min_precipitation_year = year

    results.sort(key=lambda x: x["Year"])

    for result in results:
        print(f"Año: {result['Year']}, Total Anual: {result['AnnualMean']:.2f}")

    print(f"\nEl año con más precipitación fue {max_precipitation_year} con {max_precipitation:.2f} mm.")
    print(f"El año con menos precipitación fue {min_precipitation_year} con {min_precipitation:.2f} mm.")

def main():
    input_directory_1 = "./PROVA"
    input_directory_2 = "./PROVA"

    print("=== Calcular precipitación combinada de todas las estaciones ===")
    calculate_annual_precipitation_combined(input_directory_1)

    print("\n=== Calcular precipitación por estación ===")
    calculate_annual_precipitation_separated(input_directory_2)

if __name__ == "__main__":
    main()