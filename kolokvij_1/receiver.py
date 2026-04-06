import math

def costas_loop(noisy_symbols: list, alpha: float = 0.05) -> list:
    """
    Costasov sprejemnik za BPSK.
    alpha — hitrost sledenja faze (loop gain)
    """
    phase  = 0.0
    synced = []

    for symbol in noisy_symbols:
        I = symbol * math.cos(phase)
        Q = symbol * math.sin(phase)
        
        error  = I * Q
        phase += alpha * error
        
        synced.append(I)

    return synced

def bpsk_demodulate(symbols):

    return [0 if symbol >= 0 else 1 for symbol in symbols]

def hamming_decode_nibble(coded_bits):
  
    p1, p2, d1, p4, d2, d3, d4 = coded_bits

    
    s1 = p1 ^ d1 ^ d2 ^ d4        # pokriva pos 1,3,5,7
    s2 = p2 ^ d1 ^ d3 ^ d4        # pokriva pos 2,3,6,7
    s4 = p4 ^ d2 ^ d3 ^ d4        # pokriva pos 4,5,6,7

    # Syndrom pove pozicijo napake (1-7), 0 = brez napake
    error_pos = s1 * 1 + s2 * 2 + s4 * 4

    # Popravi napako če obstaja
    if error_pos != 0:
        coded_bits = list(coded_bits)
        coded_bits[error_pos - 1] ^= 1  # flip bita

    # Izvleci podatkovne bite iz popravljenega bloka
    _, _, d1, _, d2, d3, d4 = coded_bits
    return [d1, d2, d3, d4], error_pos


def hamming_dekodiraj(kodirani_biti):
 
    dekodirani = []
    napake = []

    for i in range(0, len(kodirani_biti), 7):
        blok = kodirani_biti[i:i + 7]
        data_bits, error_pos = hamming_decode_nibble(blok)
        dekodirani.extend(data_bits)
        napake.append(error_pos)

    return dekodirani, napake