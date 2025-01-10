## Exercici 1 - Obtención de Datos

>Ir a la fuente de datos fiable de meteorología, la AEMET. Obtener los archivos de datos precip.MIROC5.RCP 60.2006-2100.SDSM_REJ. Antes será necesario solicitar una API-Key a la AEMET para poder acceder a la descarga de los datos.

### Obtención del API Key

Para obtener la API Key, es necesario acceder a la página oficial de AEMET. Seguidamente, situarse en el apartado de "DATOS ABIERTOS" -> "AEMET OPENDATA", bajar hasta el final de la página y entrar en el enlace de "AEMET OPENDATA". Una vez dentro, elegir la opción de de obtención de API Key "Solicitar". Dentro del formulario, introducir un Email para obtener la clave mediante el correo electrónico.

![img1](./img/ej1/img_ej1_1.png)
---
![img2](./img/ej1/img_ej1_2.png)
---
![img3](./img/ej1/img_ej1_3.png)
---
![img4](./img/ej1/img_ej1_4.png)
---

Una vez tengamos todos el archivo descargado (precip.MIROC5.RCP60.2006-2100.SDSM_REJ.tar.gz), deberemos de descomprimirlo para obtener la carpeta con todos los archivos .dat
![img5](./img/ej1/img_ej1_5.png)

## Exercici 2 - Organizar y procesar los datos

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

![img6](./img/ej1/img_ej2_1.png)

  - Una etiqueta del punto de observación (P1) es la estación. También es conocido como "Punto de Observación"
  - Año. (2006-2100).
  - Mes (1-12).
  - Fechas diarias, valores de precipitaciones, seguidas por valores de control como -999 que no existen datos válidos o disponibles.
