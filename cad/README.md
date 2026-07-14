# Modello CAD del carro armato

Stato meccanico di riferimento: revisione 5 del 14 luglio 2026. Gli export
revisione 4 restano un checkpoint precedente; vedere
`CHECKPOINT_REV4_2026-07-14.md` e `ASSEMBLAGGIO_FATTIBILITA.md`.

Questa cartella contiene il modello meccanico modificabile del carro armato.

## Struttura prevista

- `source/`: sorgenti parametrici e file nativo di Autodesk Fusion.
- `exchange/`: esportazioni STEP compatibili con Fusion 360 e altri CAD.
- `stl/`: parti pronte per la stampa 3D, generate solo dopo la conferma delle quote.
- `reference/`: tabella delle quote confermate e note di assemblaggio.

Il modello sarà suddiviso in componenti:

1. piano inferiore con batteria, Arduino e passaggio cavi dei motori DC;
2. piano superiore con driver, PCB della torretta e passaggio cavi verticale;
3. base rotante della torretta sostenuta dallo stepper;
4. supporto superiore inclinabile azionato da due servomotori;
5. cannone rettilineo solidale alla parte inclinabile, senza le fascette/barre
   laterali indicate nel riferimento.

Le quote non leggibili dagli schizzi non vengono stimate, salvo quando l'utente
autorizza esplicitamente una prima proposta modificabile. In quel caso sono
marcate come provvisorie nei parametri.

Sono disponibili viti M2, M2.5, M3, M4 e M5. La struttura principale resta
M3; i due servo vengono fissati dalle loro alette reali con viti M2.5.

## Assieme completo modificabile

L'export principale corrente, generato dalla revisione 4, è:

- `exchange/carro_armato_assieme_completo_modificabile_v4_torretta_funzionante_griglie_foro_10x10.f3d`;
- `exchange/carro_armato_assieme_completo_modificabile_v4_torretta_funzionante_griglie_foro_10x10.step`.

Nell'assieme le pareti del supporto batteria Sud-Ovest sono unite direttamente
al piano inferiore: la piastra da 3 mm è anche il fondo della vaschetta, quindi
non esistono un secondo fondo o viti dedicate. L'F3D riunisce questa base, il
riferimento Arduino Nord-Est, il guscio laterale continuo e il sottoassieme
tetto/stepper/torretta. Il guscio è un solo corpo da Z=0 a Z=76 mm; il tetto
removibile occupa Z=76…79 mm e scende con quattro boss M3 interni. Il
riferimento Arduino resta uno schizzo 2D finché non sono note le quote dello
stack Arduino + shield. La revisione 4 aggiunge un foro di servizio 10 x 10 mm
sul piano inferiore, tre feritoie 42 x 4 mm sul fronte e tre sul retro, oltre al
nuovo sostegno fisico della torretta. Nello STEP il piano
inferiore compare come
`01_Piano_inferiore_colonnine_M3_supporto_batteria_integrato`, senza un
componente portabatteria separato. I vecchi file revisione 3 restano soltanto
come checkpoint precedente.

## Grezzo disponibile

`stl/piano_inferiore_grezzo_senza_fori.stl` rappresenta esclusivamente la
piastra inferiore 170 x 160 x 3 mm. È marcata come grezzo perché i passacavi non
sono ancora quotati e non devono essere posizionati arbitrariamente. Il file
`source/piano_inferiore_grezzo.scad` contiene la stessa geometria parametrica.

`exchange/base_due_piani_grezza_senza_fori.obj` contiene entrambi i piani come
oggetti separati, con il piano superiore da Z=43 mm a Z=46 mm. La luce libera
tra le due piastre è quindi esattamente 40 mm. Il corrispondente sorgente è
`source/base_due_piani_grezza.scad`.

## Base con fissaggi M3

I file aggiornati della sola base sono:

- `exchange/base_colonnine_M3_asole_aperture_superiori_Arduino_pacco_batteria.f3d`;
- `exchange/base_colonnine_M3_asole_aperture_superiori_Arduino_pacco_batteria.step`.

