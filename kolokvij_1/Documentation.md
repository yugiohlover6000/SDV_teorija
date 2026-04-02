## Načrt fizične plasti komunikacijskega sistema
---
Predmet: Sistemi Daljinskega Vodenja

Avtorji:
- Rok Merlak - rok.merlak@student.um.si
- Niko Korošec - niko.korosec@student.um.si
- Jakob Sadar - jakob.sadar@student.um.si

Uporabljene Metode: 
- NRZ (Non-Return-to-Zero) nivojska predstavitev
- CRC-32 zaščitno kodiranje
- Hamming (kanalsko kodiranje)
- BPSK (Binary Phase Shift Keying) modulacija

Naloga: 
Naloga je bila zasnovati lastno komunikacijsko shemo na fizičnem nivoju za prenos podatkovnega sporočila v obliki imena, priimka, vpisne številke in države. Najprej smo morali definirati strukturo podatkovnega okvirja, ki vključuje preambulo, začetek okvirja, kontrolne podatke, samo sporočilo in konec okvirja.

Nato smo na podatke dodali zaščito z uporabo CRC-32, da lahko zaznamo napake pri prenosu. Okvir smo nato pretvorili v bitni tok in ga pripravili za prenos z NRZ predstavitvijo. Za dodatno zanesljivost prenosa smo uporabili Hammingovo kodiranje, na koncu pa signal še modulirali z uporabo BPSK.

Na sprejemni strani se postopek obrne, kjer najprej demoduliramo signal, dekodiramo podatke, preverimo CRC in ponovno sestavimo originalno sporočilo.

---
