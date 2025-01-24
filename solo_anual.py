import os

def calculate_annual_precipitation(input_dir):
    """
    Calcula la media anual de precipitación para todas las estaciones meteorológicas combinadas,
    y determina el año con mayor y menor precipitación.

    Args:
        input_dir (str): Directorio donde se encuentran los archivos.
    """
    # Crear un diccionario para almacenar los resultados anuales
    annual_totals = {}
    annual_days = {}

    # Variables para llevar el registro del año con más y menos precipitación
    max_precip_year = None
    max_precip = float('-inf')
    min_precip_year = None
    min_precip = float('inf')

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
            for line in data_lines:
                parts = line.split()

                # Extraer información de la fila
                year = int(parts[1])
                precipitation = [float(x) for x in parts[3:] if x != "-999"]

                # Actualizar los totales y conteos anuales
                if year not in annual_totals:
                    annual_totals[year] = 0.0
                    annual_days[year] = 0

                annual_totals[year] += sum(precipitation)
                annual_days[year] += len(precipitation)

    # Calcular la media anual para cada año
    for year in sorted(annual_totals.keys()):
        if annual_days[year] > 0:
            annual_mean = annual_totals[year] / annual_days[year]
            print(f"{year}: {annual_mean:.2f}")

            # Actualizar el año con mayor y menor precipitación
            if annual_mean > max_precip:
                max_precip = annual_mean
                max_precip_year = year
            if annual_mean < min_precip:
                min_precip = annual_mean
                min_precip_year = year

    # Mostrar los resultados del año con más y menos precipitación
    print(f"\nAño con más precipitación: {max_precip_year} ({max_precip:.2f} mm)")
    print(f"Año con menos precipitación: {min_precip_year} ({min_precip:.2f} mm)")

# Configuración
input_directory = "./PROVA"

# Ejecutar la función
calculate_annual_precipitation(input_directory)