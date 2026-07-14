# Arduino UNO R4 WiFi - riferimento meccanico ufficiale

Questa cartella contiene il modello STEP ufficiale della scheda indicata dal
firmware del progetto.

## Provenienza

- Prodotto: Arduino UNO R4 WiFi, SKU `ABX00087`.
- Pagina ufficiale: <https://docs.arduino.cc/hardware/uno-r4-wifi>
- Archivio STEP ufficiale:
  <https://docs.arduino.cc/resources/models/ABX00087-step.zip>
- Data di acquisizione: 13 luglio 2026.

## File

- `ABX00087-step.zip`: archivio originale non modificato.
- `UNO_R4_WIFI.step`: modello estratto dall'archivio ufficiale.

## Verifica integrità locale

- SHA-256 `ABX00087-step.zip`:
  `FB2222C1E27613ACC34D50ABD4F42FEE5ED545D13B8294C984050AE625373285`
- SHA-256 `UNO_R4_WIFI.step`:
  `C1A5440B8D4C2D80CBFB134C82E82B0B2FA5DC4193D0E858E1493122096E1448`

Il disegno meccanico a pagina 20 del datasheet ufficiale, revisione 3 luglio
2026, quota un ingombro di 68,58 x 53,34 mm e quattro fori R1,6 mm, quindi
diametro 3,2 mm. Assumendo l'origine nell'angolo Sud-Ovest della scheda, asse X
verso Est e asse Y verso Nord, i centri dei fori sono:

- Sud-Ovest: X 13,97 mm, Y 2,54 mm;
- Nord-Ovest: X 15,24 mm, Y 50,80 mm;
- Sud-Est: X 66,04 mm, Y 7,62 mm;
- Nord-Est: X 66,04 mm, Y 35,56 mm.

Il file STEP resta il riferimento vendor. La scheda non è ancora stata
posizionata sul piano inferiore e il disegno non autorizza a scegliere
arbitrariamente altezza e diametro delle colonnine oppure le distanze dai bordi
del carro.
