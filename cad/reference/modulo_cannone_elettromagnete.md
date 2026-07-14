# Modulo cannone con elettromagnete

Riferimento fotografico ricevuto il 13 luglio 2026:

`e344e3a2-ca87-48e2-a202-04f4933ae241/1-Photo-1.jpg`

## Requisiti funzionali confermati

- La PCB con elettromagnete, il relativo meccanismo e la canna
  devono essere incastrati nella parte mobile della torretta.
- Tutto questo gruppo deve ruotare insieme alla culla comandata dai due servo.
- I fori già presenti nella PCB devono essere usati per il
  fissaggio; non bisogna inventare una diversa foratura.
- Lo stepper continua a ruotare l'intera torretta nel piano XY.
- La PCB 50 x 50 x 2 mm del modulo di sparo fa parte del gruppo mobile.

## Quote confermate

- materiale/tipo della base: PCB, non piastra metallica;
- PCB: 50 x 50 x 2 mm;
- diametro dei quattro fori: 3,5 mm;
- centro di ogni foro a 5 mm dai due bordi adiacenti della PCB; le coordinate
  rispetto al centro della PCB sono quindi X = ±20 mm e Y = ±20 mm;
- cannone completo nella zona comprendente il solenoide: diametro esterno
  massimo 20 mm;
- canna cilindrica/tubolare: diametro esterno 10 mm e parete spessa 1 mm,
  quindi diametro interno 8 mm;
- sporgenza della canna dall'uscita del cannone: 46 mm.
- altezza totale dalla faccia inferiore della PCB alla sommità del gruppo:
  23 mm.

## Quote leggibili ma non ancora confermate

- ingombro laterale del corpo elettromagnete: circa 25 mm;
- larghezza indicata nella vista dall'alto: circa 30 mm;

Questi ultimi valori non devono ancora essere usati per generare la geometria.

## Scelta di assemblaggio da verificare sul prototipo

La PCB verrà centrata sulla culla mobile e fissata mediante i quattro fori
confermati. La posizione definitiva dell'asse di elevazione rispetto al modulo
potrà essere regolata nei parametri dopo una verifica del bilanciamento reale.
