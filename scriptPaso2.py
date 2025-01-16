import os

# Ruta del directorio donde están los archivos
directorio = './precip.MIROC5.RCP60.2006-2100.SDSM_REJ'


# Función para contar columnas y delimitadores en una línea
def obtener_columnas_y_delimitador(linea):
    # Intenta determinar el delimitador (espacio o tabulación)
    if '\t' in linea:
        delimitador = '\t'  # tabulador
    else:
        delimitador = ' '  # espacio
    # Divide la línea por el delimitador y contar las columnas
    columnas = linea.strip().split(delimitador)
    return len(columnas), delimitador


# Lista para almacenar los resultados de validación
resultados = []

# Recorremos cada archivo en el directorio
for archivo in os.listdir(directorio):
    if archivo.endswith('.dat'):
        ruta_archivo = os.path.join(directorio, archivo)

        with open(ruta_archivo, 'r') as f:
            # Leer las primeras líneas (por ejemplo, las primeras 3)
            lineas = [f.readline().strip() for _ in range(3)]  # Leer las primeras 3 líneas

            # Obtener el número de columnas y delimitador de la primera línea
            num_columnas, delimitador = obtener_columnas_y_delimitador(lineas[0])

            # Comprobar si las otras líneas tienen el mismo número de columnas
            for linea in lineas[1:]:
                columnas, _ = obtener_columnas_y_delimitador(linea)
                if columnas != num_columnas:
                    resultados.append(f"Error en el archivo {archivo}: columnas inconsistentes en la línea.")
                    break
            else:
                # Si no hay errores, guardar el formato detectado
                resultados.append(f"Archivo {archivo} tiene {num_columnas} columnas con delimitador '{delimitador}'.")

# Imprimir los resultados de la validación
for resultado in resultados:
    print(resultado)

