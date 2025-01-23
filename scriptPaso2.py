import os
import re
from datetime import datetime

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

            # Extraer el número del prefijo Px del nombre del archivo (por ejemplo, "P3" de "precip.P3.MIROC5...")
            file_prefix = file.split('.')[1]  # Esto debería ser "P3" o "P4", dependiendo del archivo
            expected_prefix = file_prefix[1:]  # Extraemos solo el número de "P3", "P4", etc.

            # Verificar la segunda línea
            second_line = lines[1].strip().split('\t')
            if len(second_line) != 8 or not second_line[0].startswith('P'):
                error_message = (
                    f"ERROR: {file} MOTIVO: La segunda línea no cumple el formato. "
                    f"Esperado prefijo 'P' y 8 columnas, encontrado: {len(second_line)} columnas."
                )
                log_error(error_message)
                all_valid = False

            # Verificar que el prefijo en la segunda línea coincida con el esperado
            if second_line[0][1:] != expected_prefix:
                error_message = f"ERROR: {file} MOTIVO: El prefijo en la segunda línea ({second_line[0]}) no coincide con el nombre del archivo ({file_prefix})."
                log_error(error_message)
                all_valid = False

            # Inicializar el año y el mes esperados
            expected_year = 2006
            expected_month = 1

            # Contador para resumir errores de secuencia y días inexistentes
            sequence_errors = 0
            invalid_day_errors = 0
            detailed_errors = []  # Para agrupar mensajes de errores por archivo

            # Verificar las siguientes líneas
            for i, line in enumerate(lines[2:], start=3):
                columns = line.strip().split()

                line_errors = []  # Acumulamos los errores de cada línea

                # Verificar que haya al menos 34 columnas antes de continuar
                if len(columns) < 34:
                    line_errors.append(f"Línea {i}: tiene un número insuficiente de columnas ({len(columns)}). Se esperaban 34.")
                else:
                    # Validar año y mes
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

                        # Verificar que el prefijo sea el mismo que el del archivo
                        if len(columns) > 0 and columns[0][1:] != expected_prefix:  # Comparar solo el número después de "P"
                            line_errors.append(f"Línea {i}: El prefijo ({columns[0]}) no coincide con el nombre del archivo ({file_prefix}).")

                        # Verificar que el año sea correcto y seguir el patrón cíclico
                        if not columns[1].isdigit() or not (2006 <= int(columns[1]) <= 2100):
                            line_errors.append(f"Línea {i}: El año ({columns[1]}) debe estar entre 2006 y 2100.")
                        elif int(columns[1]) != expected_year:
                            sequence_errors += 1

                        # Verificar que el mes sea correcto y seguir el patrón cíclico
                        if not columns[2].isdigit() or not (1 <= int(columns[2]) <= 12):
                            line_errors.append(f"Línea {i}: El mes ({columns[2]}) debe estar entre 1 y 12.")
                        elif int(columns[2]) != expected_month:
                            sequence_errors += 1

                        # Actualizar el año y mes esperados
                        if expected_month == 12:
                            expected_month = 1
                            expected_year += 1
                        else:
                            expected_month += 1

                        # Verificar que los valores -999 estén en días inexistentes
                        for day_index, value in enumerate(columns[3:], start=1):
                            if day_index > valid_days and value != '-999':
                                invalid_day_errors += 1
                            elif day_index <= valid_days and value == '-999':
                                # Valor -999 en días existentes no genera error para casos válidos de febrero
                                if not (month == 2 and day_index > 28 and valid_days == 29):
                                    invalid_day_errors += 1

                # Si hay errores en la línea, los agrupamos
                if line_errors:
                    detailed_errors.extend(line_errors)
                    all_valid = False

            # Resumir errores de secuencia si existen
            if sequence_errors > 0:
                detailed_errors.append(f"{sequence_errors} errores de secuencia temporal.")

            # Resumir errores de días inexistentes si existen
            if invalid_day_errors > 0:
                detailed_errors.append(f"{invalid_day_errors} valores incorrectos en días inexistentes.")

            # Registrar todos los errores agrupados
            if detailed_errors:
                log_error(f"ERROR: {file} MOTIVO: Errores detectados.")
                for error in detailed_errors:
                    log_error(f"{error}")

        except Exception as e:
            # Registrar cualquier error inesperado en el log
            error_message = f"ERROR: {file} MOTIVO: Error inesperado durante el procesamiento. Detalles: {str(e)}"
            log_error(error_message)  # No se muestra en terminal
            all_valid = False

    if not all_valid:
        print("\033[31mSe encontraron errores en uno o más archivos .dat.\033[0m")

# Cambia el directorio según sea necesario
directory = "./prueba_clima"
validate_dat_files(directory)
