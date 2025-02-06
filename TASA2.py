import os

def calcular_tasa_variacion_anual(input_dir):
    """
    Calcula exclusivamente la tasa de variación anual (%) de la precipitación media ajustada.
    - Omite la impresión de valores medios anuales.
    - Devuelve las tasas de variación desde el segundo año.
    """
    # Paso 1: Calcular precipitaciones anuales brutas
    annual_precip = {}
    for file_name in os.listdir(input_dir):
        if file_name.endswith(".dat"):
            file_path = os.path.join(input_dir, file_name)
            with open(file_path, "r") as file:
                lines = file.readlines()[2:]  # Saltar cabeceras

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

    # Paso 2: Normalizar al rango 450-900 mm
    annual_totals = [
        (year, sum(monthly_averages) * 12)
        for year, monthly_averages in annual_precip.items()
    ]
    min_original = min(annual_totals, key=lambda x: x[1])[1]
    max_original = max(annual_totals, key=lambda x: x[1])[1]

    # Función de normalización
    normalize = lambda value: 450 + (value - min_original) * 450 / (max_original - min_original) if max_original != min_original else 450

    # Aplicar normalización y ordenar por año
    sorted_totals = sorted(
        [(year, normalize(total)) for year, total in annual_totals],
        key=lambda x: x[0]
    )

    # Paso 3: Calcular tasas de variación anual
    tasas_variacion = {}
    for i in range(1, len(sorted_totals)):
        año_actual, total_actual = sorted_totals[i]
        año_anterior, total_anterior = sorted_totals[i-1]
        tasa = ((total_actual - total_anterior) / total_anterior) * 100
        tasas_variacion[año_actual] = tasa

    # Imprimir solo las tasas
    print("Tasas de variación anual (%):")
    for año, tasa in tasas_variacion.items():
        print(f"Año {año}: {tasa:.2f}%")

# Ejemplo de uso
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_tasa_variacion_anual(input_directory)