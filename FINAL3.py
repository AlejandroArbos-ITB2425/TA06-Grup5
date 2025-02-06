import os
import numpy as np
from collections import defaultdict

# Constantes
AREA_ESPAÑA_KM2 = 505_990  # Área de España en km²
LITROS_POR_MM_KM2 = 1_000_000  # 1 mm de lluvia sobre 1 km² = 1,000,000 litros


def leer_datos(input_dir):
    """
    Lee los archivos .dat en el directorio dado y devuelve un diccionario con los datos de precipitación.
    Retorna:
    - annual_precip: Diccionario {año: [precipitaciones mensuales promedio]}
    - precipitacion_total: Diccionario {año: precipitación total en mm}
    - archivos_procesados: Contador de archivos leídos
    """
    annual_precip = defaultdict(list)
    precipitacion_total = defaultdict(float)
    archivos_procesados = 0

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        
        if os.path.isfile(file_path) and file_name.endswith(".dat"):
            archivos_procesados += 1
            
            with open(file_path, "r", encoding='utf-8') as file:
                lines = file.readlines()[2:]  # Omitir cabecera
            
            for line in lines:
                parts = line.split()
                if len(parts) < 4:
                    continue  # Evitar errores en líneas mal formateadas

                year = int(parts[1])
                valid_values = [float(x) / 10 for x in parts[3:] if x not in ("-999", "-999.0")]
                valid_days = len(valid_values)

                if valid_days == 0:
                    continue

                monthly_avg = sum(valid_values) / valid_days  # Media mensual considerando valores válidos
                annual_precip[year].append(monthly_avg)
                precipitacion_total[year] += sum(valid_values)

    return annual_precip, precipitacion_total, archivos_procesados


def calcular_media_anual(annual_precip):
    """Calcula la media anual de precipitación normalizada (450-900 mm) por año."""
    all_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    
    min_original = min(all_totals, key=lambda x: x[1])[1]
    max_original = max(all_totals, key=lambda x: x[1])[1]

    def normalize(value):
        return 450 + (value - min_original) / (max_original - min_original) * (900 - 450) if max_original > min_original else 450

    results = [{"Year": year, "AnnualTotal": normalize(annual_total)} for year, annual_total in all_totals]
    results.sort(key=lambda x: x["Year"])
    
    for result in results:
        print(f"Año: {result['Year']}, Media Anual: {result['AnnualTotal']:.2f} mm")
    
    max_precipitation_year = max(results, key=lambda x: x["AnnualTotal"])
    min_precipitation_year = min(results, key=lambda x: x["AnnualTotal"])
    print(f"\nEl año con más precipitación fue {max_precipitation_year['Year']} con {max_precipitation_year['AnnualTotal']:.2f} mm.")
    print(f"El año con menos precipitación fue {min_precipitation_year['Year']} con {min_precipitation_year['AnnualTotal']:.2f} mm.")


def calcular_precipitacion_litros(precipitacion_total, archivos_procesados):
    """Calcula la precipitación total anual en litros para toda España."""
    litros_anuales = {año: precip * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2 for año, precip in precipitacion_total.items()}
    
    print(f"Archivos procesados: {archivos_procesados}")
    print("\nPrecipitación Total Anual:")
    for año, litros in sorted(litros_anuales.items()):
        print(f"Año {año}: {litros:.2e} L")
    
    if litros_anuales:
        max_año, max_val = max(litros_anuales.items(), key=lambda x: x[1])
        min_año, min_val = min(litros_anuales.items(), key=lambda x: x[1])
        print(f"\nEl año con más precipitación fue {max_año} con {max_val:.2e} L")
        print(f"El año con menos precipitación fue {min_año} con {min_val:.2e} L")


def calcular_tasa_variacion(annual_precip):
    """Calcula la tasa de variación anual de la precipitación normalizada."""
    all_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    min_original = min(all_totals, key=lambda x: x[1])[1]
    max_original = max(all_totals, key=lambda x: x[1])[1]
    
    normalize = lambda value: 450 + (value - min_original) * 450 / (max_original - min_original) if max_original != min_original else 450
    sorted_totals = sorted([(year, normalize(total)) for year, total in all_totals], key=lambda x: x[0])
    
    tasas_variacion = {sorted_totals[i][0]: ((sorted_totals[i][1] - sorted_totals[i-1][1]) / sorted_totals[i-1][1]) * 100 for i in range(1, len(sorted_totals))}
    
    print("\nTasas de variación anual (%):")
    for año, tasa in tasas_variacion.items():
        print(f"Año {año}: {tasa:.2f}%")


# Directorio de datos
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"

# Ejecutar funciones
annual_precip, precipitacion_total, archivos_procesados = leer_datos(input_directory)
calcular_media_anual(annual_precip)
calcular_precipitacion_litros(precipitacion_total, archivos_procesados)
calcular_tasa_variacion(annual_precip)
