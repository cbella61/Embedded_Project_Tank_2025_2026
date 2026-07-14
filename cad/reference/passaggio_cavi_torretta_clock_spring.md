# Passaggio cavi torretta tipo clock-spring

Stato: revisione 4 generata in Fusion 360; la geometria è verificata nel CAD,
mentre lunghezza, attrito e durata del fascio devono essere collaudati sui cavi
reali prima dell'uso continuativo.

## Campo di funzionamento

La torretta parte da uno zero centrale e può raggiungere `+180°` oppure `-180°`.
La corsa totale è quindi 360°, ma non è continua: arrivata a un estremo deve
tornare passando dallo zero. I limiti sono software e non sono battute
meccaniche. Per rotazione continua occorre uno slip ring con almeno otto vie.

## Geometria revisione 4

| Elemento | Valore |
| --- | ---: |
| Pista utile senza ostacoli | r23,5...32,5 mm |
| Raggio medio | 28 mm |
| Larghezza radiale utile | 9 mm |
| Fondo anulare | r19...40 mm, spessore 3 mm |
| Altezza libera sopra il fondo | 7 mm |
| Passaggio mobile | 9 x 7 mm a r28 |
| Uscita fissa | 9 x 7 mm a 45° nello zero |
| Fascio azimut libero iniziale | almeno 210 mm, lasciare eccedenza |
| Ansa elevazione cannone | 50...60 mm |
| Corsa azimut | -180°...+180°, non continua |

Nel volume r23,5...32,5 mm non entrano razze, colonnine, dadi, teste di vite o
fermagli. Le quattro viti M3 che uniscono adattatore e telaio sono a r19 e le
relative sedi dado restano interamente all'interno della pista. La guida
radiale parte da r34,5 e la rondella assiale da r38: entrambi gli elementi sono
quindi esterni al percorso dei fili.

## Punti di ritegno

- Tre coppie di asole 5 x 2 mm sulla parte fissa raccolgono servo sinistro,
  cannone e servo destro prima del passaggio comune.
- Una coppia di asole sulla culla mobile trattiene i due fili del cannone.
- Una coppia di asole su una piastrina sotto l'uscita fissa trattiene il fascio
  che scende verso Arduino e impedisce che venga richiamato nella pista.
- La piastrina è irrigidita da un ponte stampato largo 20 mm verso il fondo
  anulare; le asole sono spostate di 1,5 mm verso l'esterno e conservano almeno
  1,2 mm di legamento nominale.
- Le fascette devono essere piccole e non serrate al punto da schiacciare gli
  isolamenti.
- Nessuna fascetta o testa sporgente deve entrare nella pista anulare.

## Sequenza corretta di montaggio

1. Lasciare smontati i due SG90, il PCB cannone, la base rotante e il telaio.
2. Infilare il connettore 5 x 3 mm del cannone dal foro 6 x 4 mm della culla,
   quindi lasciare 50...60 mm di ansa morbida vicino all'asse di elevazione.
3. Infilare ciascun connettore SG90 7 x 3 mm attraverso la grande finestra del
   relativo supporto prima di inserire il servo dall'esterno.
4. Bloccare separatamente i tre rami nelle coppie di asole della parte fissa.
5. Con adattatore e tetto ancora separati, passare uno alla volta nel foro
   mobile 9 x 7 mm: SG90 sinistro, SG90 destro, connettore cannone.
6. Ripetere nello stesso ordine attraverso l'uscita fissa 9 x 7 mm. Nella pista
   devono restare solo i fili; i connettori devono terminare sotto il tetto.
7. Formare sul fondo anulare un'unica ansa ordinata, senza nodi o incroci,
   partendo da almeno 210 mm di fascio libero e lasciando inizialmente una
   buona eccedenza, da regolare solo dopo il collaudo.
8. Montare la base D100, la rondella assiale, la guida e i quattro fermagli
   anti-sollevamento controllando che nessun filo venga pizzicato.
9. Bloccare il tratto fisso alle due asole della piastrina inferiore, poi
   collegarlo all'apertura Arduino 25 x 25 mm e al nuovo foro di
   servizio 10 x 10 mm del piano inferiore secondo il cablaggio definitivo.
10. Solo dopo il collaudo montare i gusci dei servo e del cannone.

## Collaudo obbligatorio

1. Muovere a mano l'elevazione completa verificando l'ansa da 50...60 mm.
2. A bassa velocità eseguire `0°, +180°, 0°, -180°, 0°`.
3. Ripetere almeno dieci cicli con la base ancora apribile, poi controllare il
   fascio riaprendo il disco; il canale chiuso non consente ispezione visiva.
4. Provare anche `(+180,+35)`, `(+180,-10)`, `(-180,+35)` e `(-180,-10)`.
5. Verificare che non aumenti la trazione sui connettori e che la base non
   schiacci i fili contro fondo, guida o fermagli.
6. Memorizzare lo zero software dopo ogni accensione o introdurre una procedura
   di homing: il solo conteggio passi non recupera una perdita di posizione.

Se il fascio si sovrappone, esce dalla pista o tende i connettori, non usare la
torretta a velocità normale. Ridisporre l'ansa o passare a una cassetta
spiralata/FFC; per una rotazione senza ritorno allo zero è obbligatorio uno slip
ring.
