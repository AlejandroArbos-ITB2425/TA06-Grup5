import os
import numpy as np
from collections import defaultdict

# ------------------------------
# Cálculo de Máximos y Mínimos Mensuales
# ------------------------------
def calcular_maximos_minimos_mensuales(input_dir):
    maximos_mensuales = defaultdict(lambda: float('-inf'))  # Establecer -inf para encontrar máximos
    minimos_mensuales = defaultdict(lambda: float('inf'))  # Establecer inf para encontrar mínimos
    
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
                month = int(parts[2])  # El mes está en la tercera columna
                valid_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]
                if valid_values:
                    monthly_precip = sum(valid_values) / len(valid_values)
                    # Actualizar máximos y mínimos mensuales
                    if monthly_precip > maximos_mensuales[month]:
                        maximos_mensuales[month] = monthly_precip
                    if monthly_precip < minimos_mensuales[month]:
                        minimos_mensuales[month] = monthly_precip
    
    print("\nMáximos y Mínimos Mensuales de Precipitación:")
    for month in range(1, 13):
        print(f"Mes {month}: Máximo: {maximos_mensuales[month]:.2f} mm, Mínimo: {minimos_mensuales[month]:.2f} mm")


# ------------------------------
# Cálculo de Tendencia de Precipitación (Pendiente de la Recta)
# ------------------------------
def calcular_tendencia_precipitacion(input_dir):
    precipitacion_anual = defaultdict(list)

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
                month = int(parts[2])
                valid_values = [float(x) for x in parts[3:] if x not in ("-999", "-999.0")]
                if valid_values:
                    monthly_precip = sum(valid_values) / len(valid_values)
                    precipitacion_anual[year].append((month, monthly_precip))

    # Para cada estación se ajusta una línea de tendencia
    print("\nTendencia de Precipitación (Pendiente de la Recta):")
    for year, data in precipitacion_anual.items():
        months = [month for month, _ in data]
        precip = [precip for _, precip in data]
        
        if len(months) > 1:
            # Ajustar una recta (y = mx + b) usando la regresión lineal
            m, b = np.polyfit(months, precip, 1)  # '1' es el grado de la polinómica (recta)
            print(f"Año {year}: Pendiente de la recta (Tendencia): {m:.2f} mm/mes")
        else:
            print(f"Año {year}: No se puede calcular la tendencia debido a datos insuficientes.")


# Ejecutar las funciones con el directorio correspondiente
input_directory = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_maximos_minimos_mensuales(input_directory)
calcular_tendencia_precipitacion(input_directory)
