#=======================================================================
# SISTEMI DALJINSKEGA VODENJA
# Avtor: Rok Merlak, Niko Korosec, Jakob Sadar
# Program: 1. MAG MEH
# Datum: 1.4.2026
#=======================================================================
# BESEDILO NALOGE:
# Načrtajte fizično plast lastne komunikacije za prenos podatkovnega sporočila v obliki:
# Ime, Priimek, vpisna številka, država (Aleš Novak E300400500 Slovenija)
#=======================================================================

import struct
import binascii


#=======================================================================
# Naloga 1:
# Podatkovni okvir naj vsebuje vsaj:
# preambulo, začetek okvirja, kontrolne znake
# (tip okvirja, naslov pošiljatelja, naslov sprejemnika), konec okvirja

#Nivojska predstavitev
#    1. NRZ

# Zaščitno kodiranje
# CRC-32

#Kanalsko kodiranje
#    3. Hamming

#Modulacija
#    4. BPSK

# Podatki: Rok Merlak M1002506999 Slovenija
#=======================================================================


#=======================================================================
# Deklaracija podatkov
#=======================================================================
ime = "Rok"
priimek = "Merlak"
vpisna = "M1002506999"
drzava = "Slovenija"
#=======================================================================


#=======================================================================
# KONSTANTE OKVIRJA
#=======================================================================

PREAMBULA           = bytes([0xAA] * 7)                         # 7 B — sinhronizacija ure
SFD                 = bytes([0xAB])                             # 1 B — Start Frame Delimiter
TIP_OKVIRJA         = bytes([0x08, 0x00])                       # 2 B — IPv4
NASLOV_POSILJATELJA = bytes([0xAA,0xBB,0xCC,0xDD,0xEE,0xFF])    # 6 B MAC
NASLOV_SPREJEMNIKA  = bytes([0x11,0x22,0x33,0x44,0x55,0x66])    # 6 B MAC
EOF                 = bytes([0xFF, 0xFE])                       # 2 B — konec okvirja
#=======================================================================


# Import za CRC32
import binascii

# Funkcija za pretvorbo iz stringa v bytes
def text_to_bytes(text):
    #return ''.join(format(byte, '08b') for byte in text.encode('utf-8'))
    return text.encode('utf-8')

# Funkcija za preracun CRC32
def izracunaj_CRC32(data):

    val = binascii.crc32(data) # Ta funkcija vraca intiger
    return struct.pack('>I', val)



# Sestavljanje podatkovnega okvirja
def data_frame(ime,priimek,vpisna,drzava):

    print("\n" + "═"*65)
    print("  KORAK 1: SESTAVLJANJE PODATKOVNEGA OKVIRJA")
    print("═"*65)

    # Deklaracija sporocila ter pretvorba v bytes
    sporocilo = f"{ime}|{priimek}|{vpisna}|{drzava}"
    zapakirano = text_to_bytes(sporocilo)

    
    print("\n")
    print("Originalno sporocilo: ")
    print(sporocilo)
    print("\n")
    #print("Originalno sporocilo je tipa ")
    #print(type(sporocilo))
    #print("═"*65)

    print("Pretvorjeno sporocilo: ")
    print(zapakirano)
    print("\n")
    #print("Pretvorjeno sporocilo je tipa: ", type(zapakirano))
    #print("═"*65)
    
    glava = NASLOV_SPREJEMNIKA + NASLOV_POSILJATELJA + TIP_OKVIRJA
    fcs = izracunaj_CRC32(zapakirano + glava) 

    print("FCS after CRC32 je: ")
    print(fcs)
    print("\n")
    #print("FCS je tipa: ", type(fcs)) # Sanity check ce je FCS dejansko tipa bytes

    # Sestavljen okvir
    okvir = PREAMBULA + SFD + glava + zapakirano + fcs + EOF

    # Izpis
    print(f"  Sporočilo        : '{sporocilo}'")
    print(f"  Zapakirano       : {len(zapakirano)} B")
    print(f"  FCS (CRC-32)     : {fcs.hex(' ').upper()}")
    print(f"  Skupaj (okvir)   : {len(okvir)} B")

    return  okvir



data_frame(ime,priimek,vpisna,drzava)