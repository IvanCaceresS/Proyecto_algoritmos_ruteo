# Instrucciones para configurar el proyecto

Sigue estos pasos para configurar el entorno virtual, instalar dependencias y ejecutar el proyecto.
- **USAR PYTHON 3.9 y descargar CPLEX_STUDIO2211 DE IBM,** 


### 1. Crear y activar el entorno virtual

```bash
python -m venv virtual_env
virtual_env\Scripts\activate
```

### 2. Instalar CPLEX desde la carpeta de instalación

```bash
cd "C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cplex\python\3.9\x64_win64"
pip install .
```

### 3. Instalar dependencias del proyecto
```bash
cd "C:\Users\Ivaaan\Desktop\git\Proyecto_algoritmos_ruteo"
pip install -r requirements.txt
```

### 4. Ejecutar el proyecto
```bash
python main.py
```

# Segundo trabajo grupal (Fase 2)

Para el segundo trabajo grupal del curso (fase 2), deberá hacer una presentación (que deberá subir a Canvas) donde se detalle claramente el proceso y contenga enlaces a cada archivo (recuerde que se evaluará que el contenido esté en la presentación para poder evaluar por igual a todos).

# Tercer trabajo grupal (Fase 3)
1.- La infraestructura a utilizar deberá permitir generar rutas realistas, es decir, no debe generar líneas rectas entre dos puntos. [LISTO]

2.- Se deberá poder filtrar la información a consultar por comunas (para esto deberá utilizar el siguiente geojsonLinks to an external site.). [LISTO]

3.- La interfaz web deberá poder recibir los parámetros de consulta del usuario (restricciones del usuario impuestas por su aplicación) y detectar su geolocalización de forma automática (de forma alternativa, el usuario en caso de no dar permisos para compartir la geolocalización, podrá indicar la dirección a utilizar como inicio).[LISTO]

4.- La interfaz deberá ser capaz de cargar todos los metadatos y amenazas detectados en las comunas filtradas (utilizar popups o algún otro mecanismo para desplegar la información que no se pueda visualizar como un polígono). Para habilitar o deshabilitar la información mostrada, puede utilizar un panel de control que posea checkboxes.[LISTO]

5.- A partir de los datos obtenidos como amenaza, cada uno debe ser modelado como una probabilidad de falla en su sistema. Para esto, deberá crear un archivo que genere la probabilidad de fallo de cada enlace y nodo a partir de cada amenaza considerada en su trabajo. [LISTO]

6.- Deberá mostrar como solución la mejor ruta que satisfaga su problemática, utilizando y detallando el funcionamiento de las siguientes técnicas:

Pgr_dijkstra usando como peso solo la distancia en metros. [LISTO]
Utilizando CPLEX, a partir del modelamiento formal de su problema de optimización, considere las variables de los metadatos y amenazas, y las condiciones del usuario como restricciones.[LISTO]
Pgr_dijkstra utilizando el los parámetros y condiciones propuestas en el punto anterior.[LISTO]
Una metaheurística que considere viable para solucionar su problemática.[LISTO]
Las 4 rutas generadas deben ser posibles de habilitar o deshabilitar desde su página web.

Deberá indicar el tiempo de cómputo en calcular cada ruta.

7.- A partir de las probabilidades asignadas, deberá habilitar una opción que permita, a partir de números aleatorios entre 0 y 100, determinar si ocurrirá o no la falla (a partir de si supera o no el umbral de falla).[LISTO]

8.- Deberá poder habilitar un checkbox que permita mostrar solo las amenazas que podrían ocurrir.[LISTO]

9.- Utilizar una métrica de resiliencia para su servicio, para cada una de las técnicas de ruteo utilizadas e indicar cuál de ellas fue la más resiliente frente a las amenazas detectadas en su infraestructura. Este valor debe ser desplegado junto a la leyenda que indica el algoritmo y tiempo de cómputo de cada ruta.[LISTO]

10.- Realizar un ejemplo de caso en donde se pueda evidenciar que su solución provee una ruta alternativa frente a una amenaza (mitigando lo más posible las amenazas), y que evidencie que se logra cumplir sus objetivos iniciales.