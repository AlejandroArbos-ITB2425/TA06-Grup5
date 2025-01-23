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
            df["Source_File"] = filename  # Añadir el nombre del archivo como columna
            all_data.append(df)
        except Exception as e:
            print(f"Error procesando el archivo {filename}: {e}")

# Combinar todos los datos en un único DataFrame
combined_df = pd.concat(all_data, ignore_index=True)

# Calcular el porcentaje y número total de datos faltantes
total_values = combined_df.iloc[:, 3:].size
missing_values = (combined_df.iloc[:, 3:] == missing_value).sum().sum()
missing_percentage = (missing_values / total_values) * 100
print(f"\nPorcentaje de datos faltantes: {missing_percentage:.2f}%")
print(f"Número total de valores nulos: {missing_values}\n")

# Convertir columnas numéricas y reemplazar valores faltantes
for col in combined_df.columns[3:]:
    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

# Sustituir valores negativos por NaN
combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].applymap(lambda x: np.nan if x < 0 else x)

# Estadísticas de los datos procesados
daily_data = combined_df.iloc[:, 3:].stack()

# Convertir valores a enteros y luego a cadenas para mostrar top como 0 en lugar de 0.0
daily_data = daily_data.dropna().astype(int).astype(str)
categorical_stats = daily_data.describe()
print("Estadísticas básicas de los datos procesados (categóricas):")
print(categorical_stats.to_string())

# Calcular totales y medias anuales
combined_df["Annual_Total"] = combined_df.iloc[:, 3:].sum(axis=1)
combined_df["Annual_Mean"] = combined_df.iloc[:, 3:].mean(axis=1)
annual_stats = combined_df.groupby("Year")[["Annual_Total", "Annual_Mean"]].sum()

# Mostrar los totales y medias anuales de forma ordenada
print("\nTotales y medias anuales:")
print(annual_stats.to_string(index=True))

# Calcular la tasa de variación anual
annual_stats["Change_Rate"] = annual_stats["Annual_Total"].pct_change() * 100

# Mostrar la tasa de variación anual
print("\nTasa de variación anual:")
print(annual_stats[["Change_Rate"]].to_string())

# Años más lluviosos y secos
most_rainy_year = annual_stats["Annual_Total"].idxmax()
least_rainy_year = annual_stats["Annual_Total"].idxmin()
print(f"\nAño más lluvioso: {most_rainy_year}, Precipitación total: {annual_stats.loc[most_rainy_year, 'Annual_Total']}")
print(f"Año más seco: {least_rainy_year}, Precipitación total: {annual_stats.loc[least_rainy_year, 'Annual_Total']}")

# Guardar los resultados
annual_stats.to_csv("resultados_annual_stats.csv", index=True)
with open("resultados_annual_stats.txt", "w") as f:
    f.write(annual_stats.to_string())
