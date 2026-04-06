# Dokumentacija fizične plasti komunikacijskega sistema

**Predmet:** Sistemi daljinskega vodenja

**Avtorji:**
- Rok Merlak – rok.merlak@student.um.si
- Niko Korošec – niko.korosec@student.um.si
- Jakob Sadar – jakob.sadar@student.um.si

## 1. Uvod

<div align="justify">
V okviru naloge pri predmetu Sistemi daljinskega vodenja smo izdelali poenostavljen komunikacijski sistem za prenos sporočila preko fizične plasti. Namen naloge je bil prikazati celoten potek prenosa podatkov, od priprave sporočila na oddajni strani do sprejema, rekonstrukcije in preverjanja pravilnosti na sprejemni strani.

Najprej se besedilno sporočilo pretvori v bajte in vstavi v podatkovni okvir. Okvir vsebuje sinhronizacijska in naslovna polja, dolžino podatkovnega dela, uporabniške podatke ter CRC-32 kontrolno vsoto za zaznavanje napak. Nato se okvir pretvori v bitni tok, ta pa se dodatno zaščiti s Hammingovim kodiranjem. Kodirani biti se modulirajo z BPSK modulacijo, signalu pa se za simulacijo realnega kanala doda še šum.

Na sprejemni strani se najprej izvede sinhronizacija s Costasovo zanko, nato BPSK demodulacija in Hammingovo dekodiranje, s katerim lahko popravimo enobitne napake. Iz tako dobljenih podatkov se ponovno sestavi okvir, na koncu pa se s CRC-32 preveri, ali je bil prenos uspešen, in izlušči sprejeto sporočilo.
</div>

<p align="center"> <img src="Slike/OSI.gif" width="500"/> </p>


## 2. Uporabljene metode

Pri implementaciji sistema smo uporabili več osnovnih metod s področja digitalnih komunikacij:

- **CRC-32** za zaznavanje napak
- **Hamming(7,4)** za popravljanje enobitnih napak
- **BPSK** za modulacijo bitov
- **AWGN** za simulacijo šuma v kanalu
- **Costasovo** zanko za fazno sinhronizacijo sprejema
- **NRZ** prikaz za lažjo predstavitev bitnega toka

## 3. Zgradba programa

Program je razdeljen na štiri module, ki skupaj pokrivajo celoten potek komunikacije, vse od oddaje do sprejema in prikaza rezultatov.

### 3.1 `main.py`

Datoteka `main.py` vsebuje glavni potek programa. V njej določimo vhodno sporočilo, nato pa po vrsti izvedemo vse korake oddajne in sprejemne strani. Ta datoteka torej povezuje ostale module in skrbi za pravilen vrstni red izvajanja.

### 3.2 `transmitter.py`

Datoteka `transmitter.py` vsebuje glavni del oddajne strani. V njej so definirane konstante okvirja ter funkcije za sestavo okvirja, izračun CRC-32, pretvorbo okvirja v bitni tok, Hammingovo kodiranje, BPSK modulacijo in dodajanje šuma.

### 3.3 `receiver.py`

Datoteka `receiver.py` vsebuje funkcije sprejemne strani. Sem spadajo Costasova zanka, BPSK demodulacija ter Hammingovo dekodiranje in popravljanje enobitnih napak. Namen tega modula je, da iz prejetega signala ponovno dobi pravilne podatke.

### 3.4 `display.py`

Datoteka `display.py` vsebuje pomožne funkcije za izpis rezultatov v terminal. Uporablja se za prikaz okvirja, bitnega toka, Hammingovega kodiranja, modulacije, sprejemne strani in končne rekonstrukcije sporočila. Ta del ni ključen za samo delovanje sistema, je pa zelo uporaben za razlago in pregled nad posameznimi koraki.

## 4. Celoten workflow sistema

Celoten potek obdelave podatkov v programu lahko opišemo z naslednjim zaporedjem:

```text
besedilo
→ bajti
→ podatkovni okvir
→ CRC-32 zaščita
→ bitni tok
→ Hamming(7,4) kodiranje
→ BPSK modulacija
→ prenos skozi kanal z dodatnim šumom
→ Costasova zanka
→ BPSK demodulacija
→ Hamming dekodiranje
→ rekonstrukcija okvirja
→ preverjanje CRC
→ izluščenje sprejetega sporočila
```

## 5. Struktura podatkovnega okvirja

Za prenos sporočila je v programu definiran lasten podatkovni okvir. Okvir predstavlja urejeno zaporedje bajtov, v katerega se poleg uporabniških podatkov vključijo še sinhronizacijska, naslovna in kontrolna polja. Takšna struktura omogoča jasno določitev začetka in konca sporočila, identifikacijo pošiljatelja in sprejemnika ter preverjanje pravilnosti prenosa.

Oblika okvirja je naslednja:

```text
[PREAMBLE][SOF][FRAME_TYPE][SRC_ADDR][DST_ADDR][PAYLOAD_LEN][PAYLOAD][CRC32][EOF]
```

Posamezna polja imajo v implementaciji naslednji pomen:

- **PREAMBLE (3 B)** predstavlja sinhronizacijsko zaporedje na začetku okvirja. Uporablja se za lažje zaznavanje prihoda podatkov in za uskladitev sprejemnika z vhodnim signalom.
- **SOF (1 B)** oziroma Start of Frame označuje začetek dejanskega okvirja.
- **FRAME_TYPE (1 B)** določa tip okvirja. V implementaciji je uporabljen kot identifikacijsko polje z vnaprej določeno vrednostjo.
- **SRC_ADDR (6 B)** predstavlja naslov pošiljatelja.
- **DST_ADDR (6 B)** predstavlja naslov sprejemnika.
- **PAYLOAD_LEN (2 B)** vsebuje dolžino uporabniških podatkov v bajtih.
- **PAYLOAD (N B)** vsebuje dejansko besedilno sporočilo.
- **CRC32 (4 B)** vsebuje kontrolno vsoto, izračunano nad zaščitenim delom okvirja.
- **EOF (2 B)** označuje konec okvirja.

Zaščiteni del okvirja, nad katerim se izračuna CRC-32, obsega naslednja polja:

```text
[FRAME_TYPE][SRC_ADDR][DST_ADDR][PAYLOAD_LEN][PAYLOAD]
```

Polji PREAMBLE in SOF nista vključeni v CRC, ker služita predvsem sinhronizaciji in označevanju začetka okvirja, ne pa vsebinski zaščiti podatkov. Enako tudi zaključno polje EOF ni del zaščitenega dela okvirja.

Takšna zasnova okvirja omogoča, da sprejemna stran po rekonstrukciji bitnega toka ponovno razdeli podatke na posamezna polja, preveri dolžino uporabniškega dela, izračuna novo CRC vrednost ter jo primerja s prejeto kontrolno vsoto. Na ta način se ugotovi, ali je bil okvir med prenosom poškodovan.

