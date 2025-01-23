import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Configuración inicial
data_folder = "./PROVA"  # Carpeta que contiene los archivos
missing_value = -999  # Valor que representa datos faltantes

# Función para procesar un archivo
def process_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file.readlines()[2:]:  # Ignorar las dos primeras líneas
            parts = line.strip().split()
            if len(parts) > 3:
                data.append(parts)

    # Crear el DataFrame
    columns = ["Region", "Year", "Month"] + [f"Day_{i + 1}" for i in range(31)]
    df = pd.DataFrame(data, columns=columns)

    # Convertir las columnas relevantes a tipo numérico
    df.iloc[:, 1:] = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
    return df

# Leer y combinar los datos de todos los archivos
all_data = []
for filename in os.listdir(data_folder):
    file_path = os.path.join(data_folder, filename)
    if os.path.isfile(file_path):
        try:
            df = process_file(file_path)
            all_data.append(df)
        except Exception as e:
            print(f"Error procesando el archivo {filename}: {e}")

# Combinar todos los datos en un único DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Calcular el porcentaje y número total de datos faltantes
total_values = combined_df.iloc[:, 3:].size
missing_values = (combined_df.iloc[:, 3:] == missing_value).sum().sum()
missing_percentage = (missing_values / total_values) * 100

# Sustituir valores negativos por NaN
combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].applymap(lambda x: np.nan if x < 0 else x)

# Calcular totales y medias anuales
combined_df["Annual_Total"] = combined_df.iloc[:, 3:].sum(axis=1)
combined_df["Annual_Mean"] = combined_df.iloc[:, 3:].mean(axis=1)
annual_stats = combined_df.groupby("Year")[["Annual_Total", "Annual_Mean"]].sum()

# Calcular la tasa de variación anual
annual_stats["Change_Rate"] = annual_stats["Annual_Total"].pct_change() * 100

# Identificar el año más lluvioso y más seco
most_rainy_year = annual_stats["Annual_Total"].idxmax()
least_rainy_year = annual_stats["Annual_Total"].idxmin()

# Imprimir resultados
print(f"Año más lluvioso: {most_rainy_year}, Precipitación total: {annual_stats.loc[most_rainy_year, 'Annual_Total']:.1f}")
print(f"Año más seco: {least_rainy_year}, Precipitación total: {annual_stats.loc[least_rainy_year, 'Annual_Total']:.1f}\n")

# Resumen por año
for year in annual_stats.index:
    print(f"Resumen para el año {year}:")
    print(f"Total de precipitación en {year}: {annual_stats.loc[year, 'Annual_Total']:.1f}")
    print(f"Promedio mensual en {year}: {annual_stats.loc[year, 'Annual_Mean']:.2f}")
    change_rate = annual_stats.loc[year, "Change_Rate"]
    print(f"Tasa de variación anual en {year}: {change_rate:.2f}%\n")

# Mostrar estadísticas de datos faltantes
print(f"Porcentaje de datos faltantes: {missing_percentage:.2f}%")
print(f"Número total de valores nulos: {missing_values}")

# Guardar resultados
annual_stats.to_csv("resultados_annual_stats.csv", index=True)