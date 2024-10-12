# Segundo Trabajo Grupal (Fase 2)

Para el segundo trabajo grupal del curso (fase 2), deberá hacer una presentación (que deberá subir a Canvas) donde se detalle claramente el proceso y contenga enlaces a cada archivo (recuerde que se evaluará que el contenido esté en la presentación para poder evaluar por igual a todos).

## Repositorio en GitHub

El repositorio debe contener las siguientes carpetas y archivos:

### 1. Carpeta Infraestructura
Debe contener:
- Un archivo que automatice la descarga de la infraestructura.
- El archivo descargado que contenga la infraestructura (nodos y aristas).

### 2. Carpeta Metadata
Debe contener:
- N archivos, donde cada uno automatice la descarga de la metadata de n APIs o bases de datos distintas.
- El archivo respectivo que contenga la metadata descargada.

### 3. Carpeta Amenazas
Debe contener:
- N archivos, donde cada uno automatice la descarga de la amenaza de n APIs o bases de datos distintas.
- El archivo respectivo que contenga la amenaza descargada.

### 4. Estructura Resultante
Por cada archivo de automatización, deberá indicar la estructura resultante de cada archivo descargado, para facilitar el entendimiento de la data obtenida.

### 5. Imagen de Tablas y Valores
Debe disponer de una imagen que muestre las tablas y los valores que poseen para un mejor entendimiento de su base de datos. Esta imagen debe estar acompañada de un archivo `.sql` que permita crear la base de datos desde cero.

### 6. Importación de Data
Por cada archivo de automatización, deberá generar un archivo que permita importar la data recolectada a su base de datos. En este archivo, podrá sanitizar el archivo descargado y hacer las modificaciones necesarias para ajustar los datos a las tablas de su base de datos.

### 7. Carpeta Sitio Web
Debe contener un archivo que permita crear un sitio web con [Leaflet](https://leafletjs.com/) para visualizar:
- La infraestructura.
- La información de la metadata.
- Las amenazas.

### 8. Ruta Generada con pgr_dijkstra
El sitio deberá mostrar una ruta generada con `pgr_dijkstra`, utilizando la longitud de la ruta como costo. Esta ruta mostrará, a modo de ejemplo, una posible solución al problema planteado. Será el peor caso que podría resolver la problemática, ya que no considerará la metadata ni las posibles amenazas (esto será parte de la fase 3).

### 9. Archivo Main
Debe crear un archivo `main` (en la carpeta raíz del repositorio de GitHub) que permita ejecutar los procesos anteriores de forma automatizada, desde la descarga de toda la información, su importación en la base de datos y la habilitación del sitio web.


chromedirver: https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.100/win64/chromedriver-win64.zip