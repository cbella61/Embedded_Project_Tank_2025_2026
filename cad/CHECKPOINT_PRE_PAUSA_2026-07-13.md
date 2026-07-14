# Checkpoint CAD pre-pausa — 13 luglio 2026

Questo file è il punto di ripartenza per il modello 3D del carro armato.

## Aggiornamento del 14 luglio 2026 — supporto batteria integrato

- Nello stage completo le pareti 2,5 x 17 mm della vaschetta batteria sono ora
  unite direttamente al piano inferiore.
- Il piano inferiore da 3 mm costituisce il fondo: non esistono più un secondo
  fondo, viti o colla dedicati al supporto.
- Ingombro e posizione restano 45 x 100 mm, centro X=-52,5 mm e Y=-15 mm.
- La parete lunga Est ha un'apertura utile da 10 mm subito dopo la parete corta
  Sud, così l'intero passaggio resta accessibile dall'interno.
- Lo stage `battery_holder` conserva la variante autonoma con fondo da 2 mm.
- Il nuovo export completo è
  `carro_armato_assieme_completo_modificabile_v3_batteria_integrata_canale_cavi.*`;
  è stato generato con successo in Fusion il 14 luglio 2026.

## Stato raggiunto

- Il generatore parametrico Fusion 360 è in
  `cad/source/fusion360_tank_generator/`.
- `parameters.json` è stato lasciato su
  `full_editable_reference_assembly`.
- Il guscio esterno del carro è ora un solo corpo laterale continuo da
  Z=0 mm a Z=76 mm, senza giunzione visibile all'altezza del secondo piano.
- Il tetto è un componente separato da Z=76 mm a Z=79 mm.
- Il vecchio secondo gruppo di quattro pareti e le vecchie flange quadrate M3
  sono stati eliminati: non ci sono volumi duplicati.
- Il tetto scende con quattro boss cilindrici Ø10 mm, forati Ø3,2 mm, fino al
  piano superiore. Le viti M3 sono accessibili dall'alto.
- Il controllo visivo in Fusion mostra una sola parete esterna continua e una
  sola linea di separazione, quella necessaria tra guscio e tetto removibile.

## Architettura meccanica corrente

- Piano inferiore: 160 x 170 x 3 mm, Z=0…3 mm.
- Luce libera: 40 mm.
- Piano superiore: 160 x 170 x 3 mm, Z=43…46 mm.
- Guscio laterale: esterno 166 x 176 mm, parete 2,5 mm, Z=0…76 mm.
- Tetto: 166 x 176 x 3 mm, Z=76…79 mm.
- Quattro linguette interne del guscio per M2,5 sotto il piano superiore.
- Quattro boss del tetto per viti M3 dall'alto verso i dadi prigionieri delle
  colonnine principali.
- Stepper: rotazione orizzontale XY dell'intera torretta.
- Due SG90: assi orizzontali e coassiali; sollevano e abbassano insieme culla,
  PCB, solenoide e canna.
- Il cannone è diritto e il gruppo mobile comprende la PCB 50 x 50 x 2 mm,
  quattro fori Ø3,5 mm su interasse 40 x 40 mm, solenoide Ø20 mm e canna
  tubolare Ø10/Ø8 mm con sporgenza di 46 mm.

## Rotazione e cavi

- Azimut limitato via software da -180° a +180° rispetto al centro: 360°
  complessivi, ma non rotazione continua.
- Una rotazione continua richiederebbe uno slip ring.
- I due connettori SG90 sono 7 x 3 mm; i cavi sono circa 4 x 1 mm.
- Il connettore del cannone è 5 x 3 mm.
- I connettori vengono infilati uno alla volta nel passaggio comune 8 x 6 mm
  prima del fissaggio finale della torretta.
- Il cannone usa anche un passaggio mobile 6 x 4 mm.
- Nel tetto è presente un anello completo per l'ansa di servizio. Sotto
  l'anello è ora definito nelle sorgenti un canale tipo clock-spring con fondo
  continuo r19-r40, pista libera r24-r32, altezza utile 7 mm e uscita fissa
  8 x 6 mm a 45°. Le quattro razze radiali esposte sono state eliminate.
- Dall'uscita fissa i cavi raggiungono l'apertura Arduino 25 x 25 mm del piano
  superiore.
- La lunghezza e il raggio di curvatura reali dell'ansa devono essere provati
  sui cavi fisici prima di usare tutta la corsa -180°/+180°.

## File esportati e verificati prima della correzione cavi

I file seguenti sono conservati come riferimento precedente, ma contengono
ancora le quattro razze e non sono la versione da approvare per la stampa.

Assieme completo:

- `cad/exchange/carro_armato_assieme_completo_modificabile.f3d`
- `cad/exchange/carro_armato_assieme_completo_modificabile.step`
- esportati il 13/07/2026 alle 18:56;
- STEP: 24 solidi chiusi, 21 occorrenze e 22 prodotti;
- F3D: 64 elementi interni, 52 non vuoti e 37 parti B-Rep;
- SHA-256 F3D:
  `7B37EFB651B53CE213BC6AEACF8C05809A17F2D4CE696A1EA747311801F77CDB`;
