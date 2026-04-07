from transmitter import build_frame, build_payload
from visualisation.gui import run_gui
from visualisation.display import (
    bytes_to_hex,
    bytes_to_bitstring,
    print_frame_sections,
    print_original_message,
    print_hamming_coded_bits,
    print_bpsk,
    print_costas,
    print_demodulated_bpsk,
    print_decoded_hamming,
    print_received_frame,
)


def run_terminal_demo():
    message = build_payload("Niko", "Korosec", "12345", "Slovenija")
    snr = 5  # ocitno se vidi, da pravilno popravi napako

    print_original_message(message)

    # Oddajna stran
    frame = build_frame(message)

    print("\nFULL FRAME (HEX):")
    print(bytes_to_hex(frame))

    print("\nFULL FRAME (BITS):")
    print(bytes_to_bitstring(frame))
    print_frame_sections(frame)

    print_hamming_coded_bits(frame)
    modulated = print_bpsk(frame, snr)

    print("KONEC ODDAJNE STRANI")
    print("=" * 72)

    # Sprejemna stran
    print("\nZACETEK SPREJEMNE STRANI")

    synced = print_costas(modulated)
    demodulated = print_demodulated_bpsk(synced)
    decoded = print_decoded_hamming(demodulated)
    print_received_frame(decoded)


def main():
    mode = input("Izberi nacin zagona [1=terminal, 2=GUI]: ").strip()

    if mode == "2":
        run_gui()
    else:
        run_terminal_demo()


if __name__ == "__main__":
    main()