Contengono due piastre 170 x 160 x 3 mm e quattro colonnine diametro 10 mm alte
40 mm, unite al piano inferiore. Ogni colonnina ha un foro passante diametro
3,2 mm e una sede esagonale per dado M3 aperta nella sua estremità superiore.
Il piano superiore contiene i quattro fori tondi per le viti, una singola
apertura Arduino 25 x 25 mm centrata in X=33,33 mm, Y=45,71 mm e l'apertura
60 x 33 mm per il pacco batteria separato della PCB del cannone, centrata in
X=-52,5 mm, Y=-15 mm e orientata con il lato da 60 mm verso Nord. Il piano
inferiore contiene le quattro asole 10 x 5 mm per le fascette alle posizioni
confermate. Il STEP è stato verificato con due solidi chiusi e ingombro
complessivo 160 x 170 x 46 mm; l'F3D è un archivio Fusion valido.

Il precedente file `base_colonnine_M3_asole_fascette_senza_passacavi.*` resta
una revisione intermedia valida con le asole, ma priva delle due aperture
superiori. `base_colonnine_integrate_dadi_M3_senza_passacavi.*` è ancora più
vecchio e non contiene neppure le asole per fascette.

I precedenti file `base_due_piani_con_colonnine_M3_senza_passacavi.*` sono una
revisione superata, con le sedi dei dadi nella posizione non richiesta, e non
devono essere usati come base per le prossime modifiche.

## Fissaggio al telaio con fascette

Le quattro asole sono confermate come rettangoli 10 x 5 mm, con asse lungo
Est-Ovest e allineamento laterale centrale. Le posizioni longitudinali 10, 25,
75 e 90 mm partono dal bordo Sud e crescono verso Nord lungo il lato da 170 mm.
La fase `base_with_upper_access_openings` del generatore conserva queste quote
e aggiunge soltanto le due aperture elettroniche superiori, senza inventare i
passacavi ancora sconosciuti.

## Supporto batteria

Nella fase `full_editable_reference_assembly` il supporto è stampato insieme al
piano inferiore. Conserva esterno 100 x 45 mm, vano 95 x 40 mm, pareti da
2,5 mm alte 17 mm e posizione Sud-Ovest; il piano inferiore da 3 mm ne forma il
fondo. Un tratto utile di 10 mm della parete lunga Est, subito dopo la parete
corta Sud, viene rimosso per il passaggio dei cavi. Non servono viti, colla o
incastri per fissare il supporto alla base.

La fase `battery_holder` rimane disponibile come alternativa autonoma
modificabile con fondo proprio da 2 mm e le stesse pareti.

Il nuovo export autonomo atteso, non ancora rigenerato, è:

- `exchange/supporto_batteria_standalone_parametrico_v2_apertura_utile_10mm.f3d`;
- `exchange/supporto_batteria_standalone_parametrico_v2_apertura_utile_10mm.step`.

L'ingombro nominale è 100 x 45 x 19 mm: 2 mm di fondo più 17 mm di parete.
I vecchi `supporto_batteria_parametrico.*` restano soltanto come riferimento
della versione precedente.

## Coperchio, stepper e torretta modulare

La fase `cover_and_modular_turret` genera un assieme modificabile composto da:

1. tetto removibile dell'elettronica, ma fisso durante il funzionamento, con
   quattro boss M3 accessibili dall'alto;
2. statore del 28BYJ-48 fissato sotto il tetto e rotore/albero modellato come
   componente separato;
3. base rotante D100 con sede a D, trascinata soltanto dal rotore/albero;
4. rondella assiale removibile, guida radiale e quattro fermagli
   anti-sollevamento;
5. struttura fissa della torretta sollevata di 6 mm e solidale alla base;
6. due servomotori esterni, uno per lato, fissati mediante le alette reali da
   2 mm e viti M2.5;