V programu je struktura okvirja definirana s konstantami PREAMBLE, SOF, FRAME_TYPE, SRC_ADDR, DST_ADDR in EOF, medtem ko funkcija build_frame() iz vhodnega besedila sestavi celoten okvir, funkcija parse_frame() pa sprejeti okvir ponovno razčleni na posamezne sestavne dele.

## 6. Oddajna stran

Oddajna stran komunikacijskega sistema skrbi za pripravo uporabniškega sporočila na prenos skozi komunikacijski kanal. Njena naloga je, da vhodno besedilo najprej pretvori v ustrezno podatkovno obliko, ga zapakira v podatkovni okvir, zaščiti pred napakami in nato pretvori v signalno predstavitev, primerno za prenos.

V obravnavani implementaciji oddajna stran vključuje več zaporednih korakov. Najprej se sporočilo pretvori v bajte, nato se sestavi podatkovni okvir z vsemi pripadajočimi polji. Nad zaščitenim delom okvirja se izračuna CRC-32 kontrolna vsota. Celoten okvir se nato pretvori v bitni tok, ki se dodatno zaščiti s Hammingovim kodiranjem. Tako pripravljeni kodirani biti se modulirajo z BPSK modulacijo, na koncu pa se za simulacijo realnega komunikacijskega kanala signalu doda še šum vrste AWGN.

S tem se zaključi oddajni del sistema in pripravi signal, ki vstopi v kanal ter nato na sprejemno stran.

### 6.1 Pretvorba sporočila v bajte

Prvi korak oddajne strani je pretvorba vhodnega besedilnega sporočila v bajtno obliko. Računalniški komunikacijski sistemi namreč podatkov ne prenašajo neposredno kot znake, temveč kot zaporedja bajtov oziroma bitov. Zato je treba vhodni niz pred nadaljnjo obdelavo kodirati v ustrezen binarni zapis.

V programu to nalogo opravlja funkcija `text_to_bytes(text)`, ki vhodni niz pretvori v bajte z uporabo kodiranja UTF-8. Tak način zapisa omogoča, da se besedilo obravnava kot standardizirano zaporedje bajtov, primerno za vstavljanje v podatkovni okvir.

Ta korak je nujen, ker vse nadaljnje operacije v sistemu, kot so izračun dolžine podatkovnega dela, izračun CRC, pretvorba v bitni tok in kasnejše kodiranje, temeljijo na bajtni oziroma bitni predstavitvi podatkov. Če vhodno sporočilo ne bi bilo najprej pretvorjeno v bajte, ga ne bi bilo mogoče pravilno vključiti v komunikacijski okvir.

V implementaciji se ta pretvorba izvede z ukazom `text.encode("utf-8")`, rezultat pa predstavlja polje tipa `bytes`, ki se nato uporabi kot vsebina polja `PAYLOAD`.

### 6.2 Sestava okvirja

Ko je vhodno sporočilo pretvorjeno v bajtno obliko, se v naslednjem koraku sestavi celoten podatkovni okvir. Namen tega koraka je, da se uporabniški podatki dopolnijo še z vsemi potrebnimi polji, ki omogočajo sinhronizacijo, identifikacijo, določitev dolžine podatkovnega dela ter kasnejše preverjanje pravilnosti prenosa.

V programu sestavo okvirja izvaja funkcija `build_frame(payload_text)`. Ta najprej pretvori vhodno besedilo v bajte, nato določi dolžino podatkovnega dela in jo zapiše v dvobajtno polje `PAYLOAD_LEN`. Zatem sestavi zaščiteni del okvirja v obliki:

```text
[FRAME_TYPE][SRC_ADDR][DST_ADDR][PAYLOAD_LEN][PAYLOAD]
```

Na ta del se nato doda še CRC-32 kontrolna vsota, na začetek pa sinhronizacijska polja PREAMBLE in SOF, na konec pa zaključno polje EOF. Končni okvir je zato sestavljen v naslednji obliki:

```text
[PREAMBLE][SOF][FRAME_TYPE][SRC_ADDR][DST_ADDR][PAYLOAD_LEN][PAYLOAD][CRC32][EOF]
```

Takšna struktura omogoča, da sprejemna stran po prejemu podatkov natančno določi začetek okvirja, prebere dolžino uporabniških podatkov, izlušči sporočilo in preveri pravilnost prenosa. Funkcija build_frame() tako predstavlja osrednji korak oblikovanja podatkov za nadaljnji prenos skozi komunikacijski sistem.

### 6.3 CRC-32 zaščita

Po sestavi zaščitenega dela okvirja se izvede izračun kontrolne vsote CRC-32. Namen uporabe CRC je zaznavanje napak, ki lahko nastanejo med prenosom podatkov skozi komunikacijski kanal. CRC ne služi popravljanju napak, temveč preverjanju integritete prejetih podatkov.

V obravnavani implementaciji je CRC izračunan nad polji FRAME_TYPE, SRC_ADDR, DST_ADDR, PAYLOAD_LEN in PAYLOAD. Funkcija calculate_crc32(data) za podane podatke izračuna 32-bitno CRC vrednost s pomočjo knjižnice zlib, nato pa rezultat pretvori v štiribajtno obliko. Tako dobljena kontrolna vsota se doda v polje CRC32 znotraj okvirja.

Uporaba CRC-32 je pomembna zato, ker sprejemni strani omogoča končno preverjanje, ali je rekonstruirani okvir enak izvorno poslanemu okviru. Tudi če Hammingovo kodiranje popravi posamezne enobitne napake, CRC služi kot dodatni mehanizem za zaznavo morebitnih preostalih napak v podatkih. Na sprejemni strani se zato nad ponovno izluščenim zaščitenim delom okvirja še enkrat izračuna CRC in primerja s prejeto vrednostjo. Če se vrednosti ujemata, je prenos okvirja veljaven.

### 6.4 Pretvorba okvirja v bitni tok

Ko je podatkovni okvir sestavljen v bajtni obliki, ga je treba pred kanalskim kodiranjem in modulacijo pretvoriti v bitni tok. Razlog za to je, da Hammingovo kodiranje in BPSK modulacija delujeta na nivoju posameznih bitov, ne pa na nivoju celotnih bajtov.

V programu to nalogo opravlja funkcija `frame_to_bits(frame)`. Funkcija sprejme okvir tipa `bytes` in ga pretvori v seznam bitov. Vsak bajt obdela posebej, pri čemer bite bere od najbolj pomembnega proti najmanj pomembnemu bitu, torej od MSB proti LSB. Tako je zagotovljeno, da je vrstni red bitov enoličen in skladen skozi celoten sistem.

