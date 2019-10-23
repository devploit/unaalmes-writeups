# UAM - Dragon Ball 3 - 15/10/2019 - julianjm

## Enunciado
[Versión completa](https://unaalmes.hispasec.com/challenges#EPISODIO%203). Nos proporcionan un binario ELF64 para analizar e intentar descubrir la flag.

## Análisis inicial
A primera vista, tenemos una función `main` de lo más sencillo. Inicializa un array con una serie de valores, les hace un XOR con un valor en la función `decrypt` y utiliza ese resultado para compararlo con la entrada del programa.

Nos damos cuenta rápido de que no todo va a ser tan fácil (n0t_s0_34sY). Por alguna razón está fallando al comparación de cadena con strcmp, pero solamente cuando _no_ estamos en modo debug. Lo único que tenemos claro es la longitud de la flag, 11.

![He visto cosas](img/uam_he_visto_cosas.jpg?raw=true)

## glibc __init_array

Pasan cosas antes del `main`. Durante la inicialización de la libc se ejecutan diversas funciones, entre ellas las definidas en la sección `__init_array` del ELF. Aquí está, por ejemplo, la ejecución de constructores de los objetos declarados de forma global, que tienen que estar inicializados cuando se empiece a ejecutar `main`.

![__init_array](img/uam_init_array.png?raw=true)

Tirando del hilo llegamos al constructor de la clase vector, que no hace otra cosa que reemplazar la función `strcmp`, usada para comparar la flag en la función `main`, por otra que analizaremos más adelante.

![__init_array](img/uam_vector_constructor.png?raw=true)

Este reemplazo, no obstante, solo ocurre bajo cierta condición, que no existan en la sección de código más de 6 bytes de valor `0xCC`. Este byte codifica la instrucción `int 3`, que es utilizada por los debugger para meter breakpoints por software. De esta forma, si hemos definido alguno (por ejemplo al inicio del `main`), el número de bytes será superior a 6 y no reemplazará nada, dejándonos un poco locker.

Una solución, es utilizar breakpoints por hardware, aunque están limitados en número. Estos breakpoints se basan en registros de la CPU y no en la modificación de la memoria para incluir llamadas a `int 3`, por lo que no serían detectados por esta técnica antidebugging.

## VM

Llegados a este punto podemos debugear la función reemplazo de `strcmp`. Esta función crea una secuencia de enteros, en los que inserta el string que recibe como primer parámetro. Posteriormente crea un objeto de la clase `xd`, en cuyo constructor sucede la magia.

![__init_array](img/uam_xd_xd.png?raw=true)

![__init_array](img/uam_xd_run.png?raw=true)

Se trata de una máquina virtual, que valua una cadena de código formada por opcodes y datos. Hay diferentes opcodes definidos, JMP, MOVRV, XOR, EQ, JMP_NEQ. Analizando cada función, vemos qué datos utiliza y cómo los procesa. La operación `EQ`, por ejemplo, establece un registro interno a 1 si la igualdad (entre un valor definido en la instrucción y un valor de la memoria) es cierta.

![__init_array](img/uam_xd_cmp_eq.png?raw=true)

Un pequeño script en python nos permitirá ver el código más claramente en un formato similar al ensamblador. Como la flag forma parte el código, utilizaremos para este desensamblado una flag incorrecta: "123456789ab"

``` as
  0: JMP 3
  2: RETURN
  3: MOVRV mem[0], 11    # La longitud de la flag
  6: EQ mem[0], 11
  9: JMP_NEQ 2
 11: MOVRV mem[0], 49    # Primer caracter de la flag, '0'
 14: XOR [0], 210
 17: EQ mem[0], 149
 20: JMP_NEQ 2
 22: MOVRV mem[0], 50    # Segundo caracter de la flag '1'
 25: XOR mem[0], 214
 28: EQ mem[0], 230
 31: JMP_NEQ 2
 33: MOVRV mem[0], 51
 36: XOR mem[0], 135
 39: EQ mem[0], 211
 42: JMP_NEQ 2
 44: MOVRV mem[0], 52
 47: XOR mem[0], 234
 50: EQ mem[0], 181
 53: JMP_NEQ 2
 55: MOVRV mem[0], 53
 58: XOR mem[0], 212
 61: EQ mem[0], 188
 64: JMP_NEQ 2
 66: MOVRV mem[0], 54
 69: XOR mem[0], 2
 72: EQ mem[0], 50
 75: JMP_NEQ 2
 77: MOVRV mem[0], 55
 80: XOR mem[0], 27
 83: EQ mem[0], 43
 86: JMP_NEQ 2
 88: MOVRV mem[0], 56
 91: XOR mem[0], 9
 94: EQ mem[0], 98
 97: JMP_NEQ 2
 99: MOVRV mem[0], 57
102: XOR mem[0], 172
105: EQ mem[0], 157
108: JMP_NEQ 2
110: MOVRV mem[0], 97
113: XOR mem[0], 16
116: EQ mem[0], 126
119: JMP_NEQ 2
121: MOVRV mem[0], 98
124: XOR mem[0], 170
127: EQ mem[0], 205
130: JMP_NEQ 2
132: MOVRV mem[19], 1
135: RETURN
```

Vemos que la primera comprobación que realiza es si la longitud de la flag suministrada es igual a 11. En caso contrario, saltaría a la posición 2 y retornaría. El registro interno valdría 0 en este punto, por lo que la función retornaría incorrecto.

Posteriormente, carga en memoria el valor 49, correspondiente al primer caracter de la flag, en el ejemplo '0'. Le realiza una operación XOR con el valor 210 y compara el resultado con 149. Si coincide, pasa a analizar el siguiente caracter. Para averiguar el caracter necesario para que la comparación sea correcta, nos basta con realizar la operación 149 xor 210, que da como resultado 71. En ASCII corresponde al caracter 'G'.

Repitiendo la operación con el resto de la flag, obtenemos: *G0T_h00k1ng*

Convertimos al formato habitual (md5), y tenemos la flag definitiva:

UAM{7b02cd3d2d3cea80359cf600799413d3}