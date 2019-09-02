#Copiame en un archivo .py, ejecutame con python3
#
#
#
try:
    import os
except ImportError:
    print("Error importing 'os'")
    exit()
try:
    import hashlib
except ImportError:
    print("Error importing 'hashlib'")
    exit()
    
    
if os.getuid() is not 0:
    print("Necesito sudo para montar particiones y crear directorios!")
    exit()
    
print("Una al Mes #5 Write-Up")
print("Write-up Interactivo Por Blueudp\n")
print("Lo primero que nos encontramos en la plataforma es un texto que dice:")
print("""Con todo el dinero robado, necesitamos escapar dando una distracción 
a la policia. Para ello, hace falta encontrar la bomba programada en el \033[1;33;40mfirmware
del sistema informático. Una vez resuelta, podremos acceder al servidor\033[0m, donde 
tras buscar bien, conseguiremos la flag final y escaparemos con el premio. [Pulsa Enter]: """)
f = input(" ")
print("Posteriormente, descargamos el '.zip' que nos ofrecen [Pulsa Enter]: ")
f = input(" ")

os.system("clear")

print("Downloading .zip...")

os.system("wget https://unaalmes.hispasec.com/files/92b2478b76c8ccf43f8fb2c4814faab3/firmware.zip")
os.system("clear")

print("Descargado!!! [Pulsa Enter]: ")
f = input(" ")
print("Lo siguiente, lógicamente, es descomprimir el zip: ")
print("unzip firmware.zip\n")

os.system("unzip firmware.zip")

print("""\nUna vez descomprimido vemos un archivo '.raw', le hacemos un file
y nos damos cuenta que es una partición ext4""")
print("\nfile backup.raw")

os.system("file backup.raw")

print("\nAl ser una partición ext4, procedemos a montarla [Pulsa Enter]: ")
f = input(" ")
print("Montada!")

os.system("mkdir /media/DISK1")
os.system("sudo mount -t ext4 backup.raw /media/DISK1")

f = input("Presione enter para hacer un 'ls -a' y ver los archivos: ")
print("\n")

os.system("ls -a /media/DISK1")

print("""El archivo '.bomb' es la bomba, asi que necesitamos el código, para ello
primero la desempaquetaremos con upx 'upx -d .bomb' [Pulsa Enter]: """)
f = input(" ")

os.system("sudo upx -d /media/DISK1/.bomb")

print("Posteriormente, hacemos un strings para ver la pass [Pulsa Enter]: ")
f = input(" ")

os.system("strings /media/DISK1/.bomb")

print("Por el medio del fichero pone 'italy', prueba a insertar esa pass en la bomba. [Pulsa Enter] (Tendrás que esperar 1 min): ")
f = input(" ")

os.system("/media/DISK1/.bomb")

print("""\nBien!, tienes un string algo raro, si le quitas las barra bajas
verás que es un hash md5 el cual, una vez crackeado, contiene la ip del server  [Pulsa Enter]: """)
f = input(" ")
print("La ip es http://95.216.138.194/ (crackeado con 'https://www.md5online.es/')     [Pulsa Enter]: ")
f = input(" ")
print("Procedemos a entrar [Pulsa Enter]: ")
f = input(" ")
os.system("wget https://95.216.138.194")
print("\nwget dice que el certificado del propietario con coincide con el host que pusimos... Vamos a ver cual es el propietario [Pulsa Enter]: ")
f = input(" ")
print("Al pasar la ip por 'https://www.sslshopper.com', nos dice que el propietario es 'lacasadepapel.cloud', probaremos a asignar la ip que nos dieron con ese propietario a ver si funciona [Pulsa Enter]: ")
f = input(" ")
print("Para ello, añadimos esta linea a /etc/hosts: '95.216.138.194 lacasadepapel.cloud' <- copiala [Pulsa Enter para abrir /etc/hosts/]: ")
f = input(" ")

os.system("sudo nano /etc/hosts")

print("Una vez editado, probamos a hacer una petición a 'lacasadepapel.cloud', pero con la opción de no revisar el certificado, disponible en curl (-k) y wget (--no-check-certificate) [Pulsa Enter]: ")
f = input(" ")
os.system("curl -k https://lacasadepapel.cloud")
print("\nRayos!, un index con dos audios, procedemos a descargarlos [Pulsa Enter]: ")
f = input(" ")

os.system("wget --no-check-certificate https://lacasadepapel.cloud/audio/Bella_Ciao.mp3")
os.system("wget --no-check-certificate https://lacasadepapel.cloud/audio/Bella_Cia0.wav")

print("Si te fijas, en el .wav hay un morse algo flojito, y en el mp3 está la misma canción, pero sin el morse")
print("Hay un tipo de auriculares 'con supresión de ruido' que captan el sonido por el micrófono y lo emiten (con las ondas al revés) por los altavoces, como nosotros tenemos dos audios iguales, pero con un pequeño sonido diferente podemos aplicar la misma técnica, y así, quedará el morse limpio [Pulsa Enter]: ")

f = input(" ")

print("¿Como se hace eso?, abre audacity y añade los dos archivos de sonido, selecciona uno de ellos y ve a efectos > invertir, no notarás nada, pero al darle a play.. Solo se escucha el morse!, (al principio del audio no se escuhará nada), asi que solo queda decodearlo, para ello vamos a una web para ello, el resultado será: 'laflagesbellaciaoremoenmd5' , así que hasheamos 'bellaciaoremo', añadimos UAM{} y... Listo! [Pulsa Enter]: ")

f = input(" ")
hashear=""
while "bellaciaoremo" not in hashear:
    hashear = input("Inserta bellaciaoremo para cifrarlo en md5: ")
    if "bellaciaoremo" in hashear:
        m = hashlib.md5()
        m.update(hashear.encode('utf-8'))
        print("\nEl hash es: '{}'".format(m.hexdigest()))
        print("\nGracias por leer este chapuzero write-up, espero que hayais aprendido con el.\nun saludo a los admins y a los compañeros de UAM!\n yo me voy a ver la casa de papel")
        exit()  
    else:
        print("Esa no es la string a cifrar!")
