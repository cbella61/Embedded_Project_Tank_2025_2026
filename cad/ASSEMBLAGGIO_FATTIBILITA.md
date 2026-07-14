# Studio di fattibilità dell'assemblaggio

Stato: verifica preliminare aggiornata il 14 luglio 2026 per la generazione
dell'assieme revisione 5 con torretta azimutale fisicamente supportata. Le quote indicate come
provvisorie devono essere provate sui componenti reali prima della stampa
definitiva.

## Verdetto

L'assemblaggio è fattibile come prototipo con la struttura corrente:

- guscio laterale continuo da Z=0 a Z=76 mm;
- due piani interni;
- supporto batteria stampato nello stesso corpo del piano inferiore;
- tetto e statore dello stepper fissi rispetto allo scafo durante l'uso;
- rotore/albero separato che trascina la sola base D100 e la torretta;
- sola parte superiore della torretta rotante su base diametro 100 mm;
- rondella assiale esterna alla pista cavi, guida radiale e quattro fermagli
  anti-sollevamento removibili;
- quattro M3 accessibili dall'alto per togliere tetto e torretta;
- SG90 inseribili lateralmente e fissati dalle alette reali da 2 mm con M2.5;
- cornetti a croce reali accoppiati a due guance stampate regolabili sotto la
  culla da 54 mm;
- modulo cannone removibile dall'alto;
- cavi instradati verso il primo piano con un'ansa anulare controllata;
- foro di servizio 10 x 10 mm sul piano inferiore;
- tre feritoie di ventilazione anteriori e tre posteriori.

Il giudizio è **GO condizionato per un prototipo di verifica**, non ancora per
una stampa definitiva completa. Prima vanno verificati sul pezzo reale la sede
D di trasmissione, l'attrito della rondella, l'accoppiamento dei
due SG90 e delle guance, gli ingombri delle PCB e l'ansa dei cavi.

## Preparazione

1. Stampare piccoli provini dei prefori M2,5, dei fori M3 e delle sedi dado.
2. Provare i dadi M3 nelle sedi da 5,8 mm tra facce e 2,6 mm di profondità.
3. Eliminare bave dai passaggi 9 x 7 mm e 6 x 4 mm senza allargarli prima di
   avere provato i connettori reali.
4. Verificare che il guscio 166 x 176 x 76 mm entri nella stampante. Su un
   piano 220 x 220 mm entra, ma è consigliabile un brim per gli angoli.
5. Inserire i dadi prigionieri prima di chiudere i sottoassiemi.
6. Stampare prima un provino corto della sede D diametro 5,4 mm con quota al
   piatto 3,2 mm. Se il motore entra con troppo gioco, correggere il solo
   parametro di tolleranza prima di stampare la base diametro 100 mm.
7. Preparare la rondella DI 76 / DE 94 / spessore 0,8 mm: PTFE o POM sono
   preferibili; PETG o nylon stampati sono adatti alla prima prova. Provare
   anche la sede ribassata da 0,3 mm con 0,2 mm di gioco radiale per lato.
8. Usare per lo stepper due vere viti M4 a testa svasata 90°, diametro testa
   non superiore a 8,4 mm. Una testa cilindrica o bombata bloccherebbe la base.

## Sequenza di montaggio

### 1. Piano inferiore e telaio

1. Fissare il piano inferiore alle due aste mediante le quattro asole 10 x
   5 mm e le fascette.
2. Far passare i cavi dei motori DC prima di chiudere il vano.
3. Inserire la batteria nella vaschetta Sud-Ovest già stampata insieme al piano
   inferiore; la piastra da 3 mm ne costituisce il fondo.
4. Montare Arduino UNO R4 WiFi e shield a Nord-Est, con jack DC verso Sud.
5. Provare motori e alimentazione prima di aggiungere il secondo piano.

