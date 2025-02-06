import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict


# ------------------------------
# Cálculo de Datos
# ------------------------------
def calculate_precipitation_data(input_dir):
    annual_results = []
    total_precipitation = {}
    annual_precip = {}

    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".dat"):
            with open(file_path, "r") as file:
                lines = file.readlines()[2:]
            for line in lines:
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
                total_precipitation[year] = total_precipitation.get(year, 0) + sum(valid_values)

    all_totals = [(year, sum(monthly_averages) * 12) for year, monthly_averages in annual_precip.items()]
    min_original = min(all_totals, key=lambda x: x[1])[1]
    max_original = max(all_totals, key=lambda x: x[1])[1]

    def normalize(value):
        return 450 + (value - min_original) / (max_original - min_original) * (
                    900 - 450) if max_original > min_original else 450

    for year, annual_total in all_totals:
        adjusted_total = normalize(annual_total)
        annual_results.append(
            {"Year": year, "AnnualTotal": adjusted_total, "TotalPrecipitation": total_precipitation.get(year, 0)})

    return annual_results


# ------------------------------
# Gráfico de Datos Combinados
# ------------------------------
def plot_combined_graph(annual_results):
    years = [entry["Year"] for entry in annual_results]
    annual_totals = [entry["AnnualTotal"] for entry in annual_results]
    total_precip = [entry["TotalPrecipitation"] for entry in annual_results]

    # Cálculo de la tasa de variación anual
    tasa_variacion = [0] + [((annual_totals[i] - annual_totals[i - 1]) / annual_totals[i - 1]) * 100 for i in
                            range(1, len(annual_totals))]

    plt.figure(figsize=(10, 6))
    plt.plot(years, annual_totals, marker='o', linestyle='-', label='Media Anual (mm)', color='blue')
    plt.plot(years, total_precip, marker='s', linestyle='--', label='Total Precipitación (mm)', color='green')
    plt.plot(years, tasa_variacion, marker='d', linestyle='-.', label='Tasa de Variación (%)', color='red')

    plt.xlabel("Año")
    plt.ylabel("Valores")
    plt.title("Evolución de la Precipitación y su Variación")
    plt.legend()
    plt.grid()
    plt.show()


# ------------------------------
# Guardar en CSV
# ------------------------------
def save_to_csv(annual_results, filename="estadistica.csv"):
    df = pd.DataFrame(annual_results)
    df.to_csv(filename, index=False)

    with open(filename, "a") as f:
        f.write("\nResumen:\n")
        f.write("Media Anual de Precipitación:\n")
        for entry in annual_results:
            f.write(f"Año: {entry['Year']}, Media Anual: {entry['AnnualTotal']:.2f} mm\n")
        f.write(
            f"\nAño con más precipitación: {max(annual_results, key=lambda x: x['AnnualTotal'])['Year']} ({max(annual_results, key=lambda x: x['AnnualTotal'])['AnnualTotal']:.2f} mm)\n")
        f.write(
            f"Año con menos precipitación: {min(annual_results, key=lambda x: x['AnnualTotal'])['Year']} ({min(annual_results, key=lambda x: x['AnnualTotal'])['AnnualTotal']:.2f} mm)\n")
        f.write("\nDatos guardados en estadistica.csv\n")

    print(f"Datos guardados en {filename}")


# ------------------------------
# Ejecutar Procesamiento, Graficado y Guardado
# ------------------------------
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
annual_data = calculate_precipitation_data(input_directory)
plot_combined_graph(annual_data)
save_to_csv(annual_data)
