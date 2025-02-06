import os
from collections import defaultdict

def calculate_annual_precipitation(input_dir):
    """
    Calcula la precipitación total anual a partir de 16,064 archivos .dat.
    - Ignora valores inválidos (-999).
    - Procesamiento eficiente para grandes volúmenes de datos.
    """
    annual_totals = defaultdict(float)  # {año: precipitación_total}

    # Contador para verificar que se procesen 16,064 archivos
    processed_files = 0

    # Recorrer todos los archivos .dat en el directorio y subdirectorios
    for root, _, files in os.walk(input_dir):
        for file_name in files:
            if file_name.endswith(".dat"):
                file_path = os.path.join(root, file_name)
                processed_files += 1

                # Leer y procesar el archivo
                with open(file_path, "r") as file:
                    lines = file.readlines()[2:]  # Omitir cabeceras
                    
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) < 4:
                            continue  # Saltar líneas corruptas
                        
                        year = int(parts[1])
                        daily_values = parts[3:]  # Valores diarios
                        
                        # Sumar solo valores válidos
                        valid_precip = sum(
                            float(value) 
                            for value in daily_values 
                            if value not in ("-999", "-999.0")
                        )
                        
                        annual_totals[year] += valid_precip

    # Verificar número de archivos procesados
    print(f"Archivos procesados: {processed_files}/16064")

    # Calcular máximos y mínimos
    if annual_totals:
        max_year = max(annual_totals, key=annual_totals.get)
        min_year = min(annual_totals, key=annual_totals.get)
        
        # Resultados ordenados por año
        sorted_totals = sorted(annual_totals.items(), key=lambda x: x[0])
        
        print("\nPrecipitación anual (mm):")
        for year, total in sorted_totals:
            print(f"Año {year}: {total:.2f} mm")
        
        print(f"\nMáximo: Año {max_year} ({annual_totals[max_year]:.2f} mm)")
        print(f"Mínimo: Año {min_year} ({annual_totals[min_year]:.2f} mm)")
    else:
        print("No se encontraron datos válidos.")

# Ejecutar
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calculate_annual_precipitation(input_directory)