- SHA-256 STEP:
  `E80FC152042EF0CEB58620060DD67D95D0C1F1248EFFB98BC3D18BE32FEAE8F9`.

Sottoassieme tetto/torretta:

- `cad/exchange/coperchio_supporto_stepper_torretta_modulare.f3d`
- `cad/exchange/coperchio_supporto_stepper_torretta_modulare.step`
- esportati il 13/07/2026 alle 19:00;
- STEP: 20 solidi chiusi, 14 occorrenze e 15 prodotti;
- SHA-256 F3D:
  `F0CB08A28E4AD4AD47DA2C12FFF4978C34A14DFB04DA372B35F1D2087CB51913`;
- SHA-256 STEP:
  `08C1FE1549CB9307355BB39CFB2C7D4437B287ED52A823EF5D0B35ADD15EF8CC`.

Entrambi gli STEP precedenti contengono il
`Tetto_removibile_con_supporto_stepper_e_boss_M3` e non contengono più le
vecchie `Parete_Ovest` o `Flangia_M3` del coperchio sdoppiato.

La revisione 3 del generatore esporta senza sovrascrivere i precedenti:

- `cad/exchange/carro_armato_assieme_completo_modificabile_v3_batteria_integrata_canale_cavi.f3d`;
- `cad/exchange/carro_armato_assieme_completo_modificabile_v3_batteria_integrata_canale_cavi.step`;
- `cad/exchange/coperchio_supporto_stepper_torretta_modulare_v2_canale_cavi.f3d`;
- `cad/exchange/coperchio_supporto_stepper_torretta_modulare_v2_canale_cavi.step`.

I due export completi revisione 3 sono stati generati e verificati il 14 luglio
2026 alle 00:48. Lo STEP contiene 23 solidi chiusi, 19 occorrenze e 20 prodotti;
l'F3D contiene 62 elementi, 50 non vuoti e 35 elementi B-Rep. Lo STEP contiene
`01_Piano_inferiore_colonnine_M3_supporto_batteria_integrato` e non contiene un
sottoassieme portabatteria separato.

- SHA-256 F3D:
  `F172929D42E8358DB981C4CF62F95784D860FB48DD3C63FF18B9CDD75B7DBA95`;
- SHA-256 STEP:
  `E21FA81F2B7CEE4B6C86BD55ACBCCEC4454C715D3854879C8E411AB96E2464F0`.

I due export separati torretta revisione 2 devono ancora essere rigenerati; la
stessa geometria corretta è già contenuta e verificata nell'assieme completo
revisione 3.

## Montaggio previsto

1. Fissare con fascette il piano inferiore alle due aste del telaio.
2. Inserire la batteria nella vaschetta integrata, poi montare Arduino e
   cablaggio motori sul piano inferiore.
3. Inserire i dadi M3 nelle quattro colonnine e montare il piano superiore.
4. Calare il guscio laterale unico dall'alto e bloccarlo con quattro M2,5x8
   dalle aperture superiori, prima di montare il tetto.
5. Preparare a banco tetto, stepper e torretta.
6. Infilare nell'ordine i due connettori SG90 e quello del cannone nel passaggio
   comune, lasciando l'ansa di servizio.
7. Calare il tetto con i quattro boss all'interno del guscio.
8. Serrare dall'alto quattro M3x40 nei dadi delle colonnine.
9. Controllare manualmente elevazione e azimut a bassa velocità prima di
   attivare i limiti software completi.

## Quote o prove ancora necessarie

- Interasse e diametro reali dei fori del 28BYJ-48: nel modello sono ancora
  provvisori (35 mm e Ø4,2 mm).
- Ingombro e fori del driver motori e della PCB fissa della torretta.
- Altezza e fissaggio definitivo dell'Arduino con shield.
- Diametro e posizione dei passaggi futuri dei cavi motori.
- Prova fisica delle tolleranze FDM per SG90, dadi, connettori e ansa cavi.
- Verifica dell'ingombro esterno del guscio rispetto ai cingoli reali.
- Dimensioni del proiettile morbido/inerte e conferma del foro posteriore del
  solenoide prima di progettare un caricamento manuale sicuro.

## Prossima attività alla ripresa

Il problema dell'anello inferiore e l'integrazione del supporto batteria sono
ora presenti nell'assieme completo revisione 3, già aperto e verificato in
Fusion. La prossima operazione è misurare altezza e connettore della batteria
principale, controllare l'interferenza verticale con il pacco batteria PCB e,
se serve come file autonomo, rigenerare lo stage
`cover_and_modular_turret`. Prima della stampa definitiva restano necessarie le
prove fisiche elencate sopra.

Usare `cad/ASSEMBLAGGIO_FATTIBILITA.md` come procedura di montaggio preliminare.
Alla ripresa bisogna misurare i componenti critici, provare le tolleranze e
correggere le quote provvisorie. Non rigenerare da vecchi file cloud:
continuare dal generatore e dagli export indicati sopra.