Ta korak je pomemben zato, ker predstavlja prehod iz bajtne predstavitve podatkov v zaporedje ničel in enic, nad katerim se nato izvajata Hammingovo kodiranje in modulacija. Brez te pretvorbe nadaljnja obdelava signala ne bi bila mogoča.

### 6.5 Hamming(7,4) kodiranje

Po pretvorbi okvirja v bitni tok sledi kanalsko kodiranje s Hammingovim kodom Hamming(7,4). Namen tega koraka je povečati odpornost prenosa proti napakam, ki lahko nastanejo v komunikacijskem kanalu. Hammingov kod omogoča zaznavo in popravljanje enobitne napake v posameznem 7-bitnem bloku.

Pri kodi Hamming(7,4) se vsak blok štirih podatkovnih bitov razširi v sedembitni blok. Poleg štirih podatkovnih bitov se dodajo še trije paritetni biti. V programu je razporeditev naslednja:

```text
pozicije: 1   2   3   4   5   6   7
vsebina:  p1  p2  d1  p4  d2  d3  d4
```

Paritetni biti se izračunajo z operatorjem XOR po pravilih:

```text
p1 = d1 ^ d2 ^ d4
p2 = d1 ^ d3 ^ d4
p4 = d2 ^ d3 ^ d4
```

To implementira funkcija hamming_encode_nibble(data_bits), ki iz štirih podatkovnih bitov sestavi en Hammingov blok. Nato funkcija hamming_kodiraj_bistream(biti) obdela celoten bitni tok po štiri bite naenkrat. Če dolžina vhodnega toka ni večkratnik štiri, funkcija na koncu doda ničelne bite, da je kodiranje mogoče izvesti nad celotnim tokom.

Uporaba Hammingovega kodiranja je v tem sistemu pomembna zato, ker omogoča osnovno popravljanje napak že pred končnim preverjanjem s CRC. CRC namreč napake samo zazna, Hamming pa lahko posamezne enobitne napake tudi popravi.

### 6.6 BPSK modulacija

Ko je bitni tok zaščiten s Hammingovim kodiranjem, se pretvori v signalno obliko z uporabo BPSK modulacije. BPSK oziroma Binary Phase Shift Keying je ena najpreprostejših digitalnih modulacijskih tehnik, pri kateri vsak bit predstavimo z enim od dveh faznih stanj nosilnega signala.

V tej implementaciji je modulacija poenostavljena na preslikavo bitov v dve amplitudni vrednosti:

```text
bit 0 se preslika v simbol +1.0
bit 1 se preslika v simbol -1.0
```

To nalogo izvaja funkcija bpsk_modulate(bits), ki za vhodni seznam bitov vrne seznam simbolov tipa float. Na ta način se binarni podatki pretvorijo v obliko, ki predstavlja signal pripravljen za prenos skozi kanal.

BPSK je uporabljen zato, ker je preprost za implementacijo in razlago, hkrati pa dovolj dobro ponazarja osnovni princip digitalne modulacije. Vsak bit je neposredno povezan z enim simbolom, kar omogoča pregledno simulacijo prenosa in kasnejše demodulacije na sprejemni strani.

### 6.7 Dodajanje šuma (AWGN)

Da bi simulirali bolj realne pogoje prenosa, se po modulaciji signalu doda šum. V programu je uporabljen model AWGN (Additive White Gaussian Noise), ki je eden izmed standardnih modelov šuma v telekomunikacijah. Tak šum se prišteje vsakemu simbolu posebej, njegova vrednost pa je naključno generirana po Gaussovi porazdelitvi.

Dodajanje šuma izvaja funkcija awgn_noise(signal, snr_db). Funkcija najprej iz podane vrednosti SNR v decibelih izračuna linearno vrednost razmerja signal-šum, nato določi standardni odklon šuma in ga prišteje vsakemu simbolu. Rezultat je nov seznam simbolov, ki predstavlja signal po prehodu skozi šumni kanal.

Namen dodajanja AWGN šuma je preveriti, kako se komunikacijski sistem obnaša v neidealnih razmerah. Brez šuma bi bil prenos popolnoma idealen, zato ne bi bilo mogoče prikazati dejanske uporabnosti Hammingovega kodiranja, demodulacije in preverjanja pravilnosti sprejetih podatkov. V programu je vpliv šuma dodatno viden tudi pri izpisu statistike, kjer se primerjajo poslani in demodulirani biti glede na izbrano vrednost SNR.

## 7. Sprejemna stran

Sprejemna stran komunikacijskega sistema skrbi za obratni postopek oddajne strani. Njena naloga je, da iz prejetega in s šumom obremenjenega signala ponovno pridobi bitni tok, popravi morebitne napake, rekonstruira podatkovni okvir in iz njega izlušči izvorno sporočilo.

V obravnavani implementaciji sprejemna stran vključuje več zaporednih korakov. Najprej se nad prejetimi BPSK simboli izvede osnovna fazna sinhronizacija s Costasovo zanko. Nato sledi BPSK demodulacija, pri kateri se simboli ponovno pretvorijo v bite. Nad dobljenim bitnim tokom se izvede Hammingovo dekodiranje, ki omogoča zaznavo in popravljanje enobitnih napak v posameznih blokih. Po dekodiranju se biti pretvorijo nazaj v bajte, iz njih pa se rekonstruira okvir. Na koncu se preveri pravilnost prejetega okvira s pomočjo CRC-32 in iz polja `PAYLOAD` pridobi sprejeto sporočilo.

### 7.1 Costasova zanka

Prvi korak sprejemne strani je osnovna fazna sinhronizacija prejetega signala. V komunikacijskih sistemih sprejemnik pogosto nima popolnoma usklajene faze z oddajnikom, zato je treba pred demodulacijo signal ustrezno poravnati. V obravnavani implementaciji to nalogo opravlja Costasova zanka.

Costasova zanka je povratni mehanizem, ki na osnovi prejetega signala ocenjuje fazno napako in postopno prilagaja interno fazo sprejemnika. V programu je to реализirano v funkciji `costas_loop(noisy_symbols, alpha=0.05)`. Za vsak prejeti simbol se izračunata komponenti:

- `I = symbol * cos(phase)`
- `Q = symbol * sin(phase)`

Na podlagi teh komponent se določi ocena napake `error = I * Q`, nato pa se faza posodobi po pravilu:

- `phase = phase + alpha * error`

Pri tem parameter `alpha` določa hitrost prilagajanja faze. Funkcija kot izhod vrne seznam sinhroniziranih simbolov, ki se nato uporabijo pri BPSK demodulaciji. 

Vloga Costasove zanke v sistemu je predvsem izboljšanje robustnosti sprejema. Čeprav je implementacija poenostavljena, dobro ponazori osnovno idejo faznega sledenja in pripravi signal za zanesljivejšo odločitev pri demodulaciji.

