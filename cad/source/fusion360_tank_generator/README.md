# Tank Generator per Autodesk Fusion

Lo script genera il modello partendo da `parameters.json`. Ogni campo `null`
indica una quota che deve ancora essere misurata o confermata.

`meta.build_stage` può valere:

- `lower_deck_blank`: genera solo la piastra inferiore grezza, senza inventare
  i fori ancora non quotati;
- `two_decks_blank`: genera entrambi i piani alla distanza confermata, ancora
  senza fori né colonnine;
- `base_with_standoffs`: genera i due piani, quattro colonnine solidali al piano
  inferiore, i fori passanti e le sedi esagonali in cima alle colonnine per dadi
  M3, senza passacavi né asole per fascette. Le posizioni 10, 25, 75 e 90 mm
  sono misurate dal bordo Sud verso Nord lungo i 170 mm, ma restano inattive
  finché non sono confermate le dimensioni delle asole;
- `base_with_standoffs_and_zip_slots`: aggiunge al piano inferiore quattro asole
  rettangolari 10 x 5 mm, con asse lungo Est-Ovest, centrate lateralmente e
  posizionate a 10, 25, 75 e 90 mm dal bordo Sud verso Nord;
- `base_with_upper_access_openings`: conserva colonnine e asole e aggiunge sul
  piano inferiore il foro di servizio 10 x 10 mm al centro (-0,5; 25) mm,
  20 mm a Nord del centro dell'ultima asola fascetta; aggiunge inoltre sul
  piano superiore l'apertura Arduino 25 x 25 mm al centro (33,33; 45,71) mm e
  il passaggio 60 x 33 mm del pacco batteria PCB al centro (-52,5; -15) mm;
- `full_editable_reference_assembly`: genera nello stesso F3D la base completa
  con le pareti del supporto batteria unite al piano inferiore a Z=3 mm. Il
  piano da 3 mm costituisce il fondo della vaschetta, quindi non viene creato
  un secondo componente da fissare. Aggiunge inoltre il riferimento
  planimetrico Arduino, il guscio laterale continuo Z=0…76 mm e il sottoassieme
  tetto/stepper/torretta appoggiato a Z=46 mm. Il tetto occupa Z=76…79 mm e non
  duplica le pareti laterali. L'Arduino resta uno schizzo XY finché non sono
  confermate le quote verticali di montaggio. Il guscio integra tre feritoie
  42 x 4 mm sul fronte Nord e tre sul retro Sud, centrate nel vano inferiore;
- `base_two_decks`: genera entrambi i piani completi dei due passacavi.
- `battery_holder`: genera l'alternativa autonoma del supporto batteria a U.
  Le quote 100 x 45 mm esterne, 95 x 40 mm interne, fondo 2 mm, pareti
  2,5 mm e altezza 17 mm sono confermate. Il campo `cable_exit.kind` indica
  un'apertura utile di 10 mm nella parete lunga Est, subito dopo la parete corta
  Sud. Questa fase usa il fondo autonomo da 2 mm; lo stage completo usa invece
  il piano inferiore da 3 mm.
