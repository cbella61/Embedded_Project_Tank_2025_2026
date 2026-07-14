# Verifica di stampabilità al FabLab UniTrento

Verifica eseguita il 14 luglio 2026 sulle schede pubblicate dal FabLab. Il
carro va esportato e stampato **per moduli**, non come assieme completo.

## Ingombri CAD determinanti

| Modulo | Inviluppo nominale | Nota |
|---|---:|---|
| Guscio laterale continuo | 166 x 176 x 76 mm | Parte più critica sul piano XY |
| Tetto removibile con supporto torretta | 166 x 176 x circa 36 mm | Stesso ingombro XY del guscio |
| Piano inferiore | 160 x 170 x circa 13 mm | Supporto batteria integrato |
| Piano superiore | 160 x 170 x circa 3 mm | Aperture Arduino e pacco batteria PCB |
| Base rotante | diametro 100 mm | Stampare separatamente |
| Torretta, culla, coperchio culatta e fermagli | inferiori a 100 mm | Parti separate e orientabili singolarmente |

Le quote sono l'inviluppo geometrico nominale. Brim, skirt, supporti e distanza
di sicurezza dal bordo richiedono ulteriore spazio nel piano di stampa.

## Stampanti disponibili

| Stampante | Volume dichiarato | Materiali ammessi dal FabLab | Giudizio sul progetto |
|---|---:|---|---|
| [Bambu Lab A1 Mini](https://fablab.unitn.it/tools/bambu-lab-a1-mini-ams/) | 180 x 180 x 180 mm | PLA, PETG, TPU | Ingombro nominalmente sufficiente, ma restano solo 2 mm sul lato da 176 mm e 7 mm sul lato da 166 mm: non consigliata per guscio e tetto; adatta alle parti piccole |
| [Bambu Lab A1, cinque macchine](https://fablab.unitn.it/tools/bambu-lab-a1-ams/) | 256 x 256 x 256 mm | PLA, PETG, TPU | Consigliata; margine comodo e possibilità di distribuire i moduli su più macchine |
| [Bambu Lab H2D](https://fablab.unitn.it/tools/bambu-lab-h2d/) | 325 x 320 x 325 mm con un ugello | PLA, PETG, TPU | Consigliata; grande margine per guscio e tetto |
| [Prusa XL](https://fablab.unitn.it/tools/prusa-xl/) | 360 x 360 x 360 mm | PLA, PETG, TPU | Consigliata; massimo margine disponibile |

L'[elenco ufficiale delle macchine](https://fablab.unitn.it/tools/) comprende
anche la Wanhao Duplicator D7 Plus. Non è necessaria per le parti strutturali
grandi del carro, che sono state progettate per FDM con ugello da 0,4 mm.

## Scelta pratica

- Prima scelta: una delle Bambu A1 da 256 mm; consente anche di stampare più
  moduli in parallelo.
- Alternative con più margine: H2D o Prusa XL.
- A1 Mini: usare solo per base rotante, torretta, coperchio della culatta,
  fermagli e provini. Guscio e tetto entrano soltanto nominalmente e non lasciano
  spazio affidabile per brim o tolleranze del piatto.
- PLA: adatto al primo controllo dimensionale rapido.
- PETG: preferibile per il prototipo funzionale grazie alla maggiore tenacità,
  dopo aver verificato giochi e ritiri sui provini.
- TPU: non previsto per i moduli rigidi; può servire solo per eventuali parti
  flessibili aggiunte in seguito.

## Orientamento e prove prima delle parti lunghe

1. Stampare prima i provini della sede D dello stepper, dei fori M2,5/M3/M4 e
   del gioco della guida rotante.
2. Stampare guscio e tetto con la faccia piana maggiore appoggiata al piatto,
   salvo diversa indicazione del tecnico del FabLab dopo lo slicing.
3. Usare almeno quattro perimetri per guscio, tetto e parti della torretta; il
   riempimento va scelto nello slicer dopo aver controllato peso e durata.
4. Controllare nello slicer che le feritoie 42 x 4 mm, le asole dei cavi e il
   ponte da 4 mm non generino pareti isolate.
5. Stampare guscio mobile e coperchio della culatta come prova accoppiata prima
   di stampare il resto della torretta.
6. Non considerare definitiva la ricarica finché il foro posteriore del
   solenoide reale non è stato misurato e provato a mano, senza alimentazione.

## Esito

Il progetto è **stampabile per ingombro** sulle Bambu A1, H2D e Prusa XL del
FabLab. Per le parti da 166 x 176 mm la A1 Mini è tecnicamente al limite e non è
la scelta raccomandata. Il giudizio resta condizionato ai provini delle
tolleranze e alla verifica fisica di stepper, SG90, cablaggio e solenoide.
