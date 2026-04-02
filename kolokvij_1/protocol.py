import zlib
from typing import Dict


def text_to_bytes(text: str) -> bytes:
    return text.encode("utf-8")


def int_to_bytes(value: int, length: int) -> bytes:
    return value.to_bytes(length, byteorder="big")


def frame_to_bits(frame: bytes) -> list[int]:
    bits = []
    for byte in frame:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits


def build_frame(payload_text: str) -> bytes:
    preamble = bytes([0xAA] * 4)
    sof = bytes([0x7E])
    frame_type = bytes([0x01])
    src_addr = bytes([0x11])
    dst_addr = bytes([0x22])

    payload = text_to_bytes(payload_text)
    payload_len = int_to_bytes(len(payload), 2)

    protected_part = frame_type + src_addr + dst_addr + payload_len + payload
    crc = int_to_bytes(zlib.crc32(protected_part) & 0xFFFFFFFF, 4)
    eof = bytes([0x7F])

    frame = preamble + sof + protected_part + crc + eof
    return frame


def parse_frame(frame: bytes) -> Dict:
    preamble = frame[0:4]
    sof = frame[4]

    frame_type = frame[5]
    src_addr = frame[6]
    dst_addr = frame[7]
    payload_len = int.from_bytes(frame[8:10], byteorder="big")

    payload_start = 10
    payload_end = payload_start + payload_len

    payload = frame[payload_start:payload_end]
    received_crc = int.from_bytes(frame[payload_end:payload_end + 4], byteorder="big")
    eof = frame[payload_end + 4]

    protected_part = frame[5:payload_end]
    calculated_crc = zlib.crc32(protected_part) & 0xFFFFFFFF

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