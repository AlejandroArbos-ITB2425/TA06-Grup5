import os


def validar_archivos(carpeta):
    formatos = {}
    contador = 0
    archivos_invalidos = []

    # Procesar todos los archivos en la carpeta
    for archivo in os.listdir(carpeta):
        if archivo.endswith('.dat'):
            contador += 1
            ruta_archivo = os.path.join(carpeta, archivo)
            try:
                with open(ruta_archivo, 'r') as f:
                    # Leer las primeras 5 líneas del archivo
                    lineas = [f.readline().strip() for _ in range(5)]

                # Detectar delimitadores y columnas
                delimitadores = {'\t': "tabulaciones", ',': "comas", ' ': "espacios"}
                formato_actual = None
                for delimitador, nombre in delimitadores.items():
                    columnas = [len(linea.split(delimitador)) for linea in lineas if linea]
                    if len(set(columnas)) == 1:  # Todas las líneas tienen el mismo número de columnas
                        formato_actual = (nombre, columnas[0])
                        break
                if not formato_actual:
                    formato_actual = ('indeterminado', 'variable')

                # Contar el formato
                formatos[formato_actual] = formatos.get(formato_actual, 0) + 1

            except Exception as e:
                archivos_invalidos.append(archivo)
                print(f"Error al procesar {archivo}: {e}")

            # Mostrar progreso cada 1000 archivos
            if contador % 1000 == 0:
                print(f"Procesados {contador} archivos...")

    return formatos, archivos_invalidos


# Ruta de la carpeta con los archivos .dat
carpeta = "precip.MIROC5.RCP60.2006-2100.SDSM_REJ"

# Validar los archivos
formatos, archivos_invalidos = validar_archivos(carpeta)

# Mostrar resultados
print("\nResumen de formatos:")
for formato, cantidad in formatos.items():
    print(f"Delimitador: {formato[0]}, Columnas: {formato[1]} -> {cantidad} archivos")

print(f"\nArchivos inválidos: {len(archivos_invalidos)}")
if archivos_invalidos:
    print("Ejemplo de archivos inválidos:", archivos_invalidos[:5])
