import os
from collections import defaultdict

# Constantes
AREA_ESPAÑA_KM2 = 505_990  # Área de España en km²
LITROS_POR_MM_KM2 = 1_000_000  # 1 mm de lluvia sobre 1 km² = 1,000,000 litros

def calcular_años_extremos(input_dir):
    """
    Calcula el año más lluvioso y más seco en base a la precipitación total en litros
    """
    precipitacion_anual = defaultdict(float)

    for raiz, _, archivos in os.walk(input_dir):
        for nombre_archivo in archivos:
            if nombre_archivo.endswith(".dat"):
                ruta_archivo = os.path.join(raiz, nombre_archivo)
                
                with open(ruta_archivo, "r", encoding='utf-8') as archivo:
                    lineas = archivo.readlines()[2:]
                    
                    for linea in lineas:
                        partes = linea.strip().split()
                        
                        if len(partes) >= 4:
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

    # Encontrar años extremos
    año_max, maximo = max(litros_anuales.items(), key=lambda x: x[1])
    año_min, minimo = min(litros_anuales.items(), key=lambda x: x[1])

    print(f"Año más lluvioso: {año_max} ({maximo:.2e} litros)")
    print(f"Año más seco: {año_min} ({minimo:.2e} litros)")

# Ejecutar
directorio = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_años_extremos(directorio)