7. culla mobile larga 54 mm, con due guance stampate regolabili inferiori e
   due cornetti a croce SG90 reali;
8. modulo reale composto da PCB 50 x 50 x 2 mm, zona solenoide e canna
   tubolare, solidale alla culla mobile.

Il tetto e lo statore dello stepper restano fissi rispetto allo scafo. Il solo
rotore/albero trascina la base D100 e tutto ciò che si trova sopra di essa nel
piano XY. I due servo, che ruotano insieme alla parte fissa della torretta,
inclinano la culla e spostano il cannone in alto e in basso lungo Z. La culla e
la PCB condividono quattro
fori Ø3,5 mm con interasse 40 x 40 mm; nella culla sono presenti sedi inferiori
per dadi M3. La canna è Ø10/Ø8 mm, sporge 46 mm dalla zona solenoide Ø20 mm e
l'intero modulo raggiunge 23 mm dalla faccia inferiore della PCB.

File della revisione precedente, conservati per confronto:

- `exchange/coperchio_supporto_stepper_torretta_modulare.f3d`;
- `exchange/coperchio_supporto_stepper_torretta_modulare.step`.

L'F3D precedente contiene 55 elementi interni, 43 non vuoti; lo STEP contiene
20 solidi chiusi, 14 occorrenze e 15 prodotti. Nella revisione 5 i due giunti
rotoidali sono definiti fra statore e rotore per l'azimut e fra telaio fisso e
culla per l'elevazione. Le quote strutturali restano parametriche in Fusion.

La geometria meccanica della revisione 5 conserva la rondella, che entra in una
sede anulare ribassata di 0,3 mm; la guida conserva almeno 1 mm di
impegno anche con la base sollevata e i fermagli sono bloccati in rotazione da
spallamenti stampati. Le due viti M4 dello stepper hanno svasature 90° reali e
restano a filo sotto la base. I componenti
sono separati nell'F3D per poterli modificare o esportare singolarmente; la
base, la rondella e ciascuno dei quattro fermagli sono parti distinte.

I TowerPro SG90 entrano dall'esterno attraverso le finestre laterali. Ogni
corpo servo appoggia con le proprie alette reali spesse 2 mm sulle asole da
5 x 2,9 mm traslate verso l'esterno; sono consigliate viti M2.5 con testa bassa
sul lato interno e dado sul lato esterno. I carter laterali hanno scarichi di rispetto
per alette, teste e corsa della culla. Non sono più presenti barrette stampate
né perni lisci Ø6 mm sovrapposti agli alberi servo.

I cornetti a croce sono componenti hardware reali, non parti da stampare e non
una spline ricostruita nel CAD. Si usano come dima per segnare o realizzare i
piccoli prefori sulle due guance stampate separate. Le guance si fissano sotto
la culla larga 54 mm mediante asole di regolazione, così si possono allineare i
due assi senza precaricare i servo. Il foro centrale delle guance lascia
accessibile la vite originale del cornetto.
Il guscio mobile della torretta comprende inoltre scassi laterali di rispetto,
così non interferisce con cornetti e guance durante l'elevazione.

La rotazione di azimut è limitata via software da -180° a +180° rispetto al
centro: 360° complessivi, ma non rotazione continua. Il CAD non contiene
battute meccaniche; per una rotazione continua servirebbe uno slip ring.
Ogni SG90 dispone di un'uscita
5 x 2 mm per il cavo a tre fili da circa 4 x 1 mm. I connettori SG90 misurano
7 x 3 mm e attraversano uno alla volta il passaggio comune 9 x 7 mm nella base
fissa e nell'adattatore. Sul tetto è presente un anello completo, raggio medio
28 mm e larghezza utile 9 mm, da r23,5 a r32,5. Sotto l'anello è integrato un canale liscio tipo
clock-spring: fondo continuo da Z locale 20 a 23 mm, altezza libera 7 mm,
pareti circolari senza sporgenze e uscita fissa 9 x 7 mm a 45 gradi. Le quattro
razze radiali della versione precedente sono state eliminate perché potevano
impigliare l'ansa durante la corsa -180°/+180°.

