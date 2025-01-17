import os
import pandas as pd

def count_values_in_file(file_path):
    """
    Cuenta las ocurrencias de '-999' y de otros números en un archivo.
    """
    count_negative_999 = 0
    count_other_numbers = 0
    data = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Dividir en valores por espacios o tabulaciones
                values = line.split()
                # Contar las ocurrencias de -999
                count_negative_999 += values.count("-999")
                # Contar todos los demás números
                count_other_numbers += sum(1 for value in values if value != "-999" and value.replace('.', '', 1).lstrip('-').isdigit())
                # Guardar valores numéricos válidos
                data.extend([float(value) for value in values if value.replace('.', '', 1).lstrip('-').isdigit()])
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")
    return count_negative_999, count_other_numbers, data


def calculate_statistics(data, file_name):
    """
    Calcula estadísticas anuales de los datos procesados.
    """
    df = pd.DataFrame(data, columns=["precipitation"])
    df['year'] = (df.index // 12) + 2006  # Asumiendo 12 registros por año

    # Calcular totales y medias anuales
    annual_stats = df.groupby('year')['precipitation'].agg(['sum', 'mean']).reset_index()
    annual_stats.columns = ['Year', 'Total Precipitation', 'Average Precipitation']

    # Calcular tendencia de cambio (diferencia entre años consecutivos)
    annual_stats['Trend'] = annual_stats['Total Precipitation'].diff()

    # Calcular extremos (año más lluvioso y más seco)
    most_rainy_year = annual_stats.loc[annual_stats['Total Precipitation'].idxmax(), 'Year']
    least_rainy_year = annual_stats.loc[annual_stats['Total Precipitation'].idxmin(), 'Year']

    # Estadísticas adicionales
    max_precipitation = df['precipitation'].max()
    min_precipitation = df['precipitation'].min()

    print(f"\nEstadísticas del archivo {file_name}:")
    print(annual_stats)
    print(f"\nAño más lluvioso: {most_rainy_year}")
    print(f"Año más seco: {least_rainy_year}")
    print(f"Máxima precipitación mensual: {max_precipitation}")
    print(f"Mínima precipitación mensual: {min_precipitation}")

    # Guardar estadísticas en un archivo CSV
    annual_stats.to_csv(f"statistics_{file_name}.csv", index=False)


def count_values_in_directory(directory_path):
    """
    Recorre todos los archivos en la ruta especificada y cuenta las ocurrencias
    de '-999' y de otros números, además calcula estadísticas.
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
                file_negative_999, file_other_numbers, file_data = count_values_in_file(file_path)
                total_negative_999 += file_negative_999
                total_other_numbers += file_other_numbers
                print(f"Ocurrencias de -999 en {file_name}: {file_negative_999}")
                print(f"Ocurrencias de otros números en {file_name}: {file_other_numbers}")

                # Calcular estadísticas del archivo
                calculate_statistics(file_data, file_name)

    print(f"\nRevisión completada.")
    print(f"Total de archivos procesados: {file_count}")
    print(f"Total de ocurrencias de -999: {total_negative_999}")
    print(f"Total de ocurrencias de otros números: {total_other_numbers}")


# Ruta del directorio donde están los archivos
directory_path = "/home/eduard.perez.7e8/Baixades/precip.prova/"
count_values_in_directory(directory_path)
