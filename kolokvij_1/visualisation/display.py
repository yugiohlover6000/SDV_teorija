import matplotlib.pyplot as plt
from typing import Dict
from transmitter import (
    bits_to_bytes,
    frame_to_bits, 
    parse_frame,
    hamming_kodiraj_bistream,
    bpsk_modulate, 
    awgn_noise
)
from receiver import(
    costas_loop,
    bpsk_demodulate,
    hamming_decode_nibble,
    hamming_dekodiraj
) 

def bytes_to_hex(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def bytes_to_bitstring(data: bytes) -> str:
    return " ".join(f"{byte:08b}" for byte in data)


def print_original_message(message):
    print("=" * 72)
    #print("\n")
    print("Originalno sporočilo:")
    print(message + " ")
    print(type(message))
    #print("\n")
    print("=" * 72)
    return message


def print_frame_hex(frame: bytes) -> None:
    print(bytes_to_hex(frame))


def print_frame_sections(frame: bytes) -> None:
    parsed = parse_frame(frame) # parse the frame to extract sections for display, better than slicing raw bytes 

    sections = {
        "PREAMBLE":    parsed["preamble"],
        "SOF":         parsed["sof"],
        "FRAME_TYPE":  parsed["frame_type"],
        "SRC_ADDR":    parsed["src_addr"],
        "DST_ADDR":    parsed["dst_addr"],
        "PAYLOAD_LEN": len(parsed["payload"]).to_bytes(2, byteorder="big"),
        "PAYLOAD":     parsed["payload"],
        "CRC32":       parsed["received_crc"],
        "EOF":         parsed["eof"],
    }

    print("=" * 72)
    print("FRAME SECTIONS")
    print("=" * 72)
    for name, value in sections.items():
        print(f"{name:<12} | HEX: {bytes_to_hex(value):<40} | BITS: {bytes_to_bitstring(value)}")
    print("=" * 72)

def plot_frame_bits(frame: bytes, max_bits: int = 64) -> None:
    bits = frame_to_bits(frame)[:max_bits]

    x = []
    y = []

    for i, bit in enumerate(bits):
        x.extend([i, i + 1])
        y.extend([bit, bit])

    plt.figure(figsize=(12, 3))
    plt.plot(x, y)
    plt.ylim(-0.2, 1.2)
    plt.xlim(0, len(bits))
    plt.xlabel("Bit index")
    plt.ylabel("Bit value")
    plt.title("First bits of the frame")
    plt.grid(True)
    plt.show()


def bits_to_nrz(bits: list[int]) -> list[int]:
    return [1 if bit == 1 else -1 for bit in bits]



def print_hamming_coded_bits(frame: bytes) -> list:
    bits = frame_to_bits(frame)
    coded_bits = hamming_kodiraj_bistream(bits)

    print("=" * 72)
    print("HAMMING(7,4) KODIRANI BIT STREAM")
    print("=" * 72)

    # blok po blok prikaz
    print(f"{'Blok':<6} | {'Orig (4b)':<10} | {'Kodiran (7b)':<14} | Paritetni biti")
    print("-" * 72)
    for i in range(0, len(coded_bits), 7):
        blok = coded_bits[i:i+7]
        orig = bits[i//7*4 : i//7*4+4]
        blok_str = ''.join(map(str, blok))
        orig_str = ''.join(map(str, orig))
        p1, p2, _, p4, _, _, _ = blok
        print(f"{i//7+1:<6} | {orig_str:<10} | {blok_str:<14} | p1={p1} p2={p2} p4={p4}")

    # statistika
    print(f"Original : {len(bits)} bitov")
    print(f"Kodirano : {len(coded_bits)} bitov")
    print(f"Blokov   : {len(coded_bits)//7}")
    print(f"Overhead : {len(coded_bits) - len(bits)} bitov ({(len(coded_bits)/len(bits)-1)*100:.1f}%)")
    print("=" * 72)

    return coded_bits

def print_bpsk(frame: bytes, snr_db: float = 10.0) -> tuple:
    raw_bits     = frame_to_bits(frame)
    hamming_bits = hamming_kodiraj_bistream(raw_bits)
    symbols      = bpsk_modulate(hamming_bits)
    noisy        = awgn_noise(symbols, snr_db)
    demod        = [0 if s >= 0 else 1 for s in noisy]

    
    print("BPSK MODULACIJA")
    print("=" * 72)
    print(f"{'Blok':<6} | {'Hamming (7b)':<14} | {'Simboli (7)':<36} | {'Noisy (7)'}")
    print("-" * 72)

    num_blocks = len(hamming_bits) // 7
    for i in range(num_blocks):
        blok_bits    = hamming_bits[i*7 : i*7 + 7]
        blok_symbols = symbols     [i*7 : i*7 + 7]
        blok_noisy   = noisy       [i*7 : i*7 + 7]

        bits_str    = ''.join(map(str, blok_bits))
        symbols_str = ' '.join(f"{s:+.0f}" for s in blok_symbols)
        noisy_str   = ' '.join(f"{n:+.2f}" for n in blok_noisy)

        print(f"{i+1:<6} | {bits_str:<14} | {symbols_str:<36} | {noisy_str}")

    print("=" * 72)
    napake = sum(1 for a, b in zip(hamming_bits, demod) if a != b)
    print(f"Simbolov     : {len(symbols)}")
    print(f"SNR          : {snr_db} dB")
    print(f"Bitnih napak : {napake} / {len(hamming_bits)} ({napake/len(hamming_bits)*100:.2f}%)")
    print("=" * 72)

    return noisy


def print_costas(noisy_symbols):

    synced = costas_loop(noisy_symbols)
    print("=" * 72)
    print("COSTASOV SPREJEMNIK — SLEDENJE FAZI")
    print("=" * 72)
    print(f"{'Simbol':<8} | {'Noisy':<12} | {'Synced':<12} | {'Bit pred':<10} | {'Bit po'}")
    print("-" * 72)

    for i in range(min(20, len(noisy_symbols))):
        bit_before = 0 if noisy_symbols[i]  >= 0 else 1
        bit_after  = 0 if synced[i] >= 0 else 1
        napaka     = " ← POPRAVLJEN" if bit_before != bit_after else ""

        print(f"{i+1:<8} | "
              f"{noisy_symbols[i]:+.4f}{'':>5} | "
              f"{synced[i]:+.4f}{'':>5} | "
              f"{bit_before}{'':>9} | "
              f"{bit_after}{napaka}")

    print("=" * 72)

    # statistika
    bits_before = [0 if s >= 0 else 1 for s in noisy_symbols]
    bits_after  = [0 if s >= 0 else 1 for s in synced]

    return synced

def print_demodulated_bpsk(synced_symbols: list) -> list:
    demodulated = bpsk_demodulate(synced_symbols)

    print("\n")
    print("=" * 72)
    print("BPSK DEMODULACIJA")
    print("=" * 72)
    print(f"{'Blok':<6} | {'Synced (7)':<42} | {'Demod (7b)'}")
    print("-" * 72)

    num_blocks = len(synced_symbols) // 7
    for i in range(num_blocks):
        blok_synced = synced_symbols[i*7 : i*7 + 7]
        blok_demod  = demodulated   [i*7 : i*7 + 7]

        synced_str = ' '.join(f"{s:+.2f}" for s in blok_synced)
        demod_str  = ''.join(map(str, blok_demod))

        print(f"{i+1:<6} | {synced_str:<42} | {demod_str}")

    print("=" * 72)
    print(f"Bitov skupaj : {len(demodulated)}")
    print("=" * 72)

    return demodulated


def print_decoded_hamming(demod_bits: list) -> list:
    dekodirano, napake = hamming_dekodiraj(demod_bits)

    print("\n")
    print("=" * 72)
    print("HAMMING DEKODIRANJE IN KOREKCIJA NAPAK")
    print("=" * 72)
    print(f"{'Blok':<6} | {'Dekodirani (4b)':<20} | {'Napaka (pos)'}")
    print("-" * 72)

    num_blocks = len(dekodirano) // 4
    for i in range(num_blocks):
        blok_decoded = dekodirano[i*4 : i*4 + 4]
        error_pos    = napake[i]
        decoded_str  = ''.join(map(str, blok_decoded))
        error_str    = f"pos {error_pos}" if error_pos != 0 else "Brez napake"

        print(f"{i+1:<6} | {decoded_str:<20} | {error_str}")

    print("=" * 72)
    popravljeni = sum(1 for n in napake if n != 0)
    print(f"Blokov skupaj  : {num_blocks}")
    print(f"Popravljenih   : {popravljeni}")
    print(f"Brez napake    : {num_blocks - popravljeni}")
    print("=" * 72)

    return dekodirano


def print_received_frame(decoded_bits: list) -> bytes:
    # pretvori bite v bajte
    received_frame = bits_to_bytes(decoded_bits)

    print("\n")
    print("=" * 72)
    print("SPREJETI OKVIR — REKONSTRUKCIJA")
    print("=" * 72)

    # izpiši hex in bite
    print(f"FULL FRAME (HEX):")
    print(bytes_to_hex(received_frame))
    print(f"\nFULL FRAME (BITS):")
    print(bytes_to_bitstring(received_frame))

    # izpiši dele okvirja
    print_frame_sections(received_frame)

    # izpiši payload kot string
    parsed = parse_frame(received_frame)
    print("=" * 72)
    print("SPREJETO SPOROČILO")
    print("=" * 72)
    print(f"Payload (HEX)    : {bytes_to_hex(parsed['payload'])}")
    print(f"Payload (bits)   : {bytes_to_bitstring(parsed['payload'])}")
    print(f"Payload (string) : {parsed['payload_text']}")
    print(f"CRC OK           : {parsed['crc_ok']}")
    print("=" * 72)

    return received_frame