import os

def calculate_annual_precipitation(input_dir):
    """
    Calcula la media anual de precipitación, ajusta los valores al rango 450-900 mm,
    y determina la tasa de variación anual en porcentaje.
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

    all_totals = []
    for year, monthly_averages in annual_precip.items():
        annual_total = sum(monthly_averages) * 12
        all_totals.append((year, annual_total))

    # Normalización al rango 450-900 mm
    min_original = min(all_totals, key=lambda x: x[1])[1]
    max_original = max(all_totals, key=lambda x: x[1])[1]

    def normalize(value):
        if max_original == min_original:
            return 450.0
        return 450 + (value - min_original) / (max_original - min_original) * 450

    # Calcular valores ajustados y tasas de variación
    sorted_totals = sorted(all_totals, key=lambda x: x[0])
    adjusted_totals = []
    for year, total in sorted_totals:
        adjusted_total = normalize(total)
        adjusted_totals.append((year, adjusted_total))

    # Calcular tasas de variación anual
    variation_rates = {}
    for i in range(1, len(adjusted_totals)):
        current_year, current_total = adjusted_totals[i]
        prev_year, prev_total = adjusted_totals[i-1]
        variation = ((current_total - prev_total) / prev_total) * 100
        variation_rates[current_year] = variation

    # Construir resultados
    for year, total in adjusted_totals:
        result = {
            "Year": year,
            "AnnualTotal": total,
            "VariationRate": variation_rates.get(year, None)  # None para el primer año
        }
        results.append(result)

        # Actualizar máximos y mínimos
        if total > max_precipitation:
            max_precipitation = total
            max_precipitation_year = year
        if total < min_precipitation:
            min_precipitation = total
            min_precipitation_year = year

    # Imprimir resultados
    for result in results:
        variation = result["VariationRate"]
        if variation is not None:
            print(f"Año {result['Year']}: {result['AnnualTotal']:.2f} mm | Tasa de variación: {variation:.2f}%")
        else:
            print(f"Año {result['Year']}: {result['AnnualTotal']:.2f} mm | Tasa de variación: N/A")

    print(f"\nMáximo: {max_precipitation_year} ({max_precipitation:.2f} mm)")
    print(f"Mínimo: {min_precipitation_year} ({min_precipitation:.2f} mm)")

# Ejecutar
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calculate_annual_precipitation(input_directory)