Il supporto batteria non richiede viti o colla. Tra la sommità delle sue pareti
e il piano superiore restano 23 mm: altezza della batteria, connettore e
interferenza verticale con il pacco batterie PCB devono essere provati sul
reale. Le colonnine Arduino devono ancora essere definite.

### 2. Guscio continuo e piano superiore

1. Calare dall'alto il guscio laterale continuo attorno al piano inferiore.
2. Montare driver e PCB sul piano superiore prima di inserirlo, se i loro dadi
   saranno accessibili soltanto dal basso.
3. Far scendere il case batterie separato della PCB cannone attraverso
   l'apertura 60 x 33 mm.
4. Posare il piano superiore sulle quattro colonnine.
5. Allineare le quattro linguette interne del guscio e inserire dall'alto
   quattro M2,5 x 8.
6. Lasciare libera l'apertura Arduino 25 x 25 mm per i cavi della torretta.
7. Non coprire il nuovo foro inferiore 10 x 10 mm centrato in X=-0,5 mm,
   Y=25 mm: serve come ulteriore accesso vicino all'Arduino.
8. Controllare che le tre feritoie 42 x 4 mm sul fronte Nord e le tre sul retro
   Sud non siano ostruite da cablaggi sciolti.

### 3. Tetto, stepper e base rotante

1. A banco, inserire dal basso i quattro dadi M3 dei fermagli nelle tasche del
   tetto e trattenerli temporaneamente perché non possano cadere.
2. Fissare lo statore dello stepper sotto il tetto. Le due teste M4 90° devono
   entrare nelle svasature Ø8,4 x 2,1 mm e risultare perfettamente a filo.
3. Posare la rondella assiale DI 76 / DE 94 nella sua sede anulare ribassata da
   0,3 mm, fuori dalla pista dei cavi. Non mettere rondelle o viti nella corona
   r23,5-r32,5.
4. Infilare la base rotante diametro 100 mm sul rotore/albero D separato. Il
   piatto della sede deve combaciare col piatto dell'albero: non forzare e non
   alesare a caso.
5. Verificare che il labbro fisso r34,5-r36,5 entri nella gola con 0,3 mm di
   gioco radiale per lato e che la base appoggi sulla rondella, non sull'albero.
   L'impegno nominale è 2,1 mm e resta 1,7 mm al massimo sollevamento.
6. Portare i fili nella pista prima di montare i fermagli.
7. Avvitare i quattro fermagli M3 Est/Ovest/Nord/Sud fra le rispettive coppie
   di spallamenti antirotazione. Le linguette devono
   sovrapporsi al disco di 1,5 mm lasciando 0,4 mm in verticale: non devono
   stringere né frenare la rotazione.
8. Inserire dall'alto i quattro dadi della base D100, quindi fissare il telaio
   superiore con il pattern a raggio 19 mm. I quattro distanziali da 6 mm
   mantengono il telaio almeno 2,6 mm sopra i
   fermagli fissi durante tutta la rotazione.
9. Ruotare a mano la base completa: tetto, rondella, guida, statore e fermagli
   devono restare fissi; devono muoversi soltanto rotore/albero, base D100,
   telaio, servo e cannone. Se si muove il tetto, il vincolo di azimut è
   montato o simulato sul componente sbagliato.

Il profilo D nominale è diametro 5 mm con quota al piatto 3 mm. La sede CAD
aggiunge 0,2 mm di gioco. Con la rondella nella sede l'impegno teorico è 5,5 mm
e resta circa 5,1 mm al massimo sollevamento; lunghezza e inizio reale del
piatto dell'albero devono comunque essere misurati sul motore.

### 4. Due SG90 e culla mobile

1. Togliere i due cornetti dai servo.
2. Portare entrambi gli SG90 nella stessa posizione neutra via software.
3. Infilare ogni connettore 7 x 3 mm nella rispettiva finestra e poi nel
   passaggio comune, prima di bloccare il servo.