### 7.2 BPSK demodulacija

Po sinhronizaciji signala sledi BPSK demodulacija. Namen tega koraka je, da se prejeti simboli ponovno pretvorijo v binarno obliko, torej v zaporedje ničel in enic.

V programu to nalogo opravlja funkcija `bpsk_demodulate(symbols)`. Pravilo demodulacije je zelo preprosto:

- če je simbol večji ali enak nič, se interpretira kot bit `0`
- če je simbol manjši od nič, se interpretira kot bit `1`

Takšna odločitev temelji na dejstvu, da sta bila na oddajni strani bita `0` in `1` preslikana v simbola `+1.0` in `-1.0`. Demodulacija torej preveri predznak vsakega prejetega simbola in na tej osnovi določi pripadajoči bit.

Rezultat tega koraka je bitni tok, ki pa še ni nujno enak izvirnemu toku pred prenosom, saj lahko zaradi šuma pride do napačno določenih bitov. Zato sledi naslednji korak, Hammingovo dekodiranje.

### 7.3 Hamming dekodiranje in korekcija napak

Po BPSK demodulaciji sistem dobi zaporedje bitov, ki predstavljajo Hammingovo kodirane bloke. Namen naslednjega koraka je zaznati in po potrebi popraviti enobitne napake v posameznih 7-bitnih blokih ter iz njih ponovno izluščiti prvotne 4 podatkovne bite.

Osnovni korak dekodiranja izvaja funkcija `hamming_decode_nibble(coded_bits)`. Ta iz 7-bitnega bloka najprej prebere bite v razporeditvi:

```text
p1 p2 d1 p4 d2 d3 d4
```

Nato izračuna sindromske bite:

```text
s1 = p1 ^ d1 ^ d2 ^ d4
s2 = p2 ^ d1 ^ d3 ^ d4
s4 = p4 ^ d2 ^ d3 ^ d4
```

Iz teh treh vrednosti se določi položaj napake:

```text
error_pos = s1 * 1 + s2 * 2 + s4 * 4
```

Če je error_pos enak nič, v bloku ni zaznane napake. Če je različen od nič, funkcija obrne bit na ustrezni poziciji in s tem popravi enobitno napako. Nato iz popravljenega bloka izlušči podatkovne bite d1, d2, d3 in d4.

Dekodiranje celotnega bitnega toka izvaja funkcija hamming_dekodiraj(kodirani_biti), ki obdeluje vhodne bite po 7 naenkrat, za vsak blok pokliče hamming_decode_nibble() in gradi seznam dekodiranih bitov. Poleg tega shranjuje tudi informacijo o zaznani poziciji napake v posameznem bloku.

Ta korak je ključnega pomena, ker omogoča aktivno popravljanje napak, ki so nastale med prenosom. S tem se bistveno poveča verjetnost, da bo končno rekonstruirani okvir pravilen.

### 7.4 Rekonstrukcija okvirja

Ko so Hammingovi bloki dekodirani, sprejemna stran ponovno dobi bitni tok, ki predstavlja prvotni okvir pred kanalskim kodiranjem. Da bi ga bilo mogoče analizirati na ravni polj okvirja, ga je treba pretvoriti nazaj v bajtno obliko.

V programu to nalogo opravlja funkcija bits_to_bytes(bits). Funkcija vhodni seznam bitov združi v skupine po osem bitov in iz vsake skupine sestavi en bajt. Če število bitov ni večkratnik osem, se na koncu po potrebi dodajo ničle, da je pretvorba mogoča. Rezultat je objekt tipa bytes, ki predstavlja rekonstruiran okvir.

Nato se ta okvir obdela s funkcijo parse_frame(frame), ki iz bajtnega zaporedja ponovno izlušči posamezna polja, kot so PREAMBLE, SOF, FRAME_TYPE, SRC_ADDR, DST_ADDR, PAYLOAD_LEN, PAYLOAD, CRC32 in EOF. Tako sprejemna stran ponovno pridobi strukturirano predstavitev prejete informacije.

### 7.5 CRC preverjanje

Po rekonstrukciji okvirja sledi preverjanje njegove pravilnosti z uporabo CRC-32. Namen tega koraka je ugotoviti, ali je rekonstruirani zaščiteni del okvirja enak tistemu, ki je bil poslan na oddajni strani.

Funkcija parse_frame(frame) iz prejetega okvirja izlušči prejeto vrednost CRC32, nato pa nad polji FRAME_TYPE, SRC_ADDR, DST_ADDR, PAYLOAD_LEN in PAYLOAD ponovno izračuna CRC s funkcijo calculate_crc32(protected_part). Dobljena vrednost se primerja s prejeto kontrolno vsoto. Če se vrednosti ujemata, je rezultat preverjanja pozitiven in polje crc_ok dobi vrednost True. V nasprotnem primeru je okvir označen kot poškodovan.

CRC preverjanje predstavlja zadnji mehanizem za potrjevanje integritete podatkov. Tudi če Hammingovo kodiranje popravi posamezne napake, CRC omogoča dodatno končno kontrolo, ali je vsebina zaščitenega dela okvirja res pravilna.

### 7.6 Pridobitev originalnega sporočila

Če je rekonstrukcija okvirja uspešna, lahko sprejemna stran iz polja PAYLOAD pridobi uporabniško sporočilo. To predstavlja zadnji korak celotnega sistema, saj se signalna oblika podatkov ponovno pretvori v človeku berljivo besedilo.

V programu funkcija parse_frame(frame) izlušči polje payload in ga dekodira v niz z ukazom payload.decode("utf-8"). Rezultat shrani v element payload_text, ki predstavlja sprejeto besedilno sporočilo.

S tem je celoten komunikacijski cikel zaključen. Sistem je iz vhodnega besedila na oddajni strani ustvaril signal za prenos, ga poslal skozi kanal s šumom, nato pa na sprejemni strani ponovno rekonstruiral okvir in iz njega pridobil izvorno sporočilo. Uspešnost prenosa se dokončno potrdi z ujemanjem vsebine polja PAYLOAD in z veljavnim CRC preverjanjem.


## 8. Opis vseh funkcij

### 8.1 Funkcije modula `transmitter.py`

Modul `transmitter.py` vsebuje funkcije oddajne strani komunikacijskega sistema ter nekaj pomožnih pretvorbenih funkcij. V njem so definirane konstante podatkovnega okvirja, funkcije za pretvorbo med besedilom, bajti in biti, funkcije za sestavo ter razčlenjevanje okvirja, funkcije za Hammingovo kodiranje in funkcije za modulacijo ter simulacijo šuma.

#### Konstante okvirja

