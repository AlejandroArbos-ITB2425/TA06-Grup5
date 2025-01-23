## Ejercicio 1 - Obtención de Datos

>Ir a la fuente de datos fiable de meteorología, la AEMET. Obtener los archivos de datos precip.MIROC5.RCP 60.2006-2100.SDSM_REJ. Antes será necesario solicitar una API-Key a la AEMET para poder acceder a la descarga de los datos.

### Obtención de la API Key

Para obtener la API Key, es necesario acceder a la página oficial de AEMET. Seguidamente, situarse en el apartado de "DATOS ABIERTOS" -> "AEMET OPENDATA", bajar hasta el final de la página y entrar en el enlace de "AEMET OPENDATA". Una vez dentro, elegir la opción de de obtención de API Key "Solicitar". Dentro del formulario, introducir un Email para obtener la clave mediante el correo electrónico.

![img1](./img/ej1/img_ej1_1.png)
---
![img2](./img/ej1/img_ej1_2.png)
---
![img3](./img/ej1/img_ej1_3.png)
---
![img4](./img/ej1/img_ej1_4.png)

Una vez tengamos todos el archivo descargado (precip.MIROC5.RCP60.2006-2100.SDSM_REJ.tar.gz), deberemos de descomprimirlo para obtener la carpeta con todos los archivos .dat

![img5](./img/ej1/img_ej1_5.png)

---

## Ejercicio 2 - Organizar y procesar los datos

> PASO 1: Revisar las cabeceras, separación entre datos, comentarios. Saber cómo están delimitados los datos. Qué columnas hay y qué tipos de datos.

Principalmente, se puede ver que las cabeceras están separadas por tabulación (`\t`), dentro de ésta hay diferentes campos, los cuales son:

1. **`precip`**
  - Indica que los datos están relacionados con precipitaciones.

2. **`MIROC5`**
  - Hace referencia al modelo climático utilizado.

3. **`RCP60`**
  - Representa un escenario de emisiones de gases de efecto invernadero.

4. **`REGRESION`**
  - Indica que los datos han sido procesados mediante un modelo de regresión.

5. **`decimas`**
  - Especifica la unidad de medida para los valores de los datos.

6. **`1`**
  - Podría ser un identificador o una versión del conjunto de datos.

Los datos en las líneas dentro de los archivos están delimitados por espacios. Por ejemplo:

![img6](./img/ej2/img_ej2_1.png)

  - Una etiqueta del punto de observación (P1) es la estación. También es conocido como "Punto de Observación"
  - Año. (2006-2100).
  - Mes (1-12).
  - Fechas diarias, valores de precipitaciones, seguidas por valores de control como -999 que no existen datos válidos o disponibles.

> PASO 2: Verificar que todos los archivos tienen el mismo formato. Se puede hacer un script de validación básica, que lea las primeras filas de cada archivo y determinaar el número de columnas y delimitadores.


> PASO 3: Asegurar que los datos no contengan errores, valores que falten o inconsistencias:
Lectura: Utilizar pandas para gestionar los archivos y gestionar errores de lectura.
Verifica la consistencia de las columnas: Asegurar que los datos en cada columna tienen el tipo esperado (numérico, fecha, etc.).
Gestionar valores que faltan o corruptos: Identifica y trata datos nulos o valores atípicos.

> PASO 4: Documenta todo el proceso por si tienes que repetirlo alguna vez. Indica qué decisiones has tomado, qué has hecho con los valores nulos y cómo has solucionado inconsistencias.

Al ejecutar el código desarrollado para analizar los archivos según los parámetros indicados en el enunciado, se han obtenido los resultados que se muestran en la imagen adjunta. Este código ha permitido identificar:

- Calcular el porcentaje de datos carentes (-999)
- Calcular estadísticas: de los datos procesados.
- Medios y totales anuales: Muestra la precipitación total y media por año.
- Tendencia de cambio: La tasa de variación anual de las precipitaciones.
- Extremos: Los años más lluviosos y más secos.
- Analizar los datos: pensar qué estadísticas tiene sentido hacer. Y añadir por lo menos dos más.

![img7](./img/ej2/img_pas4_2.png)

Al ejecutar el código desarrollado para analizar los archivos según los parámetros indicados en el enunciado, se han obtenido los resultados que se muestran en la imagen adjunta. Este código ha permitido identificar:

-El total de archivos procesados, que asciende a 16.064.

-El número total de ocurrencias del valor -999, que representa los datos faltantes o especiales, con un total de 10.682.560 ocurrencias.

-El total de otros valores presentes en los archivos, que suma 557.019.200 ocurrencias.

-El porcentaje de valores -999 respecto al total de datos, que en este caso es del 1,88%

-El total de valores: 567.701.760



## Ejercicio 3 - Obtención de Datos

- Mostrar resúmenes estadísticos por pantalla
- Mostrar gráficos estadísticos por pantalla
- Exportar los resúmenes estadísticos a archivos CSV
