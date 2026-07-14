# Quote da confermare

Unità di progetto: millimetri.

| Gruppo | Quota | Valore confermato |
| --- | --- | --- |
| Telaio | Lunghezza totale del piano inferiore | 170 mm (comunicata come "height") |
| Telaio | Larghezza totale del piano inferiore | 160 mm |
| Telaio | Spessore del piano inferiore | 3 mm |
| Telaio | Luce verticale tra superficie superiore del piano inferiore e fondo del piano superiore | 40 mm |
| Fissaggio | Numero colonnine | 4 |
| Fissaggio | Diametro esterno colonnine | 10 mm (scelta autorizzata) |
| Fissaggio | Distanza centro colonnine dai bordi | 12 mm (scelta autorizzata) |
| Fissaggio | Viteria | M3 |
| Viteria disponibile | Misure utilizzabili | M2, M2.5, M3, M4 e M5; scegliere in base al componente |
| Fissaggio | Diametro fori passanti | 3,2 mm |
| Fissaggio | Sede dado M3 | 5,8 mm tra facce, profondità 2,6 mm |
| Fissaggio | Posizione sede dado M3 | In cima a ogni colonnina |
| Fissaggio al telaio | Metodo | Fascette attorno a due aste trasversali |
| Fissaggio al telaio | Dimensioni asole | 10 x 5 mm, asse lungo Est-Ovest |
| Fissaggio al telaio | Posizioni asole dal bordo Sud | 10, 25, 75 e 90 mm, allineamento laterale centrale |
| Piano superiore | Lunghezza | 170 mm |
| Piano superiore | Larghezza | 160 mm |
| Piano superiore | Spessore | 3 mm |
| Passacavi | Diametro e posizione del foro inferiore | da confermare |
| Passacavi | Diametro e posizione del foro superiore | da confermare |
| Elettronica | Modello e ingombro della batteria | da confermare |
| Elettronica | Arduino | UNO R4 WiFi ABX00087 con shield Emakefun sovrapposta; profilo ufficiale 68,58 x 53,34 mm, quattro fori Ø3,2 mm; STEP ufficiale disponibile |
| Elettronica | Apertura Arduino | una apertura quadrata 25 x 25 mm nel piano superiore, sopra S1-S8 e D2-D7; centro X=33,33 mm, Y=45,71 mm |
| Elettronica | Passaggio pacco batteria PCB cannone | 60 x 33 mm nel piano superiore, centro X=-52,5 mm, Y=-15 mm; case fotografato 59 x 32 mm, gioco 0,5 mm per lato, lato lungo verso Nord |
| Elettronica | Posizione supporto batteria | angolo Sud-Ovest; lato da 100 mm verso Nord, 5 mm da Ovest e 20 mm da Sud; centro X=-52,5 mm, Y=-15 mm |
| Elettronica | Supporto batteria nello stage completo | pareti 2,5 mm alte 17 mm unite al piano inferiore; il piano da 3 mm è il fondo; nessuna vite o colla dedicata |
| Elettronica | Supporto batteria autonomo | stage alternativo con fondo proprio da 2 mm; ingombro 100 x 45 x 19 mm |
| Elettronica | Apertura cavi supporto batteria | tratto utile di 10 mm sulla parete lunga Est, subito dopo la parete corta Sud |
| Elettronica | Posizione Arduino + shield | angolo Nord-Est, rotazione 90 gradi antioraria, jack DC verso Sud; 20 mm da Est e 5 mm da Nord; centro X=33,33 mm, Y=45,71 mm |
| Elettronica | Modello e ingombro del driver motori | da confermare |
| Elettronica | Dimensioni e schema dei fori della PCB torretta | da confermare |
| Torretta | Riferimento stepper | 28BYJ-48, quote CAD provvisorie e modificabili |
| Torretta | Base rotante | diametro 70 mm, spessore 6 mm, provvisoria |
| Elevazione | Servomotori | 2 TowerPro SG90 coricati, corpo 22,7 x 12,2 x 27 mm; inserimento laterale removibile |
| Elevazione | Fissaggio SG90 | due slitte esterne e due barrette M2.5 per lato; zona centrale libera per il cavo |
| Elevazione | Cinematica | due perni orizzontali coassiali, diametro 6 mm; movimento del cannone lungo Z |
| Elevazione | Corsa proposta | -10° / +35°, da verificare sul prototipo |
| Azimut | Corsa torretta | da -180° a +180° rispetto allo zero; 360° complessivi ma non continui |
| Azimut | Arresto | gestito dal software contando i passi dello stepper; nessuna battuta meccanica nel CAD |
| Cablaggio SG90 | Cavo, connettore e passaggi | 2 cavi, ciascuno a 3 fili, profilo circa 4 x 1 mm; uscita slitta 5 x 2 mm; connettore 7 x 3 mm; passaggio comune 8 x 6 mm, connettori infilati uno alla volta |
| Cablaggio cannone | Fili, connettore e passaggio mobile | 2 fili allungabili; connettore 5 x 3 mm; passaggio sotto culla 6 x 4 mm |
| Cablaggio torretta | Guida azimut | canale anulare completo tipo clock-spring, raggio medio 28 mm, larghezza libera 8 mm, fondo continuo Z locale 20-23 mm, altezza libera 7 mm e uscita fissa 8 x 6 mm a 45°; nessuna razza nella pista |
| Cannone | Forma | unico corpo rettilineo solidale alla culla mobile |
| Cannone | Lunghezza e sezione esterna | 175 x 40 x 14 mm, asse a 70 mm dal retro; provvisorio |
| Modulo di sparo | Parti mobili | piastra con elettromagnete, meccanismo e canna ruotano tutti con la culla |
| Modulo di sparo | Metodo di fissaggio | usare i quattro fori esistenti della PCB mobile |
| Modulo di sparo | PCB | 50 x 50 x 2 mm, non metallica |
| Modulo di sparo | Zona con solenoide | cannone completo Ø20 mm in questa zona |
| Modulo di sparo | Canna | tubolare, Ø10 mm esterno, parete 1 mm, Ø8 mm interno, sporgenza 46 mm dall'uscita |
| Modulo di sparo | Altezza complessiva | 23 mm dalla faccia inferiore della PCB alla sommità |
| Modulo di sparo | Fori PCB | Ø3,5 mm; centri a 5 mm dai due bordi adiacenti; interassi 40 x 40 mm |

## Regola di modellazione

Ogni valore inserito nel CAD deve essere riconducibile a una misura comunicata
e confermata oppure a una prima proposta espressamente autorizzata e marcata
come provvisoria. Eventuali giochi di stampa sono parametri separati e dichiarati.
