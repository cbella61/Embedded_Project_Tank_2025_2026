# Predisposizione di ricarica manuale

La revisione 4 contiene una predisposizione modificabile per caricare a mano un
solo elemento morbido e inerte. Non è una culatta a tenuta e non certifica il
funzionamento del solenoide reale.

## Parti CAD

- finestra posteriore centrale larga 14 mm nel guscio mobile;
- asola contigua sul tetto, lunga 12 mm;
- tasca superiore 30 x 15 x 2 mm con rinforzo a U inferiore da 0,8 mm;
- coperchio separato a L, arretrato di 0,3 mm sui bordi e ribassato di 0,2 mm;
- due M2,5 x 6 con passaggi Ø2,7 mm, prefori Ø2,2 mm e teste svasate;
- guida interna coassiale Ø11/Ø8 x 8 mm, sospesa sotto il tetto del guscio;
- legamento nominale di 3 mm fra finestra della culatta e tacca cavo 6 x 4 mm.

Il coperchio e il guscio sono due moduli distinti nell'F3D. Il coperchio chiuso
resta 0,2 mm sotto l'inviluppo originale del guscio mobile, perché dietro alla
torretta il margine durante l'elevazione è ridotto. Due longheroni e una traversa
sotto la tasca portano lo spessore locale nominale a 1,3 mm senza chiudere
l'asola di accesso.

## Procedura di servizio prevista

1. Portare azimut a 0° ed elevazione a 0°.
2. Togliere alimentazione a stepper, servo e solenoide.
3. Svitare le due M2,5 superiori e sollevare il coperchio a L.
4. Inserire dall'alto/posteriore soltanto un elemento morbido e inerte già
   misurato e collaudato; accompagnarlo con uno spingitore non metallico.
5. Rimontare il coperchio, controllare che le teste siano a filo e solo dopo
   riabilitare i movimenti.

L'inviluppo provvisorio del CAD è Ø7 x 10 mm. Non è la quota definitiva del
proiettile e non va usato come autorizzazione alla prova.

## Dati ancora obbligatori

Prima di considerare la funzione realmente fattibile occorre misurare:

- diametro e lunghezza dell'elemento morbido/inerte;
- materiale e deformabilità;
- diametro utile del foro posteriore reale del solenoide;
- continuità e coassialità del foro con la canna Ø8 mm;
- posizione dei terminali, del plunger e di eventuali ostacoli interni.

Nel riferimento CAD il solenoide è attraversato da un foro ideale. Questo non
dimostra che il componente fisico sia aperto: se il retro è chiuso o occupato
dal plunger, la ricarica coassiale non funziona e servirà un accesso diverso fra
solenoide e canna.

## Prove richieste

- stampare prima soltanto guscio mobile e coperchio;
- verificare gioco 0,3 mm, svasature e accesso utensile;
- provare a mano l'inserimento con solenoide non alimentato e fuori dal carro;
- rimontare e controllare elevazione completa da -10° a +35°;
- assicurarsi che coperchio e viti non sporgano;
- non comandare il solenoide con coperchio aperto.