4. Inserire i servo dall'esterno verso il centro.
5. Sistemare ogni nastro 4 x 1 mm nella sua diramazione senza schiacciarlo.
6. Allineare le alette reali spesse 2 mm alle asole 5 x 2,9 mm traslate verso
   l'esterno e fissare ciascun servo con M2.5. Sono raccomandate teste basse sul lato
   interno e dadi sul lato esterno, senza stringere il corpo in plastica.
7. Appoggiare le due guance stampate separate sotto la culla larga 54 mm e
   lasciare inizialmente lente le loro asole di regolazione.
8. Rimontare i cornetti a croce reali sulle spline e le relative viti centrali.
   Usare il cornetto reale come dima per i piccoli prefori nella guancia; non
   usare un pattern stimato dal CAD. Le viti a punta devono mordere solo la
   plastica della guancia senza raggiungere il servo.
9. Portare entrambi i servo allo zero, allineare le guance senza carico assiale
   e solo allora serrare i fissaggi sotto la culla.
10. Montare i carter con gli scarichi laterali rivolti verso alette, teste e
    parti mobili, quindi verificare a mano la corsa da -10° a +35°.

I due assi devono essere realmente coassiali e i comandi sincronizzati,
altrimenti i servo lavorano uno contro l'altro. Il collegamento usa i cornetti
reali e due guance regolabili: non sono previsti perni lisci Ø6 mm né una
spline stampata.

### 5. Cannone e guscio mobile

1. Far passare il connettore 5 x 3 mm nel passaggio mobile 6 x 4 mm.
2. Posare la PCB 50 x 50 x 2 mm sulla culla usando i quattro fori Ø3,5 mm.
3. Abbassare dall'alto il guscio mobile; la cava anteriore a U passa attorno
   alla canna e permette il successivo smontaggio. Gli scassi laterali devono
   passare liberi attorno a cornetti e guance per tutta la corsa.
4. Allineare guscio, PCB e culla.
5. Inserire quattro M3 x 30 dall'alto nei dadi prigionieri inferiori.
6. Verificare che PCB, solenoide e canna si muovano come un unico corpo.
7. Montare il coperchio a L della culatta nella tasca a filo e bloccarlo con due
   M2,5 a testa svasata/bassa. Le teste non devono sporgere dal tetto mobile.

Per la sola prova di ricarica, portare azimut ed elevazione a 0°, disabilitare
l'alimentazione del solenoide e rimuovere le due M2,5. Sollevare il coperchio a
L, inserire dall'alto/posteriore esclusivamente un elemento morbido e inerte
nelle dimensioni realmente collaudate, accompagnarlo con uno spingitore non
metallico e richiudere. Il valore CAD 7 x 10 mm è soltanto un inviluppo
provvisorio. Non eseguire la prova finché il foro posteriore del solenoide non è
stato misurato e confermato continuo e coassiale alla canna Ø8 mm.

### 6. Percorso dei cavi

1. Con adattatore ancora sollevato, infilare uno alla volta nel passaggio
   comune 9 x 7 mm: connettore SG90 sinistro, SG90 destro e infine cannone.
2. I connettori devono terminare sotto il fondo del canale; nella pista devono
   rimanere soltanto i fili, riuniti in un fascio flessibile senza incroci.
3. Bloccare i due cavi servo e il ramo cannone nelle tre coppie di asole 5 x
   2 mm della base fissa. Usare una piccola fascetta senza schiacciare i fili.
4. Bloccare il cavo del cannone nelle due asole della culla e lasciare fra culla
   e telaio un'ansa morbida da 50-60 mm centrata sull'asse di elevazione.
5. Portare la torretta a 0°: il passaggio rotante 9 x 7 mm e l'uscita fissa
   sul fondo del canale risultano entrambi a 45°.
6. Alimentare dal basso almeno 210 mm di fascio libero, lasciandolo inizialmente
   più lungo, e formare una sola ansa ordinata nel canale anulare liscio
   r23,5-r32,5, alto 7 mm. Non tagliare ancora l'eccedenza.
