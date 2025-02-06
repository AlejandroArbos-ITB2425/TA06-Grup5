import os
import numpy as np
import pandas as pd
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
        return 450 + (value - min_original) / (max_original - min_original) * (
                    900 - 450) if max_original > min_original else 450

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

    print("\nMedia Anual de Precipitación:")
    for result in results:
        print(f"Año {result['Year']}: {result['AnnualTotal']:.2f} mm")

    # Gráfico de Media Anual
    plt.figure(figsize=(10, 5))
    plt.plot([r["Year"] for r in results], [r["AnnualTotal"] for r in results], marker='o', linestyle='-')
    plt.xlabel("Año")
    plt.ylabel("Media Anual (mm)")
    plt.title("Media Anual de Precipitación")
    plt.grid()
    plt.show()

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

    litros_anuales = {año: precipitacion * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2 for año, precipitacion in
                      precipitacion_anual.items()}

    print("\nPrecipitación Total en España:")
    for año, litros in litros_anuales.items():
        print(f"Año {año}: {litros:.2e} L")

    # Gráfico de Precipitación Total
    plt.figure(figsize=(10, 5))
    plt.bar(litros_anuales.keys(), litros_anuales.values())
    plt.xlabel("Año")
    plt.ylabel("Litros (L)")
    plt.title("Precipitación Total en España")
    plt.grid()
    plt.show()

    return litros_anuales


# ------------------------------
# Cálculo de la Tasa de Variación Anual
# ------------------------------
def calcular_tasa_variacion_anual(annual_data):
    tasas_variacion = {}
    sorted_totals = sorted(annual_data, key=lambda x: x["Year"])
    for i in range(1, len(sorted_totals)):
        año_actual, total_actual = sorted_totals[i]["Year"], sorted_totals[i]["AnnualTotal"]
        año_anterior, total_anterior = sorted_totals[i - 1]["Year"], sorted_totals[i - 1]["AnnualTotal"]
        tasa = ((total_actual - total_anterior) / total_anterior) * 100
        tasas_variacion[año_actual] = tasa

    print("\nTasa de Variación Anual:")
    for año, tasa in tasas_variacion.items():
        print(f"Año {año}: {tasa:.2f} %")

    # Gráfico de Tasa de Variación
    plt.figure(figsize=(10, 5))
    plt.plot(list(tasas_variacion.keys()), list(tasas_variacion.values()), marker='o', linestyle='-')
    plt.xlabel("Año")
    plt.ylabel("Tasa de Variación (%)")
    plt.title("Tasa de Variación Anual de Precipitación")
    plt.grid()
    plt.show()

    return tasas_variacion
# ------------------------------
# Ejecutar cálculos y mostrar resultados
# ------------------------------
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"

# Calcular y mostrar media anual
annual_data = calculate_annual_precipitation(input_directory)

# Calcular y mostrar precipitación total
precip_total = calcular_precipitacion_litros_españa(input_directory)

# Calcular y mostrar tasa de variación anual
tasa_variacion = calcular_tasa_variacion_anual(annual_data)

# ------------------------------
# Guardar datos en CSV
# ------------------------------
df_media_anual = pd.DataFrame(annual_data)
df_precipitacion_total = pd.DataFrame(list(precip_total.items()), columns=["Year", "Total Litros"])
df_tasa_variacion = pd.DataFrame(list(tasa_variacion.items()), columns=["Year", "Tasa de Variación (%)"])

df_media_anual.to_csv("estadistica.csv", index=False)
df_precipitacion_total.to_csv("estadistica.csv", mode='a', index=False)
df_tasa_variacion.to_csv("estadistica.csv", mode='a', index=False)

print("\nResultados guardados en 'estadistica.csv'")
