# Checkpoint CAD carro armato - revisione 5 - 14 luglio 2026

Questo file e il riferimento di ripartenza per il modello 3D. Continuare dalla
revisione 5 e non dai vecchi export v3/v4.

## File principali

- Generatore parametrico: `cad/source/fusion360_tank_generator/TankGenerator.py`
- Parametri: `cad/source/fusion360_tank_generator/parameters.json`
- Assieme Fusion modificabile:
  `cad/exchange/carro_armato_assieme_completo_modificabile_v5_cinematica_stepper_servo_M2_5.f3d`
- Assieme neutro STEP:
  `cad/exchange/carro_armato_assieme_completo_modificabile_v5_cinematica_stepper_servo_M2_5.step`
- Procedura di montaggio: `cad/ASSEMBLAGGIO_FATTIBILITA.md`

Export verificati il 14/07/2026 alle 04:48:42:

- F3D, 1.466.401 byte, SHA-256
  `90D5A0E814A174D67A71957908B967B2F8561A92BCFD85B873FE6D34BAD55FC7`
- STEP, 1.155.363 byte, SHA-256
  `20049E4C1D255B6B6D5F500C91B3A6FDD3DD61541E9B710959126093D1FD8C8A`

## Cinematica corretta

- Il tetto dell'elettronica resta fisso durante il funzionamento ed e
  removibile soltanto per manutenzione.
- Lo statore del 28BYJ-48 e fissato sotto il tetto.
- Solo rotore e albero dello stepper ruotano; l'albero trascina la base D100 e
  tutta la parte fissa della torretta.
- Il giunto di azimut e attorno a Z e va da -180 a +180 gradi: 360 gradi
  complessivi, senza rotazione continua.
- Il movimento di azimut e stato azionato in Fusion: torretta e D100 ruotano,
  mentre tetto e scafo restano fermi.
- I corpi dei due SG90 sono solidali alla torretta fissa che ruota con lo
  stepper.
- I due SG90 sono coassiali sull'asse X e muovono soltanto culla, PCB del
  cannone, solenoide, canna e guscio mobile. Limiti CAD: -10 / +35 gradi.

## SG90 e fissaggio M2,5

- Corpo servo di riferimento: 22,7 x 12,2 x 27 mm.
- Ingombro totale delle alette: 32,3 mm; sporgenza reale circa 4,8-5 mm.
- Spessore delle alette reali: 2 mm.
- Il foro reale accetta una vite M2,5.
- Centro foro modellato a circa 1,75 mm dall'estremita libera: 0,5 mm di
  materiale oltre il raggio della vite e circa 1,8 mm verso il corpo.
- Nelle pareti della torretta ci sono asole 5 x 2,9 mm, spostate verso
  l'esterno per non indebolire la finestra del servo.
- Montaggio previsto: testa M2,5 bassa dal lato interno, dado dal lato esterno.

## Cornetti e guance mobili

- Usare i due cornetti originali SG90 a croce, uno per lato.
- I piccoli fori del cornetto non sono riprodotti nel CAD: appoggiare il
  cornetto reale sulla guancia e usarlo come dima con viti autofilettanti a
  punta.
- Il foro centrale resta accessibile per la vite del millerighe SG90.
- Le guance stampate 09A e 09B sono dischi diametro 34 mm, spessore 4 mm, con
  accesso centrale diametro 10 mm e ripiani regolabili con asole 5 x 2,9 mm.
- Il guscio mobile del cannone ha scassi laterali diametro 35 mm per non
  interferire con le guance.
- Le vecchie barrette stampate e i vecchi perni lisci non si usano piu.

## Passaggio cavi

- I connettori dei due SG90 sono circa 7 x 3 mm.
- Il connettore del cannone e circa 5 x 3 mm; il suo fascio cavi puo occupare
  circa 7 x 3 mm.
- I connettori vanno inseriti uno alla volta nel passaggio comune prima di
  fissare definitivamente la torretta.
- Lasciare un'ansa di servizio nel canale circolare sotto la torretta e
  verificare manualmente entrambe le estremita della corsa prima di abilitarle
  nel software.

## Stato verifiche digitali

- `TankGenerator.py`: compilazione Python superata.
- `parameters.json`: JSON valido, revisione 5.
- STEP: presenti statore, rotore/albero, D100, cornetti sinistro e destro,
  guance 09A/09B e guscio mobile 14.
- Controllo whitespace delle sorgenti e della documentazione superato.

## Prove fisiche prima della stampa completa

1. Stampare una piccola provetta con una sola finestra servo e due asole M2,5.
2. Inserire il servo reale e controllare il gioco delle alette da 2 mm.
3. Montare cornetto reale, guancia e vite centrale; verificare che lo stack
   laterale non strisci durante tutta l'elevazione.
4. Provare il passaggio dei tre connettori e l'ansa cavi a -180 e +180 gradi.
5. Confermare sul pezzo reale interasse e diametro dei fissaggi del 28BYJ-48.
6. Soltanto dopo queste prove stampare guscio completo e torretta completa.

Le quote della PCB fissa, del driver e di alcuni passaggi futuri dei motori
restano modificabili e vanno confermate sui componenti fisici.