7. Verificare che viti e dadi del telaio, ora a raggio 19 mm, restino dentro la
   corona; rondella, guida e fermagli sono invece fuori. Niente attraversa la
   pista utile.
8. Abbassare la base D100 sulla rondella accompagnando l'ansa e controllando
   che nessun filo rimanga fra disco e tetto.
9. Appena sotto l'uscita, fissare il fascio alle due asole della piastrina
   solidale al tetto: questo è lo scarico di trazione del lato non rotante.
10. Portare infine i fili dall'uscita fissa all'apertura Arduino 25 x 25 mm e,
   se utile, al nuovo foro inferiore 10 x 10 mm.

Con raggio medio 28 mm, un semigiro corrisponde a circa 88 mm di arco. I 210 mm
sono soltanto una lunghezza iniziale minima, non una misura già validata. Non
tagliare definitivamente i cavi prima della prova reale ai quattro estremi di
azimut ed elevazione.

La torretta è limitata via software da -180° a +180°. Non è una rotazione
continua. Dopo perdita di passi o spegnimento va ristabilito lo zero, altrimenti
i cavi possono essere sovratorti. Per rotazione continua serve uno slip ring.

### 7. Chiusura

1. Portare azimut ed elevazione in posizione centrale.
2. Calare il sottoassieme tetto-torretta accompagnando l'ansa.
3. Inserire i quattro boss Ø10 mm all'interno del guscio e allinearli alle
   colonnine.
4. Inserire quattro M3 x 40 dall'alto.
5. Serrare in diagonale senza deformare la stampa.
6. Provare a mano entrambi gli assi.
7. Con base ancora facilmente smontabile, fare una prova lenta:
   `0°, +180°, 0°, -180°, 0°`, poi provare le combinazioni
   `(+180,+35)`, `(+180,-10)`, `(-180,+35)`, `(-180,-10)`. Il canale chiuso
   non permette di vedere l'ansa durante l'uso: controllarla riaprendo la base
   dopo i primi cicli.

## Distinta viti preliminare

| Gruppo | Quantità | Vite proposta | Accesso | Stato |
| --- | ---: | --- | --- | --- |
| Linguette guscio-piano superiore | 4 | M2,5 x 8 | Dall'alto, prima del tetto | Presente nel CAD, da provare |
| Alette reali dei due SG90-telaio | 4 totali | M2,5, testa bassa interna e dado esterno | Dai lati esterni | Diametro confermato sul servo, lunghezza da scegliere sullo stack reale |
| Guance regolabili-culla 54 mm | 4 totali | M2,5 nei prefori ciechi Ø2,2 | Dal basso attraverso le asole delle guance | Lunghezza provvisoria, senza dado sopra la PCB |
| Cornetti reali-guance stampate | Da definire sul cornetto reale | Autofilettanti a punta | Dai lati | Cornetto usato come dima, nessun pattern CAD |
| Cofano posteriore torretta | 4 | M2,5 x 8 | Dai due lati | Provvisoria |
| Tetto-colonnine telaio | 4 | M3 x 40 | Dall'alto | Presente nel CAD, da provare sullo stack reale |
| Fermagli anti-sollevamento-base | 4 | M3 x 8 con dado prigioniero | Dall'alto, fuori dal disco | Presente nel CAD, gioco 0,4 mm |
| Telaio rotante-base D100 attraverso distanziali 6 mm | 4 | M3 x 16 | Dall'alto prima della culla | Pattern r19, lunghezza da provare |
| Guscio mobile-PCB-culla | 4 | M3 x 30 | Dall'alto | Fori PCB confermati, lunghezza provvisoria |
| Coperchio a L culatta-guscio mobile | 2 | M2,5 x 6 testa svasata/bassa | Dall'alto | Quote provvisorie, coperchio ribassato 0,2 mm |
| Stepper-tetto | 2 | M4 x 10…12 testa svasata 90° | Testa Ø8,4 max a filo sopra, dado sotto | Lunghezza da scegliere sullo stack reale |

