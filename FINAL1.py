import os
from collections import defaultdict

# Constantes
AREA_ESPAÑA_KM2 = 505_990  # Área de España en km²
LITROS_POR_MM_KM2 = 1_000_000  # 1 mm de lluvia sobre 1 km² = 1,000,000 litros

def calcular_estadisticas_completas(input_dir):
    """
    Calcula las estadísticas requeridas:
    1. Totales anuales y media anual en litros
    2. Tasa de variación interanual (%)
    3. Años extremos (máximo y mínimo)
    """
    # Estructuras para almacenar datos
    precipitacion_anual = defaultdict(float)
    archivos_procesados = 0

    # Procesar archivos
    for raiz, _, archivos in os.walk(input_dir):
        for nombre_archivo in archivos:
            if nombre_archivo.endswith(".dat"):
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                archivos_procesados += 1
                
                with open(ruta_archivo, "r", encoding='utf-8') as archivo:
                    lineas = archivo.readlines()[2:]  # Saltar cabeceras
                    
                    for linea in lineas:
                        partes = linea.strip().split()
                        
                        if len(partes) < 4:
                            continue
                        
                        año = int(partes[1])
                        valores_diarios = partes[3:]
                        
                        suma_mes = sum(
                            float(valor) / 10  # Conversión a mm
                            for valor in valores_diarios 
                            if valor not in ("-999", "-999.0")
                        )
                        
                        precipitacion_anual[año] += suma_mes

    # Calcular litros totales
    litros_anuales = {
        año: precipitacion * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2
        for año, precipitacion in precipitacion_anual.items()
    }

    # Ordenar datos
    años_ordenados = sorted(litros_anuales.items(), key=lambda x: x[0])
    
    # 1. Totales y media anual
    print("=== Totales y media anual ===")
    for año, litros in años_ordenados:
        media_anual = litros / (AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2)  # Convertir a mm
        print(f"Año {año}: {litros:.2e} L | Media: {media_anual:.2f} mm")

    # 2. Tasa de variación anual
    print("\n=== Tasa de variación anual ===")
    tasas = {}
    for i in range(1, len(años_ordenados)):
        año_actual, litros_actual = años_ordenados[i]
        año_anterior, litros_anterior = años_ordenados[i-1]
        tasa = ((litros_actual - litros_anterior) / litros_anterior) * 100
        tasas[año_actual] = tasa
        print(f"Año {año_actual}: {tasa:.2f}%")

    # 3. Años extremos
    año_max, maximo = max(años_ordenados, key=lambda x: x[1])
    año_min, minimo = min(años_ordenados, key=lambda x: x[1])
    print("\n=== Años extremos ===")
    print(f"Máximo: {año_max} ({maximo:.2e} L)")
    print(f"Mínimo: {año_min} ({minimo:.2e} L)")

# Ejecutar análisis
directorio = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_estadisticas_completas(directorio)