- `cover_and_modular_turret`: genera il tetto fisso rispetto allo scafo, lo
  statore dello stepper fissato al tetto, il rotore/albero separato, la base
  rotante D100 con sede D 5,4/3,2 mm, la parte fissa della torretta, due
  TowerPro SG90 coricati, due guance regolabili e la culla mobile larga 54 mm,
  oltre al modulo reale del cannone. Quest'ultimo contiene
  PCB 50 x 50 x 2 mm, quattro fori Ø3,5 mm a 5 mm dai bordi, solenoide Ø20 mm
  e canna tubolare Ø10/Ø8 mm sporgente 46 mm. Lo statore e il tetto restano
  fissi; il solo rotore/albero trascina la D100 e l'assieme superiore nel piano
  XY da -180 a +180 gradi rispetto al centro, quindi 360 gradi
  complessivi ma non continui, con arresto gestito dal software e senza battute
  meccaniche. Ogni servo viene inserito dall'esterno attraverso una finestra
  laterale e fissato con M2.5 mediante le proprie alette reali spesse 2 mm e le
  asole 5 x 2,9 mm traslate verso l'esterno; sono consigliate teste basse
  interne e dadi esterni. I carter hanno scarichi laterali di rispetto. I cornetti a croce
  reali sono riferimenti hardware e dime di foratura per le due guance stampate
  separate, fissate sotto la culla mediante asole regolabili. Il guscio mobile
  ha scassi laterali di rispetto per cornetti e guance. Non vengono
  generati barrette stampate, perni lisci Ø6 mm o una spline approssimata. I due
  servo fanno salire o scendere lungo Z la culla con PCB, solenoide e canna.
  Ogni finestra ha un'uscita 5 x 2 mm per il cavo SG90 da circa
  4 x 1 mm. I connettori SG90 da 7 x 3 mm attraversano uno alla volta il
  passaggio comune 9 x 7 mm nella base fissa e nell'adattatore. Il tetto ha un
  anello completo per i cavi, raggio medio 28 mm e larghezza 9 mm, seguito da
  un canale anulare liscio con fondo continuo, altezza libera 7 mm e uscita
  fissa 9 x 7 mm a 45 gradi. Non ci sono razze o viti nella pista: le quattro
  viti del telaio sono a raggio 19 mm. Il peso è portato da una rondella
  assiale DI76/DE94 esterna al canale; una guida r34,5-r36,5 centra il disco e
  quattro fermagli M3 removibili impediscono il sollevamento lasciando 0,4 mm
  di gioco; coppie di spallamenti stampati ne impediscono la rotazione. La
  rondella entra in una sede ribassata, le M4 stepper hanno svasature 90° reali
  e quattro distanziali da 6 mm mantengono tutto il telaio rotante sopra i
  fermagli fissi con 2,6 mm di margine. Sotto la culla mobile è presente un
  passaggio 6 x 4 mm per il connettore 5 x 3 mm dei due fili del cannone.
  Il guscio mobile integra inoltre una guida posteriore coassiale Ø11/Ø8 x 8 mm
  e un'apertura superiore-posteriore a L, chiusa da un pezzo separato ribassato
  di 0,2 mm con due M2.5 x 6. È una predisposizione modificabile per ricarica manuale di servizio,
  non una culatta a tenuta: il foro posteriore reale del solenoide e il
  proiettile morbido/inerte devono ancora essere misurati e collaudati.

La fase `base_two_decks` genera:

- piano inferiore come componente separato;
- foro per i cavi dei motori DC;
- piano superiore come componente separato;
- foro per i cavi diretti alla torretta;
- parametri utente visibili in Fusion;
- esportazioni `carro_armato_parametrico.f3d` e
  `carro_armato_parametrico.step`.

Il generatore distingue le quote confermate dalle quote
`provisional_editable_first_pass`, inserite soltanto perché l'utente ha
autorizzato una prima proposta modificabile. Se manca una quota obbligatoria,
mostra l'elenco e termina senza creare un modello parziale.

I supporti definitivi per Arduino, driver e PCB verranno aggiunti quando saranno
disponibili le quote ancora mancanti. L'apertura Arduino 25 x 25 mm è centrata
in (33,33; 45,71) mm sopra S1-S8 e D2-D7. Il passaggio del pacco separato della
PCB del cannone è 60 x 33 mm, centrato in (-52,5; -15) mm, con il lato lungo
orientato Sud-Nord. Restano pendenti altezza e diametro delle colonnine Arduino,
oltre a modello e fori di driver e PCB. I passaggi mobili della torretta sono
invece già definiti: ansa presso
l'asse di elevazione, passaggio 6 x 4 mm sotto la culla, passaggio comune
9 x 7 mm e anello completo presso l'asse di azimut. Tre coppie di asole sulla
base fissa e una coppia sulla culla permettono di bloccare i fili con piccole
fascette. I due fili del cannone
possono essere allungati. La corsa resta limitata via software a -180°/+180°;
per una rotazione continua servirebbe uno slip ring.