Na začetku modula so definirane konstante `PREAMBLE`, `SOF`, `FRAME_TYPE`, `SRC_ADDR`, `DST_ADDR` in `EOF`. Te konstante določajo fiksna polja podatkovnega okvirja. `PREAMBLE` predstavlja začetno sinhronizacijsko zaporedje treh bajtov `0xAA`, `SOF` označuje začetek okvirja, `FRAME_TYPE` določa tip okvirja, `SRC_ADDR` in `DST_ADDR` predstavljata izvorni in ciljni naslov, `EOF` pa označuje konec okvirja. Te vrednosti se uporabljajo pri sestavi okvirja v funkciji `build_frame()` ter pri razčlenjevanju okvirja v funkciji `parse_frame()`.
#### `text_to_bytes(text)`

Funkcija `text_to_bytes(text)` pretvori vhodno besedilo v bajtno obliko z uporabo kodiranja UTF-8. Njena naloga je, da vhodni niz tipa `str` spremeni v objekt tipa `bytes`, ki ga je mogoče vključiti v podatkovni okvir. Funkcija je zelo preprosta, vendar predstavlja nujen prvi korak pri pripravi uporabniškega sporočila za nadaljnjo obdelavo. Uporabljena je znotraj funkcije `build_frame()`, kjer se vhodno sporočilo pretvori v vsebino polja `PAYLOAD`.

#### `int_to_bytes(value: int, length: int) -> bytes`

Funkcija `int_to_bytes(value, length)` pretvori celoštevilsko vrednost v bajtno predstavitev podane dolžine. Pretvorba uporablja vrstni red bajtov `big-endian`, kar pomeni, da je najpomembnejši bajt zapisan prvi. V programu se ta funkcija uporablja predvsem za zapis dolžine uporabniških podatkov v polje `PAYLOAD_LEN` ter tudi posredno pri zapisu izračunane CRC-32 kontrolne vsote v štiribajtni obliki. Funkcija je pomembna zato, ker omogoča konsistentno pretvorbo številskih vrednosti v obliko, primerno za vstavljanje v okvir.

#### `bytes_to_int(data: bytes) -> int`

Funkcija `bytes_to_int(data)` izvaja obratno operacijo kot `int_to_bytes()`. Bajtno zaporedje pretvori nazaj v celoštevilsko vrednost, prav tako z uporabo `big-endian` vrstnega reda. Njena glavna vloga v programu je pri razčlenjevanju okvirja v funkciji `parse_frame()`, kjer se iz dvobajtnega polja `PAYLOAD_LEN` prebere dolžina uporabniškega dela. Na tej osnovi lahko program določi, kje se `PAYLOAD` konča in kje se začne polje `CRC32`.

#### `build_payload(ime: str, priimek: str, vpisna: str, drzava: str) -> str`

Funkcija `build_payload(ime, priimek, vpisna, drzava)` iz več ločenih podatkovnih elementov sestavi enoten besedilni niz v obliki `ime|priimek|vpisna|drzava`. Gre za pomožno funkcijo, ki omogoča pripravo standardizirane vsebine uporabniškega sporočila. V trenutnem poteku programa ta funkcija ni ključni del glavnega workflowa, je pa uporabna, kadar želimo strukturiran `PAYLOAD` sestaviti iz več logičnih polj namesto iz enega že pripravljenega niza.

#### `calculate_crc32(data)`

Funkcija `calculate_crc32(data)` izračuna 32-bitno CRC kontrolno vsoto za podane podatke. Pri tem uporablja funkcijo `zlib.crc32`, rezultat pa maskira z `0xFFFFFFFF`, da ostane vrednost vedno obravnavana kot nepredznačeno 32-bitno število. Nato se rezultat s funkcijo `int_to_bytes()` pretvori v štiribajtno obliko. Funkcija se uporablja v dveh ključnih delih programa: pri sestavi okvirja v `build_frame()`, kjer se izračunana vrednost doda v polje `CRC32`, ter pri razčlenjevanju okvirja v `parse_frame()`, kjer se CRC ponovno izračuna za preverjanje pravilnosti prenosa. Njena glavna vloga je zaznavanje napak v zaščitenem delu okvirja. 

#### `frame_to_bits(frame)`

Funkcija `frame_to_bits(frame)` pretvori podatkovni okvir iz bajtne oblike v bitni tok. Vsak bajt obdela posebej in iz njega izlušči vseh osem bitov, pri čemer gre od najbolj pomembnega proti najmanj pomembnemu bitu. Rezultat funkcije je seznam ničel in enic, ki predstavlja binarni zapis celotnega okvirja. Ta korak je potreben zato, ker Hammingovo kodiranje in BPSK modulacija delujeta na ravni bitov. Funkcija zato predstavlja most med bajtnim nivojem okvirja in signalnim nivojem nadaljnje obdelave. 

#### `bits_to_bytes(bits: list) -> bytes`

Funkcija `bits_to_bytes(bits)` izvaja obratno pretvorbo kot `frame_to_bits()`. Vhodni seznam bitov najprej po potrebi dopolni z ničlami, če njegova dolžina ni večkratnik osem. Nato bite združuje v skupine po osem in iz vsake skupine zgradi en bajt. Rezultat je objekt tipa `bytes`. Čeprav se ta funkcija vsebinsko uporablja predvsem na sprejemni strani pri rekonstrukciji okvirja, je implementirana v istem modulu kot ostale osnovne pretvorbe. Njena vloga je pretvoriti dekodiran bitni tok nazaj v bajtno obliko, primerno za ponovno razčlenitev okvirja.

#### `nrz_encode(bits)`

Funkcija `nrz_encode(bits)` pretvori binarni tok v nivojsko predstavitev NRZ. Za vsak vhodni bit vrne ustrezno amplitudno raven: za bit `1` vrne `+1.0`, za bit `0` pa `-1.0`. Ta funkcija v glavni logiki prenosa ni osrednja, saj sistem za dejanski prenos uporablja BPSK modulacijo, je pa koristna za vizualizacijo in prikaz signalnih nivojev pri analizi delovanja sistema. Funkcija zato služi predvsem kot pomožni prikaz bitnega toka na bolj signalni ravni. 

#### `hamming_encode_nibble(data_bits)`

Funkcija `hamming_encode_nibble(data_bits)` predstavlja osnovno funkcijo za Hammingovo kodiranje. Sprejme štiri podatkovne bite `d1`, `d2`, `d3`, `d4` in iz njih izračuna tri paritetne bite `p1`, `p2` in `p4`. Pri tem uporablja operator XOR po pravilih Hammingovega kode Hamming(7,4). Izhod funkcije je sedembitni blok v razporeditvi `p1 p2 d1 p4 d2 d3 d4`. To pomeni, da funkcija iz 4-bitnega vhodnega bloka naredi 7-bitni kodirani blok, ki omogoča kasnejšo zaznavo in popravljanje enobitnih napak. Gre za eno najpomembnejših funkcij v celotnem sistemu, saj implementira osnovni mehanizem kanalske zaščite podatkov. 

