# UAM - Dragon Ball - Episorio 1 - julianjm

_15/07/2019_

> Hay web con un radar que indica si una bola está en el rango de detección. La ubicación la obtiene del navegador.
>
> Existe otro servicio que, pasándole el nombre correto, devuelve la flag.
>
> [Enunciado completo](https://unaalmes.hispasec.com/challenges#EPISODIO%20)

## El (mardito) radar

Al entrar en la página nos pide acceso a la ubicación y vemos un radar con un mensaje que indica nuestras coordenadas y el mensaje "No estás cerca de ninguna bola de dragón"

Viendo las peticiones que hace la página, usando el inspector de red, vemos que realiza una llamada a serv◊er.php, enviando como parámetros lat y lng correspondientes a nuestra ubicación. La respuesta: `{"success":0}`

Analizamos el código javascript, y vemos, en client.js, una función relevante:

```javascript
function showPosition(position) {
    $.ajax({
        type: "POST",
        url: 'server.php',
        data: {'lat':position.coords.latitude, 'lng': position.coords.longitude},
        
        success: function(response) {
            var jsonData = JSON.parse(response);
            if (jsonData.success != 0) {
                output.innerHTML = "¡Estás cerca de la bola de dragón de " + jsonData.stars + " estrella(s)! Se encuentra en "
                + jsonData.city + ". (lat: " + jsonData.lat + " / lng: " + jsonData.lng + ")";
                document.getElementsByClassName("points")[0].innerHTML = jsonData.locInRadar;
            } else if (jsonData.success == 0)
                output.innerHTML = "Te encuentras en " + position.coords.latitude + " / " + position.coords.longitude + ". No estás cerca de ninguna bola de dragón.";
        }
    });
    //continua, pero lo imporatnte está arriba
}
```

La función `showPosition` se ejecuta cada vez que cambia la ubicación, o cuando se entra por primera vez. Vemos la llamada a `server.php` con los parámetros `lat`y `lng`. 

Cuando estamos cerca de una bola, un dato importante que nos indica es la ciudad en la que se encuentra. Es decir, no están distribuidas al azar por el globo (flat earthers may disagree), sino que se encuentran en ciudades. Supondremos también que están en ciudades importantes a nivel de población (ignoraremos Triquivijate y Calzadilla de los Barros).

## Automatización

No es viable de recorrer las principales ciudades del mundo, como si buscásemos Pokemones. La idea es obtener un listado de ciudades del mundo, con sus coordenadas GPS, y realizar peticiones a `server.php`, hasta que demos con las 7 bolas.

Hay varios listados de ciudades, más o menos completos. El que usé yo fue el básico de esta página: https://simplemaps.com/data/world-cities. Unas 13.000 ciudades. El formato es el siguiente:
```c
"city","city_ascii","lat","lng","country","iso2","iso3","admin_name","capital","population","id"
"Malishevë","Malisheve","42.4822","20.7458","Kosovo","XK","XKS","Malishevë","admin","","1901597212"
"Prizren","Prizren","42.2139","20.7397","Kosovo","XK","XKS","Prizren","admin","","1901360309"
"Zubin Potok","Zubin Potok","42.9144","20.6897","Kosovo","XK","XKS","Zubin Potok","admin","","1901608808"
"Kamenicë","Kamenice","42.5781","21.5803","Kosovo","XK","XKS","Kamenicë","admin","","1901851592"
"Viti","Viti","42.3214","21.3583","Kosovo","XK","XKS","Viti","admin","","1901328795"
"Shtërpcë","Shterpce","42.2394","21.0272","Kosovo","XK","XKS","Shtërpcë","admin","","1901828239"
"Shtime","Shtime","42.4331","21.0397","Kosovo","XK","XKS","Shtime","admin","","1901598505"
"Vushtrri","Vushtrri","42.8231","20.9675","Kosovo","XK","XKS","Vushtrri","admin","","1901107642"
"Dragash","Dragash","42.0265","20.6533","Kosovo","XK","XKS","Dragash","admin","","1901112530"
```

Cargamos a una lista las coordenadas de todas las ciudades:

```python
coords = []
with open("worldcities.csv","r") as f:
    f.readline()
    for line in f:
        cols = line.split(",")
        lat = float(cols[2].strip('"'))
        lng = float(cols[3].strip('"'))
        coords.append([lat,lng])
```

Definimos la función que hará la petición a server.php:

```python
import requests
import time

URL="https://34.253.120.147/dragonball/episodio1/server.php"

def check(lat,lng):
    data={ "lat":lat, "lng":lng }
    try:
        r = requests.post(URL, data=data, verify=False)
        if "city" in r.text:
            print(r.text)
    except:
        print("Exception.. sleeping 5 secs")
        time.sleep(5)
```

Por último, iteramos el listado de coordenadas:

```python
for lat,lng in coords:
    check(lat,lng)
```

Al principio la sensibilidad del radar era mucho más limitada, y había que multiplicar el numero de peticiones, de forma que se cubriese un area alrededor de cada coordenada. Para no morir en el intento, usamos multithreading (una librería DoS de python):

```python
OFFSET=0.015

POOLSIZE=500

# Función que procesa hasta POOLSIZE coordenadas, empezando en start
def doit(start):
    print("Processing %d starting at %d" % (POOLSIZE, start))
    for lat,lng in coords[start:start+POOLSIZE]:
        # La coordenada original
        check(lat,lng)
        # El cuadrado que rodea la coordenada original
        check(lat+OFFSET,   lng         )
        check(lat,          lng+OFFSET  )
        check(lat+OFFSET,   lng+OFFSET  )
        check(lat-OFFSET,   lng         )
        check(lat,          lng-OFFSET  )
        check(lat-OFFSET,   lng-OFFSET  )
        check(lat+OFFSET,   lng-OFFSET  )
        check(lat-OFFSET,   lng+OFFSET  )
        # Con un poco más de radio. La M50, vamos.
        check(lat               , lng + OFFSET*2  )
        check(lat               , lng - OFFSET*2  )
        check(lat + OFFSET*2    , lng             )
        check(lat - OFFSET*2    , lng             )
        check(lat + OFFSET*2    , lng + OFFSET*2  )
        check(lat + OFFSET*2    , lng - OFFSET*2  )
        check(lat - OFFSET*2    , lng + OFFSET*2  )
        check(lat - OFFSET*2    , lng - OFFSET*2  )

# Configuramos el número de subprocesos:
pool = Pool(processes=5)
# Cargamos los trabajos.. de 0 a numero de coordenadas, cada POOLSIZE elementos
pool.map(doit, range(0,len(coords),POOLSIZE))
```

Si todo va bien obtenemos las siguientes bolas:

```json
{"stars":1,"city":"Damasco","lat":33.513645,"lng":36.276762,"locInRadar":"<circle cx=\"150\" cy=\"150\" r=\"10\"><\/circle>"}
{"stars":2,"city":"Ronda","lat":36.745473,"lng":-5.161438,"locInRadar":"<circle cx=\"250\" cy=\"125\" r=\"10\"><\/circle>"}
{"stars":3,"city":"Guam","lat":13.440439,"lng":144.779184,"locInRadar":"<circle cx=\"125\" cy=\"270\" r=\"10\"><\/circle>"}
{"stars":4,"city":"Ulan Bator","lat":47.906641,"lng":106.895085,"locInRadar":"<circle cx=\"50\" cy=\"240\" r=\"10\"><\/circle>"}
{"stars":5,"city":"Estocolmo","lat":59.328694,"lng":18.068505,"locInRadar":"<circle cx=\"320\" cy=\"270\" r=\"10\"><\/circle>"}
{"stars":6,"city":"Reikiavik","lat":64.145144,"lng":-21.942496,"locInRadar":"<circle cx=\"80\" cy=\"80\" r=\"10\"><\/circle>"}
{"stars":7,"city":"Odessa","lat":46.482921,"lng":30.722892,"locInRadar":"<circle cx=\"30\" cy=\"280\" r=\"10\"><\/circle>"}
```

## Gimme tha flag

Comprobamos el nombre (DRGUERO), usando el servicio del puerto 9999:

```bash
$ echo DRGUERO | nc 34.253.120.147 9999
UAM{2f3c45a7fdd272de9f43836e5ca2f39c}
```

Como curiosidad, el inverso de ese md5 es: OPR4d4rftw


## Spam

[Julian J. M.](https://julianjm.com)