Il cannone usa due fili allungabili e un connettore 5 x 3 mm; sotto la culla è
tagliato un passaggio 6 x 4 mm, con 0,5 mm di gioco per lato. Il cablaggio usa
un'ansa libera da 50...60 mm presso l'asse di elevazione e almeno 210 mm di
fascio libero ordinato per l'azimut, entra nel canale anulare del
tetto, esce dal foro fisso sul fondo e raggiunge l'apertura Arduino 25 x 25 mm.
Tre coppie di asole sulla parte rotante, una coppia sulla culla e una coppia su
una piastrina fissa sotto l'uscita realizzano lo scarico di trazione. L'ansa di
elevazione prevista è 50...60 mm; i 210 mm dell'azimut sono soltanto una
lunghezza iniziale minima e i fili vanno lasciati più lunghi fino al collaudo.
La piastrina fissa è collegata al fondo anulare da un ponte stampato largo 20 mm;
le asole sono traslate di 1,5 mm verso l'esterno per conservare almeno 1,2 mm di
materiale utile con un ugello da 0,4 mm.
Lunghezza libera e raggio minimo di piega devono essere
provati sui cavi reali.

La revisione 4 comprende anche una predisposizione di ricarica manuale: una
finestra posteriore e un'asola sul tetto del guscio mobile formano un accesso a
L, richiuso da un coperchio separato ribassato di 0,2 mm con due M2,5 x 6. Una guida interna
coassiale Ø11/Ø8 x 8 mm accompagna verso il retro del solenoide. L'inviluppo CAD
provvisorio è limitato a un elemento morbido/inerte di massimo 7 x 10 mm; non è
una misura confermata. Il caricamento è consentito soltanto a torretta centrata,
elevazione 0° e alimentazione disattivata. Prima dell'uso vanno misurati il foro
posteriore reale del solenoide, i terminali e il proiettile; il foro Ø10 del
riferimento CAD non dimostra che l'hardware sia attraversabile.
La geometria, la sequenza di montaggio e le prove richieste sono riepilogate in
`reference/passaggio_cavi_torretta_clock_spring.md`; la predisposizione di
ricarica è descritta in `reference/culatta_ricarica_manuale.md`.

La verifica degli ingombri rispetto alle stampanti del FabLab UniTrento è in
`STAMPABILITA_FABLAB_UNITRENTO.md`. Per guscio e tetto da 166 x 176 mm sono
raccomandate Bambu A1, H2D o Prusa XL; la A1 Mini da 180 mm è nominalmente
sufficiente ma lascia un margine troppo ridotto per una stampa affidabile.

## Riferimenti meccanici ufficiali

Il modello STEP ufficiale dell'Arduino UNO R4 WiFi è conservato in
`reference/vendor/arduino_uno_r4_wifi/`. Viene usato soltanto come riferimento
dimensionale. L'Arduino è orientato con una rotazione di 90 gradi antioraria,
jack verso Sud, a 20 mm dal bordo Est e 5 mm dal bordo Nord; il centro è
X=33,33 mm, Y=45,71 mm. Allo stesso centro è tagliata la singola apertura
25 x 25 mm sopra i gruppi pin S1-S8 e D2-D7. Il supporto batteria segue la
direzione Sud-Nord da 170 mm, a 5 mm da Ovest e 20 mm da Sud, con centro
X=-52,5 mm, Y=-15 mm. Allo stesso centro è tagliato il passaggio 60 x 33 mm
per il case 59 x 32 mm della PCB del cannone, con 0,5 mm di gioco per lato.
Restano da confermare altezza e diametro delle colonnine Arduino, ingombro
verticale della batteria principale e del relativo connettore, e altezza finale
del pacco batterie PCB che scende dalla relativa apertura.

Le quote del TowerPro SG90 e il collegamento alla pagina del produttore sono in
`reference/vendor/towerpro_sg90/README.md`.