#### `hamming_kodiraj_bistream(biti)`

Funkcija `hamming_kodiraj_bistream(biti)` razširi delovanje `hamming_encode_nibble()` na celoten bitni tok. Če dolžina vhodnega seznama bitov ni večkratnik štiri, funkcija na konec doda ničelne bite, da je tok mogoče razdeliti na 4-bitne bloke. Nato vhodni tok obdeluje po štiri bite naenkrat, vsak blok kodira s funkcijo `hamming_encode_nibble()` in rezultate združuje v enoten kodirani bitni tok. Namen te funkcije je pretvoriti celoten podatkovni okvir v Hammingovo zaščiteno obliko, pripravljeno za nadaljnjo modulacijo in prenos. 

#### `error_simulation(coded_bits, pos)`

Funkcija `error_simulation(coded_bits, pos)` služi za testiranje sistema. Sprejme že kodiran bitni tok, ga pretvori v seznam in na podani poziciji obrne en bit. Na ta način umetno simulira enobitno napako v prenosu. Ta funkcija ni nujen del osnovnega workflowa, je pa zelo uporabna pri preverjanju, ali Hammingovo dekodiranje na sprejemni strani pravilno zazna in popravi napako. Gre torej za pomožno razvojno funkcijo za validacijo implementacije. 

#### `build_frame(payload_text)`

Funkcija `build_frame(payload_text)` je ena izmed osrednjih funkcij modula. Njena naloga je, da iz vhodnega besedila sestavi celoten podatkovni okvir. Najprej pretvori besedilo v bajte s funkcijo `text_to_bytes()`, nato določi dolžino uporabniškega dela in jo pretvori v dvobajtno obliko s funkcijo `int_to_bytes()`. Zatem sestavi zaščiteni del okvirja v obliki `FRAME_TYPE + SRC_ADDR + DST_ADDR + PAYLOAD_LEN + PAYLOAD`. Nad tem delom izračuna CRC-32 s funkcijo `calculate_crc32()`. Na koncu doda še sinhronizacijska polja `PREAMBLE` in `SOF` na začetek ter `EOF` na konec. Rezultat funkcije je celoten okvir tipa `bytes`, pripravljen za pretvorbo v bitni tok in nadaljnji prenos. Ta funkcija torej združuje več osnovnih korakov oddajne strani v eno celoto.

#### `parse_frame(frame: bytes) -> Dict`

Funkcija `parse_frame(frame)` izvaja obratni postopek od `build_frame()`. Njena naloga je, da sprejeti okvir razdeli na posamezna polja in preveri njegovo pravilnost. Najprej določi dolžine vseh fiksnih polj, nato izračuna začetne in končne indekse za posamezne dele okvirja. Iz polja `PAYLOAD_LEN` prebere dolžino podatkovnega dela s funkcijo `bytes_to_int()`, na podlagi tega pa določi mejo polja `PAYLOAD`. Nato iz okvirja izlušči vse ključne dele: `preamble`, `sof`, `frame_type`, `src_addr`, `dst_addr`, `payload`, `received_crc` in `eof`. Poleg tega ponovno izračuna CRC nad zaščitenim delom okvirja in ga primerja s prejeto vrednostjo. Rezultat funkcije je slovar, ki vsebuje tako posamezna polja okvirja kot tudi informacijo `crc_ok`, ki pove, ali je kontrolna vsota pravilna. Ta funkcija je ključna za analizo, preverjanje in končno rekonstrukcijo sprejetih podatkov. 

#### `code_frame_with_hamming(frame: bytes) -> List[int]`

Funkcija `code_frame_with_hamming(frame)` predstavlja kratko povezovalno funkcijo. Najprej z `frame_to_bits()` pretvori okvir v bitni tok, nato pa dobljene bite pošlje v `hamming_kodiraj_bistream()`. Rezultat je Hammingovo kodiran seznam bitov. Funkcija ne uvaja nove logike, vendar poenostavi uporabo sistema, saj v enem koraku poveže dva pomembna dela oddajne strani: pretvorbo okvirja v bite in kanalsko kodiranje.

#### `bpsk_modulate(bits)`

Funkcija `bpsk_modulate(bits)` izvaja BPSK modulacijo nad vhodnim bitnim tokom. Za vsak bit vrne ustrezen simbol: bit `0` preslika v `+1.0`, bit `1` pa v `-1.0`. Izhod funkcije je seznam realnih vrednosti, ki predstavljajo poenostavljeno signalno obliko za prenos skozi kanal. Čeprav je BPSK v teoriji definirana prek dveh faznih stanj nosilca, je v tej implementaciji modulacija predstavljena z dvema simbolnima amplitudama, kar je za simulacijo in razlago delovanja povsem ustrezno. Funkcija je ključna zato, ker predstavlja prehod iz bitnega sveta v signalni svet prenosa.

#### `awgn_noise(signal, snr_db)`

Funkcija `awgn_noise(signal, snr_db)` simulira vpliv šuma v komunikacijskem kanalu. Na podlagi podane vrednosti SNR v decibelih najprej izračuna linearno razmerje signal-šum, nato iz tega določi standardni odklon Gaussovega šuma. Vsakemu simbolu v vhodnem signalu nato prišteje naključno vrednost, generirano z Gaussovo porazdelitvijo. Rezultat je nov seznam simbolov, ki predstavlja signal po prehodu skozi kanal z dodatnim belim Gaussovim šumom. Namen funkcije je ustvariti neidealne pogoje prenosa, v katerih lahko preverimo delovanje demodulacije, Hammingove korekcije in CRC preverjanja.

### 8.2 Funkcije modula `receiver.py`

Modul `receiver.py` vsebuje funkcije sprejemne strani komunikacijskega sistema. Njegova naloga je, da iz prejetega signala ponovno pridobi bitni tok, izvede demodulacijo, zazna in popravi enobitne napake s Hammingovim dekodiranjem ter pripravi podatke za rekonstrukcijo okvirja. Modul tako predstavlja ključen del obratnega postopka oddajne strani.

#### `costas_loop(noisy_symbols: list, alpha: float = 0.05) -> list`

Funkcija `costas_loop(noisy_symbols, alpha=0.05)` izvaja poenostavljeno fazno sinhronizacijo sprejetih BPSK simbolov. Sprejme seznam simbolov, ki so bili med prenosom obremenjeni s šumom, in nad njimi izvede osnovni Costasov algoritem. V funkciji se za vsak simbol izračunata komponenti `I` in `Q`, ki sta odvisni od trenutne faze sprejemnika. Iz njunega produkta se določi ocena napake, na podlagi katere se faza sproti popravlja. Sinhronizirana komponenta `I` se nato shrani v izhodni seznam.

