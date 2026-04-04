import matplotlib.pyplot as plt
from typing import Dict

from protocol import frame_to_bits, parse_frame, hamming_kodiraj_bistream


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
def plot_nrz(frame: bytes, max_bits: int = 64) -> None:
    bits = frame_to_bits(frame)[:max_bits]
    nrz_levels = bits_to_nrz(bits)

    x = []
    y = []

    for i, level in enumerate(nrz_levels):
        x.extend([i, i + 1])
        y.extend([level, level])

    plt.figure(figsize=(12, 4))
    plt.plot(x, y)
    plt.ylim(-1.5, 1.5)
    plt.xlim(0, len(nrz_levels))
    plt.xlabel("Bit index")
    plt.ylabel("Amplitude")
    plt.title("Polar NRZ signal")
    plt.grid(True)
    plt.show()