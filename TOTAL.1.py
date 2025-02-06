import os
from collections import defaultdict

def calcular_precipitacion_anual(input_dir):
    """
    Calcula la precipitación total anual:
    - Ignora primeras 2 líneas de cada archivo
    - Omite primeras 3 columnas de cada línea de datos
    - Excluye valores -999 y -999.0
    - Procesa todos los archivos .dat recursivamente
    """
    precipitacion_anual = defaultdict(float)
    archivos_procesados = 0

    for raiz, _, archivos in os.walk(input_dir):
        for nombre_archivo in archivos:
            if nombre_archivo.endswith(".dat"):
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                archivos_procesados += 1
                
                with open(ruta_archivo, "r") as archivo:
                    lineas = archivo.readlines()[2:]  # Saltar primeras 2 líneas
                    
                    for linea in lineas:
                        partes = linea.strip().split()
                        
                        if len(partes) < 4:  # Si no tiene mínimo: P1, año, mes + al menos 1 día
                            continue
                        
                        # Extraer año (segunda columna)
                        año = int(partes[1])
                        
                        # Procesar solo a partir de la 4ta columna (días)
                        valores_diarios = partes[3:]
                        
                        # Sumar valores válidos
                        precipitacion_valida = sum(
                            float(valor) 
                            for valor in valores_diarios 
                            if valor not in ("-999", "-999.0")
                        )
                        
                        precipitacion_anual[año] += precipitacion_valida

    # Ordenar y mostrar resultados
    años_ordenados = sorted(precipitacion_anual.items())
    
    print(f"Archivos procesados: {archivos_procesados}")
    print("\nPrecipitación anual total (mm):")
    for año, total in años_ordenados:
        print(f"{año}: {total:.2f} mm")
    
    if años_ordenados:
        año_max, maximo = max(años_ordenados, key=lambda x: x[1])
        año_min, minimo = min(años_ordenados, key=lambda x: x[1])
        print(f"\nMáximo histórico: {año_max} ({maximo:.2f} mm)")
        print(f"Mínimo histórico: {año_min} ({minimo:.2f} mm)")

# Ejecutar análisis
directorio = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_precipitacion_anual(directorio)