Namen funkcije je zmanjšati vpliv faznega neskladja med oddajnikom in sprejemnikom. Čeprav je implementacija poenostavljena, dobro ponazarja osnovni princip Costasove zanke kot povratnega mehanizma za sledenje fazi. Parameter `alpha` določa hitrost prilagajanja faze, zato vpliva na odzivnost zanke.

#### `bpsk_demodulate(symbols)`

Funkcija `bpsk_demodulate(symbols)` izvaja BPSK demodulacijo. Njena naloga je, da vsak sprejeti simbol pretvori nazaj v ustrezen bit. Pravilo demodulacije je preprosto: če je simbol večji ali enak nič, se interpretira kot bit `0`, sicer kot bit `1`.

Funkcija s tem predstavlja obratni korak funkcije `bpsk_modulate()` na oddajni strani. Rezultat je seznam bitov, ki pa lahko zaradi vpliva šuma še vedno vsebuje napake. Zato se nad tem tokom nato izvede Hammingovo dekodiranje.

#### `hamming_decode_nibble(coded_bits)`

Funkcija `hamming_decode_nibble(coded_bits)` predstavlja osnovni gradnik sprejemne strani za Hammingovo dekodiranje. Sprejme en 7-bitni Hammingov blok v razporeditvi `p1 p2 d1 p4 d2 d3 d4` in iz njega izračuna sindromske bite `s1`, `s2` in `s4`. Ti biti določajo položaj morebitne enobitne napake v bloku.

Na podlagi sindroma funkcija določi vrednost `error_pos`. Če je ta enaka nič, napaka ni zaznana. Če je različna od nič, funkcija na ustrezni poziciji obrne bit in s tem popravi blok. Nato iz popravljenega bloka izlušči samo podatkovne bite in jih vrne skupaj s pozicijo napake.

Gre za eno ključnih funkcij celotnega sistema, saj omogoča aktivno korekcijo enobitnih napak, ki jih je povzročil komunikacijski kanal. 

#### `hamming_dekodiraj(kodirani_biti)`

Funkcija `hamming_dekodiraj(kodirani_biti)` razširi dekodiranje na celoten Hammingovo kodiran bitni tok. Vhodne bite obdeluje v blokih po 7, za vsak blok pokliče funkcijo `hamming_decode_nibble()` in dekodirane 4-bitne podatke združuje v enoten seznam.

Poleg dekodiranih podatkov funkcija vodi tudi seznam zaznanih napak, kjer je za vsak blok zapisana pozicija morebitne popravljene napake. To je uporabno pri analizi uspešnosti prenosa in pri prikazu delovanja sistema.

Funkcija je pomembna zato, ker predstavlja glavni prehod od šumom obremenjenega, Hammingovo kodiranega bitnega toka nazaj do podatkovnega bitnega toka, iz katerega je mogoče rekonstruirati okvir.

### 8.3 Funkcije modula `main.py`

Modul `main.py` predstavlja glavno vstopno točko programa. Njegova naloga ni implementacija posameznih komunikacijskih metod, temveč povezovanje funkcij oddajne in sprejemne strani v smiseln ter pregleden potek izvajanja. V njem je določen vrstni red obdelave podatkov od začetnega besedilnega sporočila do končne rekonstrukcije sprejetega okvirja. 
#### `main()`

Funkcija `main()` predstavlja osrednjo organizacijsko funkcijo celotnega programa. Na začetku definira vhodno besedilno sporočilo in vrednost razmerja signal-šum `SNR`, nato pa sproži zaporedje vseh ključnih korakov komunikacijskega sistema.

V prvem delu funkcija kliče postopke oddajne strani. Najprej prikaže izvorno sporočilo, nato s funkcijo `build_frame()` sestavi podatkovni okvir in ga s funkcijo `parse_frame()` razčleni za namen prikaza. Sledijo izpisi okvirja v šestnajstiški in bitni obliki ter prikaz posameznih sekcij okvirja. Nato funkcija sproži Hammingovo kodiranje in BPSK modulacijo z dodanim šumom. Ta del predstavlja simulacijo priprave podatkov za prenos skozi komunikacijski kanal.

V drugem delu funkcija izvede postopke sprejemne strani. Nad moduliranimi simboli pokliče `print_costas()`, ki prikaže delovanje Costasove zanke, nato izvede BPSK demodulacijo s funkcijo `print_demodulated_bpsk()`, Hammingovo dekodiranje s `print_decoded_hamming()` in na koncu rekonstrukcijo okvirja s funkcijo `print_received_frame()`. S tem funkcija zaključi celoten komunikacijski cikel od oddaje do sprejema.

Funkcija `main()` je pomembna zato, ker določa celoten workflow sistema in skrbi, da se posamezne funkcije izvajajo v pravilnem zaporedju. Sama ne vsebuje bistvene signalne ali kodirne logike, temveč predstavlja organizacijsko ogrodje, ki povezuje vse ostale module.

### 8.4 Funkcije modula `display.py`

Modul `display.py` vsebuje pomožne funkcije za izpis in vizualno razlago posameznih korakov komunikacijskega sistema v terminalu. Njegova glavna naloga je prikazovati podatke v človeku berljivi obliki, kar omogoča lažjo analizo delovanja sistema, preverjanje pravilnosti posameznih korakov in boljše razumevanje celotnega prenosa. Funkcije tega modula niso nujne za samo delovanje komunikacijskega sistema, so pa zelo pomembne za predstavitev rezultatov.

#### `bytes_to_hex(data: bytes) -> str`

Funkcija `bytes_to_hex(data)` pretvori bajtno zaporedje v niz šestnajstiških vrednosti. Vsak bajt zapiše v obliki dveh hex znakov, posamezne vrednosti pa loči s presledki. Funkcija se uporablja za preglednejši prikaz podatkovnega okvirja in njegovih posameznih polj.

#### `bytes_to_bitstring(data: bytes) -> str`

Funkcija `bytes_to_bitstring(data)` pretvori bajtno zaporedje v niz bitnih predstavitev. Vsak bajt zapiše kot osem-bitni binarni niz. Namen funkcije je omogočiti neposreden vpogled v bitno strukturo okvirja in njegovih sestavnih delov.

#### `print_original_message(message)`

Funkcija `print_original_message(message)` v terminal izpiše izvorno sporočilo pred začetkom obdelave. Poleg same vsebine prikaže tudi tip podatka. Gre za uvodni prikaz, ki uporabniku pokaže, iz katerega vhodnega podatka se začne celoten komunikacijski proces.

#### `print_frame_hex(frame: bytes) -> None`

Funkcija `print_frame_hex(frame)` izpiše podatkovni okvir v šestnajstiški obliki. Za pretvorbo uporablja funkcijo `bytes_to_hex()`. Njen namen je hiter in pregleden prikaz celotnega okvirja v obliki, ki je standardna v komunikacijskih in omrežnih sistemih.

