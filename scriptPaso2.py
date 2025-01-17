import os
import re
from datetime import datetime

def log_error(message, is_terminal=False):
    """Guarda el mensaje de error en el archivo errores.log y muestra en terminal si es necesario."""
    with open("errores.log", "a") as log_file:
        log_file.write(message + "\n")

    # Mostrar en terminal si es necesario (con color verde)
    if is_terminal:
        print(f"\033[32m{message}\033[0m")

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

    # Agregar la fecha y hora al inicio de la ejecución
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_error(f"\nEjecución iniciada: {current_time}\n{'-' * 50}")

    all_valid = True

    # Comprobamos si hay archivos que no son .dat
    non_dat_files = [f for f in files if not f.endswith('.dat')]
    if non_dat_files:
        for file in non_dat_files:
            error_message = f"Error: El archivo {file} no es un archivo .dat."
            log_error(error_message)
            all_valid = False

    # Filtramos solo los archivos .dat
    files = [f for f in files if f.endswith('.dat')]

    if not files:
        log_error("No se encontraron archivos .dat en el directorio.", is_terminal=True)
        return

    for file in files:
        file_path = os.path.join(directory, file)

        with open(file_path, 'r') as f:
            lines = f.readlines()

        # Verificar la cabecera
        header = "precip\tMIROC5\tRCP60\tREGRESION\tdecimas\t1"
        if not lines[0].strip() == header:
            error_message = f"Error: La cabecera del archivo {file} no coincide con el formato esperado."
            log_error(error_message)
            all_valid = False
            continue

        # Verificar la segunda línea
        second_line = lines[1].strip().split('\t')
        if len(second_line) != 8 or not second_line[0].startswith('P'):
            error_message = f"Error: La segunda línea del archivo {file} no cumple el formato."
            log_error(error_message)
            all_valid = False
            continue

        # Extraer el número del prefijo Px del nombre del archivo (por ejemplo, "P3" de "precip.P3.MIROC5...")
        file_prefix = file.split('.')[1]  # Esto debería ser "P3" o "P4", dependiendo del archivo
        expected_prefix = file_prefix[1:]  # Extraemos solo el número de "P3", "P4", etc.

        # Inicializar el año y el mes esperados
        expected_year = 2006
        expected_month = 1

        # Verificar las siguientes líneas
        for i, line in enumerate(lines[2:], start=3):
            columns = line.strip().split()

            line_errors = []  # Acumulamos los errores de cada línea

            # Verificar que haya 34 columnas
            if len(columns) != 34:
                line_errors.append(f"tiene un número incorrecto de columnas ({len(columns)}).")

            # Verificar que el prefijo sea el mismo que el del archivo
            if columns[0][1:] != expected_prefix:  # Comparar solo el número después de "P"
                line_errors.append(f"tiene un prefijo ({columns[0]}) que no coincide con el nombre del archivo ({file_prefix}).")

            # Verificar que el año sea correcto y seguir el patrón cíclico
            if not columns[1].isdigit() or not (2006 <= int(columns[1]) <= 2100):
                line_errors.append(f"tiene un año inválido ({columns[1]}). Debe estar entre 2006 y 2100.")
            elif int(columns[1]) != expected_year:
                line_errors.append(f"el año esperado era {expected_year}, pero se encontró {columns[1]}.")

            # Verificar que el mes sea correcto y seguir el patrón cíclico
            if not columns[2].isdigit() or not (1 <= int(columns[2]) <= 12):
                line_errors.append(f"tiene un mes inválido ({columns[2]}). Debe estar entre 1 y 12.")
            elif int(columns[2]) != expected_month:
                line_errors.append(f"el mes esperado era {expected_month}, pero se encontró {columns[2]}.")

            # Verificar que los demás valores sean números, y que no haya símbolos no permitidos
            for value in columns[3:]:
                if value != '-999':  # El valor -999 es permitido
                    if not re.match(r"^\d+(\.\d+)?$", value):  # Aceptar solo números, con decimales
                        line_errors.append(f"contiene un valor no numérico o inválido: {value}.")
                        break

            # Si hay errores en la línea, los guardamos en el archivo
            if line_errors:
                error_message = f"Errores en la línea {i} del archivo {file}:"
                log_error(error_message)  # Guardamos la cabecera de los errores de la línea
                for error in line_errors:
                    log_error(f"  - {error}")  # Guardamos cada error individual
                all_valid = False

            # Actualizar el mes y el año esperados para la siguiente fila
            expected_month += 1
            if expected_month > 12:  # Si se supera el mes 12, reiniciar el mes y avanzar el año
                expected_month = 1
                expected_year += 1

    if all_valid:
        log_error("Todos los archivos .dat cumplen con el formato especificado.", is_terminal=True)
    else:
        log_error("Se encontraron errores en uno o más archivos .dat.", is_terminal=True)

# Cambia el directorio según sea necesario
directory = "./pruebas_clima"
validate_dat_files(directory)
