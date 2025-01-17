import os

def count_values_in_file(file_path):
    """
    Cuenta las ocurrencias de '-999' y de otros números en un archivo.
    """
    count_negative_999 = 0
    count_other_numbers = 0
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Dividir en valores por espacios o tabulaciones
                values = line.split()
                # Contar las ocurrencias de -999
                count_negative_999 += values.count("-999")
                # Contar todos los demás números
                count_other_numbers += sum(1 for value in values if value != "-999" and value.replace('.', '', 1).lstrip('-').isdigit())
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")
    return count_negative_999, count_other_numbers


def count_values_in_directory(directory_path):
    """
    Recorre todos los archivos en la ruta especificada y cuenta las ocurrencias
    de '-999' y de otros números.
    """
    total_negative_999 = 0
    total_other_numbers = 0
    file_count = 0

    for root, _, files in os.walk(directory_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.isfile(file_path):  # Asegurarse de que es un archivo
                file_count += 1
                print(f"Procesando archivo: {file_name}")
                file_negative_999, file_other_numbers = count_values_in_file(file_path)
                total_negative_999 += file_negative_999
                total_other_numbers += file_other_numbers
                print(f"Ocurrencias de -999 en {file_name}: {file_negative_999}")
                print(f"Ocurrencias de otros números en {file_name}: {file_other_numbers}")

    print(f"\nRevisión completada.")
    print(f"Total de archivos procesados: {file_count}")
    print(f"Total de ocurrencias de -999: {total_negative_999}")
    print(f"Total de ocurrencias de otros números: {total_other_numbers}")


# Ruta del directorio donde están los archivos
directory_path = "/home/aleix.parise.7e8/Baixades/ficheroclima_bakup/"
count_values_in_directory(directory_path)
