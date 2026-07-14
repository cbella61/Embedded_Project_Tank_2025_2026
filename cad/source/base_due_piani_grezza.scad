// Assieme grezzo dei due piani: solo quote confermate.
// Nessun foro e nessuna colonnina vengono aggiunti senza autorizzazione.
// Unita: millimetri.

piano_lunghezza = 170;
piano_larghezza = 160;
piano_spessore = 3;
luce_tra_piani = 40;

module piano() {
    translate([-piano_larghezza / 2, -piano_lunghezza / 2, 0])
        cube([piano_larghezza, piano_lunghezza, piano_spessore]);
}

color("LightSteelBlue")
    piano();

color("Gainsboro")
    translate([0, 0, piano_spessore + luce_tra_piani])
        piano();
