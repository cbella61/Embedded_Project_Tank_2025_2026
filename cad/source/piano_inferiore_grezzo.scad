// Piano inferiore grezzo: quote confermate, nessun foro ancora quotato.
// Unita: millimetri.

piano_lunghezza = 170;
piano_larghezza = 160;
piano_spessore = 3;

// Origine al centro della faccia inferiore.
translate([-piano_larghezza / 2, -piano_lunghezza / 2, 0])
    cube([piano_larghezza, piano_lunghezza, piano_spessore]);