Per Arduino, driver e PCB del secondo piano non si sceglie ancora una
lunghezza: mancano altezza delle colonnine e stack reale.

## Accessibilità degli utensili

- Le quattro M3 x 40 del tetto sono raggiungibili dall'alto.
- Le quattro M3 dei fermagli e le quattro M3 del telaio rotante sono
  raggiungibili dall'alto dopo avere tolto i gusci della torretta.
- Le quattro M2,5 x 8 del guscio vanno montate prima del tetto.
- Le M2,5 delle alette servo e le viti del cofano sono raggiungibili
  lateralmente; lasciare almeno 25-30 mm liberi attorno alla torretta durante
  la manutenzione.
- I dadi dei fermagli entrano dal basso nel tetto e devono essere preparati a
  banco; i dadi della culla vanno inseriti prima della chiusura. Le guance si
  registrano e si serrano dal basso nei prefori ciechi della culla.
- Per intervenire sui servo conviene togliere dal carro tutto il
  sottoassieme tetto-torretta e lavorare sul banco.

Preferire viti a esagono incassato. Indicativamente: chiave da 2 mm per M2,5,
2,5 mm per M3 e 3 mm per M4; verificare comunque il tipo di testa acquistato.

## Smontaggio

1. Riportare la torretta a 0°, spegnere e scollegare la batteria.
2. Togliere le quattro M3 x 40.
3. Liberare la fascetta dalla piastrina fissa inferiore oppure scollegare il
   tratto che raggiunge Arduino: non sollevare il tetto con il fascio ancora
   bloccato su entrambi i lati.
4. Sollevare lentamente tetto e torretta accompagnando i cavi.
5. Scollegare i connettori senza tirarli attraverso i passaggi.
6. Per separare la parte rotante, togliere prima le quattro M3 del telaio e poi
   i quattro fermagli; sollevare la base D100 accompagnando l'ansa.
7. Per i servo, togliere i carter, liberare i cornetti dalle guance e svitare
   le M2,5 dalle alette reali; estrarre quindi i corpi verso l'esterno.
8. Per il cannone, togliere le quattro M3 x 30 e alzare il guscio dalla cava a U.
9. Per il piano inferiore, togliere le quattro M2,5 x 8, sollevare il piano
   superiore e infine sfilare il guscio continuo.

Non tentare di estrarre il guscio mentre è ancora avvitato alle linguette.

## Verifiche obbligatorie prima della stampa definitiva

- Fori, alette e albero reali del 28BYJ-48.
- Provino della sede D, scorrimento della rondella assiale, gioco della guida
  radiale e dei quattro fermagli anti-sollevamento.
- Accoppiamento dei cornetti SG90 reali alle guance, posizione delle asole,
  sincronizzazione, assenza di precarico assiale, coppia e bilanciamento del
  cannone.
- Dimensioni e fori di driver e PCB; altezza Arduino più shield.
- Passaggio dei cavi motori DC, altezza della batteria principale, accesso al
  connettore e ritenzione della batteria verso l'estremità aperta della
  vaschetta integrata.
- Connettori completi, raggio minimo di curvatura, almeno dieci cicli lenti
  osservati con la base apribile e poi 100 cicli di durata da -180° a +180°.
- Ingombro reale dei cingoli, motori e aste rispetto al guscio 166 x 176 mm.
- Tolleranza FDM di 0,5 mm per lato, allineamento dei boss e deformazione del
  guscio monoblocco.

Il CAD comprende ora apertura a L, coperchio a filo e guida coassiale, ma la
funzione di caricamento non è ancora certificata: servono diametro, lunghezza e
materiale reali di un proiettile morbido/inerte, posizione dei terminali e
conferma che il foro posteriore del solenoide sia libero, continuo e allineato.
