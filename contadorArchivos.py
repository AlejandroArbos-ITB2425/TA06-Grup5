import os

directorio = './precip.MIROC5.RCP60.2006-2100.SDSM_REJ'
# Obtener todos los archivos dentro del directorio
archivos = os.listdir(directorio)
contador_archivos = sum(1 for archivo in archivos if os.path.isfile(os.path.join(directorio, archivo)))

# Imprimir Resultado
print(f"Total de archivos: {contador_archivos}")
