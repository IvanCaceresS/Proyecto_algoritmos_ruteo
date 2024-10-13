# Estacionamientos:
Descripción de los Campos
type: Especifica el tipo de objeto GeoJSON. Para todo el archivo, es "FeatureCollection".

features: Es una lista de objetos de tipo Feature. Cada Feature representa un estacionamiento de bicicletas y contiene:

type: Siempre es "Feature".

id: Un identificador único para la feature, generalmente compuesto por el tipo de elemento y su identificador, por ejemplo, "node/492189391".

geometry: Define la geometría del elemento geoespacial.

type: El tipo de geometría, que en este caso es "Point" porque los estacionamientos se representan como puntos.

coordinates: Un arreglo que contiene las coordenadas geográficas en el formato [longitud, latitud].

properties: Un objeto que contiene las propiedades asociadas al estacionamiento. Las propiedades pueden variar dependiendo de la información disponible, pero comúnmente incluyen:

amenity: Siempre es "bicycle_parking", indicando que se trata de un estacionamiento de bicicletas.

capacity: (Opcional) La capacidad del estacionamiento, es decir, cuántas bicicletas puede albergar.

name: (Opcional) El nombre del estacionamiento.

network: (Opcional) Si el estacionamiento forma parte de una red o sistema específico.

bicycle_parking: (Opcional) Detalles sobre el tipo de estacionamiento, como "rack", "building", etc.

covered: (Opcional) Indica si el estacionamiento está cubierto ("yes") o no ("no").

# Iluminacion:
Descripción de los Campos
type: "Feature" indica que es una entidad geoespacial individual.

properties:

id: 7981159 es el identificador único de la vía en OpenStreetMap.

maxspeed: "50" indica que la velocidad máxima permitida en esta vía es de 50 km/h.

geometry:

type: "LineString" indica que la geometría es una línea compuesta por una secuencia de puntos.

coordinates: Una lista ordenada de coordenadas que representan la ruta de la vía. Cada punto está definido por una longitud y una latitud.

# Inundaciones:
Descripción de los Campos
type: "Feature".

geometry:

type: "Polygon".

coordinates:

Una lista de listas de coordenadas.

Cada sublista representa un anillo del polígono (en este caso, solo el anillo exterior).

Las coordenadas están en el orden [longitud, latitud].

Los puntos están ordenados para formar el perímetro del polígono.

El polígono se cierra repitiendo el primer punto al final de la lista.

properties:

-:

NOM_REGION: "REGIÓN METROPOLITANA DE SANTIAGO".

NOM_COMUNA: "PAINE".

NOM_PROVIN: "MAIPO".

ind_riesgo_inundaciones_t10_delta: 0.0312.

Este valor numérico podría representar el cambio en el índice de riesgo de inundaciones para un período de retorno de 10 años.

# Velocidades_maximas:

Descripción de los Campos
FeatureCollection

type: Indica el tipo de objeto GeoJSON. En este caso, es "FeatureCollection", lo que significa que contiene una colección de características geográficas.
features: Es una lista (array) de objetos Feature.
Feature

type: Siempre es "Feature" para objetos de características individuales.
geometry: Contiene la información geoespacial de la feature.
properties: Un objeto que contiene atributos adicionales sobre la feature.
Geometry

type: Especifica el tipo de geometría. En este caso, es "LineString", que representa una línea formada por una secuencia de puntos.
coordinates: Un array de pares de coordenadas que definen la línea. Cada par es una lista de [longitud, latitud].
Properties

id: Un identificador único para la feature. Por ejemplo, 7981159.
maxspeed: Indica la velocidad máxima permitida en esa vía. En este caso, "50", lo que probablemente significa 50 km/h.