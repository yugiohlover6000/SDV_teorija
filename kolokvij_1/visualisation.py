import matplotlib.pyplot as plt
from typing import Dict

from protocol import frame_to_bits, parse_frame


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