import os
import numpy as np

def calculate_annual_precipitation(input_dir):
    """
    Calcula la media anual y la precipitación total de cada año, determina el año con más y menos precipitación,
    y calcula la tasa de variación anual de la precipitación media.
    
    Args:
        input_dir (str): Directorio donde se encuentran los archivos.
    """
    # Crear una lista para almacenar los resultados
    results = []
    
    # Variables para almacenar el año con más y menos precipitación
    max_precipitation_year = None
    min_precipitation_year = None
    max_precipitation = float('-inf')
    min_precipitation = float('inf')

    # Diccionario para almacenar la precipitación anual por año
    annual_precip = {}

    # Iterar sobre cada archivo en el directorio
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)

        # Comprobar que es un archivo válido
        if os.path.isfile(file_path) and file_name.endswith(".dat"):
            with open(file_path, "r") as file:
                lines = file.readlines()

            # Ignorar las dos primeras filas (cabecera del archivo)
            data_lines = lines[2:]

            # Procesar cada fila (mes)
            for line in data_lines:
                parts = line.split()

                # Extraer información de la fila
                station_id = parts[0]  # Ejemplo: P3, P4...
                year = int(parts[1])
                month = int(parts[2])

                # Filtrar y verificar las precipitaciones válidas
                precipitation_values = [float(x) for x in parts[3:] if x != "-999" and x != "-999.0"]
                
                if not precipitation_values:
                    continue  # Si no hay precipitaciones válidas, saltamos esta línea

                precipitation = np.array(precipitation_values)

                # Si no hay datos para el año, inicializar
                if year not in annual_precip:
                    annual_precip[year] = []

                # Añadir la precipitación mensual al total del año
                annual_precip[year].append(precipitation.sum())

    # Calcular la media anual y la suma total por año
    for year, monthly_precip in annual_precip.items():
        annual_mean = sum(monthly_precip) / len(monthly_precip)  # Media anual
        annual_total = sum(monthly_precip)  # Precipitación total anual
        results.append({"Year": year, "AnnualMean": annual_mean, "AnnualTotal": annual_total})

        # Verificar el año con más y menos precipitación
        if annual_total > max_precipitation:
            max_precipitation = annual_total
            max_precipitation_year = year

        if annual_total < min_precipitation:
            min_precipitation = annual_total
            min_precipitation_year = year

    # Ordenar los resultados por año para asegurar una presentación cronológica
    results.sort(key=lambda x: x["Year"])

    # Mostrar los resultados por pantalla
    for result in results:
        print(f"Año: {result['Year']}, Media Anual de Precipitación: {result['AnnualMean']:.2f}, Total Anual: {result['AnnualTotal']:.2f}")

    # Calcular la tasa de variación anual de la media de precipitaciones
    prev_year_mean = None
    print("\nTasa de variación anual de la precipitación media:")
    for result in results:
        year = result["Year"]
        annual_mean = result["AnnualMean"]
        if prev_year_mean is not None:
            variation_rate = ((annual_mean - prev_year_mean) / prev_year_mean) * 100
            print(f"Año: {year}, Tasa de variación anual: {variation_rate:.2f}%")
        prev_year_mean = annual_mean

    # Mostrar el año con más y menos precipitación al final
    print(f"\nEl año con más precipitación fue {max_precipitation_year} con {max_precipitation:.2f} mm.")
    print(f"El año con menos precipitación fue {min_precipitation_year} con {min_precipitation:.2f} mm.")

# Configuración
input_directory = "./PROVA"

# Ejecutar la función
calculate_annual_precipitation(input_directory)
