import os
from datetime import datetime


def check_file_format(file_path):
    try:
        with open(file_path, 'r') as file:
            # Leer solo la primera línea
            first_line = file.readline().strip()

        # Verificar la cabecera (primera línea)
        header = first_line.split("\t")
        if len(header) != 6:
            return False, f"Error en la cabecera: {file_path}"

        return True, None
    except Exception as e:
        return False, f"Error al leer el archivo {file_path}: {e}"


def log_incidences(incident_message):
    # Obtener la fecha y hora actuales
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Formatear el mensaje de log con la fecha y hora
    log_message = f"{current_time} - {incident_message}"

    # Escribir el mensaje en el archivo log
    with open("incidencias.log", "a") as log_file:
        log_file.write(log_message + "\n")


def check_files_in_directory(directory_path):
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
    for file_name in files:
        file_path = os.path.join(directory_path, file_name)
        valid, error = check_file_format(file_path)
        if not valid:
            print(f"Archivo con formato incorrecto: {file_name}")
            print(f"Motivo: {error}")
            log_incidences(f"Archivo: {file_name} - {error}")
        else:
            print(f"Archivo válido: {file_name}")

    print("Revisión completada. Las incidencias se han registrado en incidencias.log.")


# Ruta del directorio donde están los archivos
directory_path = "/home/aleix.parise.7e8/Baixades/ficheroclima_bakup/"
check_files_in_directory(directory_path)
