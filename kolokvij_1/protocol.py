import zlib
from typing import Dict, List


PREAMBLE = bytes([0xAA] * 4)
SOF = bytes([0x7E])
FRAME_TYPE = bytes([0x01])
SRC_ADDR = bytes([0x11])
DST_ADDR = bytes([0x22])
EOF = bytes([0x7F])



def text_to_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def int_to_bytes(value: int, length: int) -> bytes:
    return value.to_bytes(length, byteorder="big")


def bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, byteorder="big")


def build_payload(ime: str, priimek: str, vpisna: str, drzava: str) -> str:
    return f"{ime}|{priimek}|{vpisna}|{drzava}"


def calculate_crc32(data: bytes) -> bytes:
    crc_value = zlib.crc32(data) & 0xFFFFFFFF
    return int_to_bytes(crc_value, 4)


def frame_to_bits(frame: bytes) -> List[int]:
    bits = []
    for byte in frame:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def bits_to_bytes(bits: List[int]) -> bytes:
    if len(bits) % 8 != 0:
        raise ValueError("Bit list length must be a multiple of 8.")

    output = bytearray()

    for i in range(0, len(bits), 8):
        byte = 0
        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit
        output.append(byte)

    return bytes(output)


def nrz_encode(bits: List[int]) -> List[float]:
    return [1.0 if bit == 1 else -1.0 for bit in bits]



def hamming_encode_nibble(data_bits):
    
   # Kodiraj 4 podatkovne bite v Hamming(7,4) 
   # d = [d1, d2, d3, d4] (indeksi 0-3)

   # Postavitev v bloku 
   #      pos: 1   2   3   4   5   6   7
   #           p1  p2  d1  p4  d2  d3  d4

    d1, d2, d3, d4 = data_bits

    # ^ - BINARNI XOR OPERATOR

    p1 = d1 ^ d2 ^ d4        # pokriva pos 1,3,5,7
    p2 = d1 ^ d3 ^ d4        # pokriva pos 2,3,6,7
    p4 = d2 ^ d3 ^ d4        # pokriva pos 4,5,6,7  


    return [p1, p2, d1, p4, d2, d3, d4] # Return list


# Apliciraj hamming_encode_nibble() na bit streamu

def hamming_kodiraj(biti):

    while len(biti) % 4 != 0:
        biti = biti + [0]
        
    kodirani = []

    for i in range(0, len(biti), 4):
        nibble = biti[i:i+4]
        kodirani.extend(hamming_encode_nibble(nibble))
    return kodirani




def build_frame(payload_text: str) -> bytes:
    payload = text_to_bytes(payload_text)
    payload_len = int_to_bytes(len(payload), 2)

    protected_part = FRAME_TYPE + SRC_ADDR + DST_ADDR + payload_len + payload
    crc = calculate_crc32(protected_part)

    frame = PREAMBLE + SOF + protected_part + crc + EOF
    return frame


def parse_frame(frame: bytes) -> Dict:
    preamble_len = len(PREAMBLE)
    sof_len = len(SOF)
    frame_type_len = len(FRAME_TYPE)
    src_len = len(SRC_ADDR)
    dst_len = len(DST_ADDR)
    payload_len_field_len = 2
    crc_len = 4
    eof_len = len(EOF)

    preamble = frame[0:preamble_len]
    sof = frame[preamble_len:preamble_len + sof_len]

    header_start = preamble_len + sof_len
    frame_type_start = header_start
    src_start = frame_type_start + frame_type_len
    dst_start = src_start + src_len
    payload_len_start = dst_start + dst_len
    payload_start = payload_len_start + payload_len_field_len

    frame_type = frame[frame_type_start:src_start]
    src_addr = frame[src_start:dst_start]
    dst_addr = frame[dst_start:payload_len_start]

    payload_len = bytes_to_int(frame[payload_len_start:payload_start])
    payload_end = payload_start + payload_len

    payload = frame[payload_start:payload_end]
    received_crc = frame[payload_end:payload_end + crc_len]
    eof = frame[payload_end + crc_len:payload_end + crc_len + eof_len]

    protected_part = frame[header_start:payload_end]
    calculated_crc = calculate_crc32(protected_part)

    return {
        "preamble": preamble,
        "sof": sof,
        "frame_type": frame_type,
        "src_addr": src_addr,
        "dst_addr": dst_addr,
        "payload_len": payload_len,
        "payload": payload,
        "payload_text": payload.decode("utf-8"),
        "received_crc": received_crc,
        "calculated_crc": calculated_crc,
        "crc_ok": received_crc == calculated_crc,
        "eof": eof,
    }

