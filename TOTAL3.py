import os
from collections import defaultdict

# Constantes
AREA_ESPAÑA_KM2 = 505_990  # Área de España en km²
LITROS_POR_MM_KM2 = 1_000_000  # 1 mm de lluvia sobre 1 km² = 1,000,000 litros

def calcular_precipitacion_litros_españa(input_dir):
    """
    Calcula la precipitación total anual en litros para toda España:
    - Convierte décimas de mm a mm
    - Suma todos los valores válidos
    - Calcula el volumen total en litros
    """
    precipitacion_anual = defaultdict(float)
    archivos_procesados = 0

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
                        
                        # Convertir décimas de mm a mm y sumar valores válidos
                        suma_mes = sum(
                            float(valor) / 10  # Conversión a mm
                            for valor in valores_diarios 
                            if valor not in ("-999", "-999.0")
                        )
                        
                        precipitacion_anual[año] += suma_mes

    # Calcular litros totales: Precipitación (mm) * Área (km²) * 1,000,000
    litros_anuales = {
        año: precipitacion * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2
        for año, precipitacion in precipitacion_anual.items()
    }

    # Resultados
    años_ordenados = sorted(litros_anuales.items())
    
    print(f"Archivos procesados: {archivos_procesados}")
    print("\nPrecipitación Total Anual:")
    for año, litros in años_ordenados:
        print(f"Año {año}: {litros:.2e} L")  # Notación científica
    
    if años_ordenados:
        año_max, maximo = max(años_ordenados, key=lambda x: x[1])
        año_min, minimo = min(años_ordenados, key=lambda x: x[1])
        print(f"\nEl año con más precipitación fue: {año_max} ({maximo:.2e} L)")
        print(f"\nEl año con menos precipitación fue: {año_min} ({minimo:.2e} L)")

#  Reemplazar con tu ruta absoluta 
directorio = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_precipitacion_litros_españa(directorio)