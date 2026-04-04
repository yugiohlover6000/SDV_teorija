## Načrt fizične plasti komunikacijskega sistema

**Predmet:** Sistemi daljinskega vodenja

**Avtorji:**
- Rok Merlak - rok.merlak@student.um.si
- Niko Korošec - niko.korosec@student.um.si
- Jakob Sadar - jakob.sadar@student.um.si

**Uporabljene metode:** 
- NRZ (Non-Return-to-Zero) nivojska predstavitev
- CRC-32 zaščitno kodiranje
- Hammingovo kanalsko kodiranje
- BPSK (Binary Phase Shift Keying) modulacija

Naloga je bila zasnovati komunikacijski protokol za prenos podatkovnega sporočila na fizičnem nivoju. Definirali smo strukturo okvirja, dodali zaščito s CRC-32, uporabili Hammingovo kodiranje ter signal predstavili z NRZ in modulirali z BPSK. Na sprejemni strani smo izvedli obratni postopek in preverili pravilnost prenosa.

---

## 1. Struktura podatkovnega okvirja

Za prenos podatkov smo definirali lasten podatkovni okvir naslednje oblike:

```
[PREAMBLE][SOF][FRAME_TYPE][SRC_ADDR][DST_ADDR][PAYLOAD_LEN][PAYLOAD][CRC32][EOF]
```

Posamezna polja imajo naslednji pomen:

- **PREAMBLE (4 B)** – služi za sinhronizacijo sprejemnika
- **SOF (1 B)** – označuje začetek okvirja
- **FRAME_TYPE (1 B)** – določa tip sporočila
- **SRC_ADDR (1 B)** – naslov pošiljatelja
- **DST_ADDR (1 B)** – naslov sprejemnika
- **PAYLOAD_LEN (2 B)** – dolžina podatkovnega dela
- **PAYLOAD (N B)** – dejansko sporočilo
- **CRC32 (4 B)** – zaščita za zaznavanje napak
- **EOF (1 B)** – označuje konec okvirja