# Riferimento locale stepper 28BYJ-48

Fonte analizzata il 13 luglio 2026:
`C:\Users\selmi\Downloads\stepper.pdf`.

Il PDF è un datasheet generico del **28BYJ-48 5 V**. È utile come riferimento,
ma non sostituisce la misura del motore fisico perché esistono varianti tra
produttori.

## Quote leggibili nel disegno

- corpo cilindrico: Ø28 mm;
- profondità nominale del corpo: 19 mm;
- interasse dei due fori: 35 ± 0,2 mm;
- due fori nominali: Ø4,2 mm;
- raggio esterno delle alette attorno ai fori: R3,5 mm;
- albero nominale: Ø5 mm con una faccia piana;
- quota trasversale della parte piatta: 3 mm nel disegno;
- sporgenza complessiva albero: 10 ± 0,5 mm;
- tratto utile indicato: 6 ± 0,2 mm;
- collare frontale indicato: 1,5 mm.

Il disegno conferma quindi i valori provvisori già usati per interasse 35 mm e
fori Ø4,2 mm. Non conferma invece che l'esemplare reale dell'utente abbia
esattamente la stessa faccia piana e la stessa sporgenza.

## Conseguenza per l'adattatore

Un foro tondo Ø5,3 mm non può trasmettere la coppia dello stepper. Per il
prototipo serve una delle seguenti soluzioni, da scegliere dopo la misura
dell'albero reale:

1. sede a D aderente all'albero;
2. mozzo con grano laterale;
3. mozzo a morsetto diviso.

Prima di modificare il CAD vanno misurati sul motore fisico:

- diametro massimo dell'albero;
- distanza tra faccia piana e lato opposto;
- lunghezza utile realmente inseribile nel mozzo.

## Vecchio riferimento disponibile

È presente anche
`C:\Users\selmi\Downloads\Carroarmato\STL\adattatore_stepper_torretta_v2_3_RC2.stl`.
La mesh ha ingombro circa 73 x 63,22 x 22 mm ed è utile come riferimento
geometrico, ma non è parametrica e le sue quote interne non vanno considerate
confermate senza confronto con il motore reale.
