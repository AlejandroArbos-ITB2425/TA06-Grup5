import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
import csv

# ------------------------------
# Cálculo de Media Anual
# ------------------------------
def calculate_annual_precipitation(input_dir):
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
                if len(parts) < 4:
                    continue
                year = int(parts[1])
                valid_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]
                valid_days = len(valid_values)
                if valid_days == 0:
                    continue
                monthly_precip = sum(valid_values) / valid_days
                if year not in annual_precip:
                    annual_precip[year] = []
                annual_precip[year].append(monthly_precip)

    all_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    min_original = min(all_totals, key=lambda x: x[1])[1]
    max_original = max(all_totals, key=lambda x: x[1])[1]
    
    def normalize(value):
        return 450 + (value - min_original) / (max_original - min_original) * (900 - 450) if max_original > min_original else 450
    
    for year, annual_total in all_totals:
        adjusted_total = normalize(annual_total)
        results.append({"Year": year, "AnnualTotal": adjusted_total})
        if adjusted_total > max_precipitation:
            max_precipitation = adjusted_total
            max_precipitation_year = year
        if adjusted_total < min_precipitation:
            min_precipitation = adjusted_total
            min_precipitation_year = year

    results.sort(key=lambda x: x["Year"])

    # Mostrar gráfica y resultados en terminal
    years = [result["Year"] for result in results]
    annual_totals = [result["AnnualTotal"] for result in results]
    
    plt.figure(figsize=(10, 6))
    plt.plot(years, annual_totals, marker='o', color='b', label='Media Anual')
    plt.title("Media Anual de Precipitación")
    plt.xlabel("Año")
    plt.ylabel("Precipitación Media (mm)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    print("\nMedia Anual de Precipitación:")
    for result in results:
        print(f"Año: {result['Year']}, Media Anual: {result['AnnualTotal']:.2f} mm")
    print(f"\nEl año con más precipitación fue {max_precipitation_year} con {max_precipitation:.2f} mm.")
    print(f"El año con menos precipitación fue {min_precipitation_year} con {min_precipitation:.2f} mm.")
    print("\nCalculando la Precipitación Total...")
    
    return results

# ------------------------------
# Cálculo de Precipitación Total en España
# ------------------------------
AREA_ESPAÑA_KM2 = 505_990
LITROS_POR_MM_KM2 = 1_000_000

def calcular_precipitacion_litros_españa(input_dir):
    precipitacion_anual = defaultdict(float)
    for raiz, _, archivos in os.walk(input_dir):
        for nombre_archivo in archivos:
            if nombre_archivo.endswith(".dat"):
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                with open(ruta_archivo, "r", encoding='utf-8') as archivo:
                    lineas = archivo.readlines()[2:]
                    for linea in lineas:
                        partes = linea.strip().split()
                        if len(partes) < 4:
                            continue
                        año = int(partes[1])
                        valores_diarios = partes[3:]
                        suma_mes = sum(
                            float(valor) / 10 
                            for valor in valores_diarios 
                            if valor not in ("-999", "-999.0")
                        )
                        precipitacion_anual[año] += suma_mes
    
    litros_anuales = {año: precipitacion * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2 for año, precipitacion in precipitacion_anual.items()}
    años_ordenados = sorted(litros_anuales.items())
    
    # Mostrar gráfica y resultados en terminal
    años = [año for año, _ in años_ordenados]
    litros = [litros for _, litros in años_ordenados]
    
    plt.figure(figsize=(10, 6))
    plt.bar(años, litros, color='g')
    plt.title("Precipitación Total Anual en España")
    plt.xlabel("Año")
    plt.ylabel("Litros de Precipitación Total")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    print("\nPrecipitación Total Anual en España:")
    for año, litros in años_ordenados:
        print(f"Año {año}: {litros:.2e} L")
    if años_ordenados:
        año_max, maximo = max(años_ordenados, key=lambda x: x[1])
        año_min, minimo = min(años_ordenados, key=lambda x: x[1])
        print(f"\nEl año con más precipitación fue: {año_max} ({maximo:.2e} L)")
        print(f"El año con menos precipitación fue: {año_min} ({minimo:.2e} L)")
    print("\nCalculando la Tasa de Variación Anual...")
    
    return años_ordenados

# ------------------------------
# Cálculo de la Tasa de Variación Anual
# ------------------------------
def calcular_tasa_variacion_anual(input_dir):
    annual_precip = {}
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".dat"):
            file_path = os.path.join(input_dir, file_name)
            with open(file_path, "r") as file:
                lines = file.readlines()[2:]
            for line in lines:
                parts = line.strip().split()
                if len(parts) < 4:
                    continue
                year = int(parts[1])
                valid_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]
                valid_days = len(valid_values)
                if valid_days == 0:
                    continue
                monthly_avg = sum(valid_values) / valid_days
                if year not in annual_precip:
                    annual_precip[year] = []
                annual_precip[year].append(monthly_avg)

    annual_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    min_original = min(annual_totals, key=lambda x: x[1])[1]
    max_original = max(annual_totals, key=lambda x: x[1])[1]
    normalize = lambda value: 450 + (value - min_original) * 450 / (max_original - min_original) if max_original != min_original else 450
    sorted_totals = sorted([(year, normalize(total)) for year, total in annual_totals], key=lambda x: x[0])
    
    tasas_variacion = {}
    for i in range(1, len(sorted_totals)):
        año_actual, total_actual = sorted_totals[i]
        año_anterior, total_anterior = sorted_totals[i-1]
        tasa = ((total_actual - total_anterior) / total_anterior) * 100
        tasas_variacion[año_actual] = tasa
    
    # Mostrar gráfica y resultados en terminal
    años = list(tasas_variacion.keys())
    tasas = list(tasas_variacion.values())
    
    plt.figure(figsize=(10, 6))
    plt.plot(años, tasas, marker='s', color='r', label='Tasa de Variación Anual')
    plt.title("Tasa de Variación Anual de Precipitación")
    plt.xlabel("Año")
    plt.ylabel("Tasa de Variación (%)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    print("\nTasas de Variación Anual (%):")
    for año, tasa in tasas_variacion.items():
        print(f"Año {año}: {tasa:.2f}%")
    
    return tasas_variacion

# Ejecutar el cálculo, mostrar gráficas y guardar en CSV
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"

# Capturar datos de las funciones
annual_media = calculate_annual_precipitation(input_directory)
litros_anuales = calcular_precipitacion_litros_españa(input_directory)
tasas_variacion = calcular_tasa_variacion_anual(input_directory)

# Combinar datos para CSV
media_dict = {item['Year']: item['AnnualTotal'] for item in annual_media}
litros_dict = dict(litros_anuales)
tasa_dict = tasas_variacion

# Crear filas del CSV
csv_rows = []
for year in sorted(media_dict.keys()):
    media = media_dict.get(year, None)
    litros = litros_dict.get(year, None)
    tasa = tasa_dict.get(year, None)
    
    csv_rows.append([
        year,
        f"{media:.2f}" if media is not None else '',
        f"{litros:.2e}" if litros is not None else '',
        f"{tasa:.2f}" if tasa is not None else ''
    ])

# Escribir archivo CSV
with open('estadisticas.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter='\t')
    writer.writerow(['Año', 'Media_Anual', 'Total_Anual', 'Tasa_Variación'])
    writer.writerows(csv_rows)

print("\nArchivo 'estadisticas.csv' creado con éxito.")