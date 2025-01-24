import os
import pandas as pd

def process_file(file_path):
    # Leer archivo
    data = pd.read_csv(file_path, delim_whitespace=True, header=None)
    data.columns = ["P194", "Latitud", "Longitud", "Altitud", "Tipo", "Inicio", "Fin"] + list(range(1, 32))
    
    rows = []
    for index, row in data.iterrows():
        year = int(row["Inicio"])
        month = index + 1
        for day in range(1, 32):
            value = row[day]
            if value != -999:
                rows.append({"Año": year, "Mes": month, "Día": day, "Precipitación": value})
    
    df = pd.DataFrame(rows)
    return df

def process_directory(directory_path):
    all_data = []
    
    # Procesar todos los archivos en el directorio
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            print(f"Procesando archivo: {file_name}")
            df = process_file(file_path)
            all_data.append(df)
    
    # Combinar datos de todos los archivos
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Calcular estadísticas anuales
    stats = combined_data.groupby("Año")["Precipitación"].agg(["sum", "mean"]).rename(columns={"sum": "Total", "mean": "Media"})
    
    # Calcular tendencia de cambio anual
    stats["Cambio"] = stats["Total"].diff()
    
    # Encontrar años más lluviosos y más secos
    max_precip_year = stats["Total"].idxmax()
    min_precip_year = stats["Total"].idxmin()
    
    print("Estadísticas anuales:")
    print(stats)
    print(f"Año más lluvioso: {max_precip_year} con {stats['Total'].max()} mm")
    print(f"Año más seco: {min_precip_year} con {stats['Total'].min()} mm")
    
    return stats

# Ruta del directorio con los archivos
directory_path = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
result = process_directory(directory_path)