#### `print_frame_sections(frame: bytes) -> None`

Funkcija `print_frame_sections(frame)` razčleni okvir na posamezna polja in jih izpiše v preglednici skupaj s hex in bitno predstavitvijo. Za razčlenitev uporablja funkcijo `parse_frame(frame)`, nato pa oblikuje izpis polj `PREAMBLE`, `SOF`, `FRAME_TYPE`, `SRC_ADDR`, `DST_ADDR`, `PAYLOAD_LEN`, `PAYLOAD`, `CRC32` in `EOF`. Funkcija je zelo uporabna za razumevanje notranje strukture okvirja in za preverjanje, ali so njegova polja pravilno sestavljena.

#### `plot_frame_bits(frame: bytes, max_bits: int = 64) -> None`

Funkcija `plot_frame_bits(frame, max_bits=64)` izriše prvih nekaj bitov okvirja s pomočjo knjižnice `matplotlib`. Namen funkcije je grafični prikaz bitnega poteka, zato je uporabna predvsem pri dodatni analizi ali predstavitvi delovanja sistema. V glavnem workflowu ni bistvena, predstavlja pa koristno razširitev terminalskega izpisa.

#### `bits_to_nrz(bits: list[int]) -> list[int]`

Funkcija `bits_to_nrz(bits)` pretvori bitni tok v NRZ nivojsko predstavitev. Vsak bit preslika v enega izmed dveh nivojev, kar omogoča prikaz signalne oblike na osnovni ravni. Funkcija se uporablja kot pomožno vizualizacijsko sredstvo in ne kot glavni del dejanskega prenosa, saj sistem za simulacijo kanala uporablja BPSK modulacijo.

#### `print_hamming_coded_bits(frame: bytes) -> list`

Funkcija `print_hamming_coded_bits(frame)` najprej pretvori okvir v bitni tok, nato pa ta tok Hammingovo kodira. Rezultat prikaže po posameznih blokih, tako da za vsak 4-bitni podatkovni blok izpiše pripadajoči 7-bitni Hammingov blok in izračunane paritetne bite. Poleg tega izpiše tudi statistiko, kot so število originalnih bitov, število kodiranih bitov, število blokov in odstotek dodatnega bitnega overhead-a. Funkcija je zelo uporabna za razlago delovanja Hammingovega kodiranja.

#### `print_bpsk(frame: bytes, snr_db: float = 10.0) -> tuple`

Funkcija `print_bpsk(frame, snr_db=10.0)` izvede več korakov zapored: okvir pretvori v bite, Hammingovo kodira dobljeni tok, izvede BPSK modulacijo in nato doda šum z uporabo modela AWGN. Rezultat prikaže v tabelarni obliki po blokih, kjer izpiše Hammingove bite, idealne BPSK simbole in s šumom obremenjene simbole. Na koncu izpiše še statistiko o številu simbolov, izbranem SNR in številu bitnih napak po demodulaciji. Funkcija ima dvojno vlogo: po eni strani izvaja ključne korake prenosa, po drugi strani pa jih pregledno prikazuje uporabniku. 

#### `print_costas(noisy_symbols)`

Funkcija `print_costas(noisy_symbols)` izvede Costasovo sinhronizacijo nad vhodnimi šumnimi simboli in izpiše primerjavo med vhodnim in sinhroniziranim signalom. Za prve simbole prikaže vrednosti pred in po sinhronizaciji ter pripadajoče bite. Namen funkcije je prikazati vpliv Costasove zanke na signal in omogočiti vpogled v to, ali je bila fazna poravnava uspešna.

#### `print_demodulated_bpsk(synced_symbols: list) -> list`

Funkcija `print_demodulated_bpsk(synced_symbols)` sprejme sinhronizirane BPSK simbole, nad njimi izvede demodulacijo in rezultat izpiše po blokih. Za vsak blok prikaže vrednosti simbolov in pripadajoči 7-bitni demodulirani zapis. Na ta način lahko uporabnik vidi neposredno povezavo med signalnimi vrednostmi in končno bitno odločitvijo.

#### `print_decoded_hamming(demod_bits: list) -> list`

Funkcija `print_decoded_hamming(demod_bits)` nad demoduliranimi biti izvede Hammingovo dekodiranje in prikaže rezultat po blokih. Za vsak blok izpiše dekodirane 4-bitne podatke in informacijo o morebitni zaznani oziroma popravljeni napaki. Poleg tega poda še skupno statistiko o številu blokov, številu popravljenih napak in številu blokov brez napake. Funkcija je zato zelo primerna za razlago mehanizma korekcije napak na sprejemni strani.

#### `print_received_frame(decoded_bits: list) -> bytes`

Funkcija `print_received_frame(decoded_bits)` dekodirani bitni tok pretvori nazaj v bajtno obliko, nato pa izpiše rekonstruirani okvir v hex in bitni obliki. Poleg tega okvir ponovno razčleni s funkcijo `parse_frame()` in izpiše posamezna polja ter vsebino sprejetega sporočila. Na koncu prikaže tudi rezultat CRC preverjanja. Gre za zaključni prikaz, ki uporabniku pokaže, ali je bil celoten komunikacijski cikel uspešen in kakšna je končna vsebina sprejetega `PAYLOAD`.

## 9. Zaključek

V nalogi smo zasnovali in implementirali poenostavljen komunikacijski sistem na fizični plasti, ki prikazuje celoten potek prenosa podatkov od besedilnega sporočila do njegove rekonstrukcije na sprejemni strani. Sistem vključuje sestavo lastnega podatkovnega okvirja, zaščito s CRC-32, kanalsko kodiranje s Hammingovim kodom Hamming(7,4), BPSK modulacijo, simulacijo šuma z modelom AWGN ter sprejemni postopek s Costasovo zanko, demodulacijo, dekodiranjem in preverjanjem pravilnosti podatkov. 

Rezultat implementacije je delujoča simulacija komunikacijskega prenosa, ki omogoča tako tehnično analizo kot tudi didaktičen prikaz delovanja posameznih faz prenosa. Posebna prednost programa je modularna zasnova, saj so oddajna stran, sprejemna stran, glavni workflow in prikaz rezultatov ločeni v samostojne module. To omogoča boljšo preglednost kode, lažje testiranje posameznih funkcij ter enostavnejše nadaljnje razširitve sistema.

Sistem dobro ponazori razliko med zaznavanjem napak in popravljanjem napak. CRC-32 služi preverjanju integritete zaščitenega dela okvirja, medtem ko Hammingovo kodiranje omogoča aktivno popravljanje enobitnih napak. V kombinaciji z BPSK modulacijo in simulacijo šumnega kanala takšna zasnova predstavlja uporaben in pregleden primer osnovnih principov digitalnih komunikacijskih sistemov.