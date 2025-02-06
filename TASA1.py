import os
import numpy as np
from scipy import stats
from collections import defaultdict

def calcular_tendencia_porcentual(input_dir):
    """
    Calcula:
    1. Variación porcentual anual de la precipitación
    2. Tendencia promedio (% por año)
    3. Resultados detallados por año
    """
    # Constantes y configuración
    AREA_ESPAÑA_KM2 = 505_990
    LITROS_POR_MM_KM2 = 1_000_000

    # Paso 1: Calcular precipitación anual
    precipitacion_anual = defaultdict(float)
    
    for raiz, _, archivos in os.walk(input_dir):
        for archivo in archivos:
            if archivo.endswith(".dat"):
                ruta = os.path.join(raiz, archivo)
                with open(ruta, "r", encoding="utf-8") as f:
                    lineas = f.readlines()[2:]
                    for linea in lineas:
                        datos = linea.strip().split()
                        if len(datos) < 4:
                            continue
                        año = int(datos[1])
                        valores = [float(v)/10 for v in datos[3:] if v not in ("-999", "-999.0")]
                        precipitacion_anual[año] += sum(valores) * AREA_ESPAÑA_KM2 * LITROS_POR_MM_KM2

    # Paso 2: Preparar datos
    años = sorted(precipitacion_anual.keys())
    litros = np.array([precipitacion_anual[a] for a in años])
    
    # Paso 3: Calcular variación interanual en %
    variacion_porcentual = {}
    for i in range(1, len(años)):
        año_actual = años[i]
        litros_actual = litros[i]
        litros_anterior = litros[i-1]
        
        if litros_anterior == 0:
            variacion = 0.0
        else:
            variacion = ((litros_actual - litros_anterior) / litros_anterior) * 100
        
        variacion_porcentual[año_actual] = variacion

    # Paso 4: Calcular tendencia promedio (regresión lineal)
    slope, intercept, _, _, _ = stats.linregress(años, litros)
    litros_promedio = np.mean(litros)
    tendencia_promedio = (slope / litros_promedio) * 100  # % por año

    # Paso 5: Resultados
    print("Variación porcentual anual:")
    for año, var in variacion_porcentual.items():
        print(f"- {año}: {var:.2f}%")
    
    print(f"\nTendencia promedio anual: {tendencia_promedio:.2f}% por año")
    print(f"(Basada en regresión lineal de {años[0]} a {años[-1]})")

#  Reemplaza con tu ruta
directorio = "./precip.MIROC5.RCP60.2006-2100.SDSM_REJ"
calcular_tendencia_porcentual(directorio)