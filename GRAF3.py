import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

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

    # Mostrar gráfica de Media Anual de Precipitación
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
    
    return results, max_precipitation_year, max_precipitation, min_precipitation_year, min_precipitation


# ------------------------------
# Cálculo de Tasa de Variación Anual
# ------------------------------
def calcular_tasa_variacion_anual(results):
    tasas_variacion = {}
    for i in range(1, len(results)):
        año_actual, total_actual = results[i]["Year"], results[i]["AnnualTotal"]
        año_anterior, total_anterior = results[i-1]["Year"], results[i-1]["AnnualTotal"]
        tasa = ((total_actual - total_anterior) / total_anterior) * 100
        tasas_variacion[año_actual] = tasa
    
    # Mostrar gráfica de Tasa de Variación Anual
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

    return tasas_variacion


# ------------------------------
# Guardar resultados en CSV
# ------------------------------
def guardar_resultados_csv(resultados, tasas_variacion, nombre_archivo="resultados_precipitacion.csv"):
    with open(nombre_archivo, mode='w', newline='', encoding='utf-8') as archivo_csv:
        escritor_csv = csv.writer(archivo_csv, delimiter='\t')
        escritor_csv.writerow(["AÑO", "MEDIA_ANUAL", "TASA_VARIACIÓN"])
        
        for resultado in resultados:
            year = resultado["Year"]
            media_anual = resultado["AnnualTotal"]
            tasa_variacion = tasas_variacion.get(year, "N/A")
            escritor_csv.writerow([year, f"{media_anual:.2f}", f"{tasa_variacion:.2f}%" if tasa_variacion != "N/A" else "N/A"])
    
    print(f"Resultados guardados en {nombre_archivo}")


# Ejecutar el cálculo y mostrar las gráficas
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
results, max_precipitation_year, max_precipitation, min_precipitation_year, min_precipitation = calculate_annual_precipitation(input_directory)
tasas_variacion = calcular_tasa_variacion_anual(results)
guardar_resultados_csv(results, tasas_variacion)
