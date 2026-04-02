import matplotlib.pyplot as plt
from typing import Dict

from protocol import frame_to_bits


def bytes_to_hex(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def bytes_to_bitstring(data: bytes) -> str:
    return " ".join(f"{byte:08b}" for byte in data)


def print_frame_hex(frame: bytes) -> None:
    print(bytes_to_hex(frame))


def print_frame_sections(frame: bytes) -> None:
    payload_len = int.from_bytes(frame[8:10], byteorder="big")
    payload_start = 10
    payload_end = payload_start + payload_len

    sections = {
        "PREAMBLE": frame[0:4],
        "SOF": frame[4:5],
        "FRAME_TYPE": frame[5:6],
        "SRC_ADDR": frame[6:7],
        "DST_ADDR": frame[7:8],
        "PAYLOAD_LEN": frame[8:10],
        "PAYLOAD": frame[payload_start:payload_end],
        "CRC32": frame[payload_end:payload_end + 4],
        "EOF": frame[payload_end + 4:payload_end + 5],
    }

    print("=" * 72)
    print("FRAME SECTIONS")
    print("=" * 72)

    for name, value in sections.items():
        print(f"{name:<12} | HEX: {bytes_to_hex(value):<40} | BITS: {bytes_to_bitstring(value)}")

    print("=" * 72)


def print_parsed_frame(parsed: Dict) -> None:
    print("=" * 72)
    print("PARSED FRAME")
    print("=" * 72)
    print(f"{'Preamble':<20}: {bytes_to_hex(parsed['preamble'])}")
    print(f"{'SOF':<20}: 0x{parsed['sof']:02X}")
    print(f"{'Frame type':<20}: 0x{parsed['frame_type']:02X}")
    print(f"{'Source address':<20}: 0x{parsed['src_addr']:02X}")
    print(f"{'Destination address':<20}: 0x{parsed['dst_addr']:02X}")
    print(f"{'Payload length':<20}: {parsed['payload_len']}")
    print(f"{'Payload (hex)':<20}: {bytes_to_hex(parsed['payload'])}")
    print(f"{'Payload (text)':<20}: {parsed['payload_text']}")
    print(f"{'Received CRC32':<20}: 0x{parsed['received_crc']:08X}")
    print(f"{'Calculated CRC32':<20}: 0x{parsed['calculated_crc']:08X}")
    print(f"{'CRC OK':<20}: {parsed['crc_ok']}")
    print(f"{'EOF':<20}: 0x{parsed['eof']:02X}")
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