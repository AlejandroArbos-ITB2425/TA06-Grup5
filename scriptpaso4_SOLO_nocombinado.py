import os
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Configuración inicial
data_folder = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"  # Carpeta que contiene los archivos
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

# Reemplazar valores faltantes (-999) por NaN y convertir todas las columnas relevantes a numéricas
combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].apply(pd.to_numeric, errors='coerce')
combined_df.iloc[:, 3:] = combined_df.iloc[:, 3:].applymap(lambda x: np.nan if x == missing_value else x)

# Calcular totales y medias anuales
combined_df["Annual_Total"] = combined_df.iloc[:, 3:].sum(axis=1, skipna=True)
combined_df["Annual_Mean"] = combined_df.iloc[:, 3:].mean(axis=1, skipna=True)

# Agrupar por año y calcular los totales y medias anuales
annual_stats = combined_df.groupby("Year")["Annual_Total"].agg(['sum', 'mean'])

# Calcular la tasa de variación anual (porcentaje de cambio entre los totales de años consecutivos)
annual_stats["Change_Rate"] = annual_stats["sum"].pct_change() * 100

# Identificar el año más lluvioso y el más seco
most_rainy_year = annual_stats["sum"].idxmax()
least_rainy_year = annual_stats["sum"].idxmin()

# Estadísticas adicionales
max_daily_precip = combined_df.iloc[:, 3:].max(axis=1).groupby(combined_df['Year']).max()
min_daily_precip = combined_df.iloc[:, 3:].min(axis=1).groupby(combined_df['Year']).min()
annual_stats["Max_Daily"] = max_daily_precip
annual_stats["Min_Daily"] = min_daily_precip

# Mostrar un resumen por cada año
for year in annual_stats.index:
    print(f"\nResumen para el año {year}:")
    print(f"Total de precipitación en {year}: {annual_stats.loc[year, 'sum']}")
    print(f"Promedio anual en {year}: {annual_stats.loc[year, 'mean']:.2f}")
    change_rate = annual_stats.loc[year, "Change_Rate"]
    print(f"Tasa de variación anual en {year}: {change_rate:.2f}%")
    print(f"Precipitación diaria máxima en {year}: {annual_stats.loc[year, 'Max_Daily']}")
    print(f"Precipitación diaria mínima en {year}: {annual_stats.loc[year, 'Min_Daily']}")

# Mostrar los resultados principales al final
print("\n" + "-"*40)
print(f"Año más lluvioso: {most_rainy_year}, Precipitación total: {annual_stats.loc[most_rainy_year, 'sum']}")
print(f"Año más seco: {least_rainy_year}, Precipitación total: {annual_stats.loc[least_rainy_year, 'sum']}")

# Guardar los resultados
annual_stats.to_csv("resultados_annual_stats.csv", index=True)
with open("resultados_annual_stats.txt", "w") as f:
    f.write(annual_stats.to_string())