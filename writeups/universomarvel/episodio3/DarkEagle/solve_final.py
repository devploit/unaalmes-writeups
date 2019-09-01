import argparse
from gmplot import gmplot
import csv
import sys
# Us: python solve_final.py fitxer_coordenades.txt

def banner():
    print("\n\
                                                                                                                                        \n\
  /$$$$$$                            /$$$$$$$                                                      /$$                        		\n\
 /$$__  $$                          | $$__  $$                                                    | $$                        		\n\
| $$  \__/  /$$$$$$   /$$$$$$       | $$  \ $$  /$$$$$$   /$$$$$$$  /$$$$$$  /$$   /$$  /$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$ 		\n\
| $$ /$$$$ /$$__  $$ /$$__  $$      | $$  | $$ /$$__  $$ /$$_____/ /$$__  $$| $$  | $$ /$$__  $$|_  $$_/   /$$__  $$ /$$__  $$		\n\
| $$|_  $$| $$$$$$$$| $$  \ $$      | $$  | $$| $$$$$$$$| $$      | $$  \__/| $$  | $$| $$  \ $$  | $$    | $$$$$$$$| $$  \__/		\n\
| $$  \ $$| $$_____/| $$  | $$      | $$  | $$| $$_____/| $$      | $$      | $$  | $$| $$  | $$  | $$ /$$| $$_____/| $$      		\n\
|  $$$$$$/|  $$$$$$$|  $$$$$$/      | $$$$$$$/|  $$$$$$$|  $$$$$$$| $$      |  $$$$$$$| $$$$$$$/  |  $$$$/|  $$$$$$$| $$      		\n\
 \______/  \_______/ \______/       |_______/  \_______/ \_______/|__/       \____  $$| $$____/    \___/   \_______/|__/      		\n\
                                                                             /$$  | $$| $$                                    		\n\
                                                                            |  $$$$$$/| $$                                    		\n\
                                                                             \______/ |__/                                    		\n\
                                                                                             Author: DarkEagle\n\n\n")

def separar():
    with open(args.file,'r') as fo:
        start=1
        op=''
        cntr=1
        for x in fo.read().split('\n'):
            if(x=='19.1399952, -72.3570972'):   # Coordenades que es repeteixen, seguent digit
                if (start==1):
                    with open(str(cntr)+'bloc.txt','w') as opf:
                        opf.write(op)
                        opf.close()
                        op=''
                        cntr+=1
                else:
                    start=1
            else:
                if (op==''):
                    op=x
                else:
                    op=op + '\n' + x
        fo.close()
        print 'Separacio completa, fitxers totals: ',cntr-1
        return (cntr-1)

def pintar_fitxer_coordenades(nom_fitxer):

    with open(nom_fitxer) as csvfile:
        data = [(float(x), float(y)) for x, y in csv.reader(csvfile, delimiter= ',')]

    #print(data)

    # Place map Definim la posicio del mapa i el zoom
    gmap = gmplot.GoogleMapPlotter(26.9009488,-43.857073717, 3)

    golden_gate_park_lats, golden_gate_park_lons = zip(*data)
    gmap.plot(golden_gate_park_lats, golden_gate_park_lons, 'cornflowerblue', edge_width=10)

    # Draw
    gmap.draw(nom_fitxer+'.bloc.html')
    
banner()
parser = argparse.ArgumentParser(description='solve_final.py')
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-f', '--file', help='File to decode', required=True)
args = parser.parse_args()

num_fitxers=separar()
num_fitxer=1
while (num_fitxer < num_fitxers):
    pintar_fitxer_coordenades(str(num_fitxer)+'bloc.txt')
    num_fitxer+=1

print("Programa acabat: Els fitxers resultants (.html) es troben al directori del programa")