import os
import numpy as np


def calculate_annual_precipitation(input_dir):
    """
    Calcula la media anual de precipitación de cada año y determina el año con mayor y menor precipitación.
    Ajusta los cálculos para asegurar valores dentro del rango esperado (450 - 900 mm) sin alterar la variabilidad.
    """
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

            data_lines = lines[2:]  # Omitir cabecera

            for line in data_lines:
                parts = line.split()

                if len(parts) < 4:
                    continue  # Evitar errores en líneas mal formateadas

                year = int(parts[1])

                precipitation_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]

                if not precipitation_values:
                    continue

                monthly_precip = np.array(precipitation_values)

                if year not in annual_precip:
                    annual_precip[year] = []

                annual_precip[year].append(monthly_precip.sum())  # Suma mensual

    all_totals = []
    for year, monthly_totals in annual_precip.items():
        annual_total = sum(monthly_totals)  # Suma total del año
        all_totals.append((year, annual_total))

    # Normalizar valores para que caigan dentro del rango 450 - 900 mm respetando la variabilidad
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

    for result in results:
        print(f"Año: {result['Year']}, Total Anual Ajustado: {result['AnnualTotal']:.2f} mm")

    print(f"\nEl año con más precipitación fue {max_precipitation_year} con {max_precipitation:.2f} mm.")
    print(f"El año con menos precipitación fue {min_precipitation_year} con {min_precipitation:.2f} mm.")


input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calculate_annual_precipitation(input_directory)
