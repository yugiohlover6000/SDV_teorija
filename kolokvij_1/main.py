from transmitter import build_frame, build_payload
from display import (
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

def main():
    message = build_payload("Niko", "Korosec", "12345", "Slovenija")
    snr = 10

    print_original_message(message)

    # Oddajna stran
    frame = build_frame(message)
    
    # Print okvirja v različnih formatih
    print("\nFULL FRAME (HEX):")
    print(bytes_to_hex(frame))

    print("\nFULL FRAME (BITS):")
    print(bytes_to_bitstring(frame))
    print_frame_sections(frame)

    # Prikažemo Hammingovo kodiranje in BPSK modulacijo
    print_hamming_coded_bits(frame)
    modulated = print_bpsk(frame,snr)

    print("KONEC ODDAJNE STRANI")
    print("=" * 72)

    # Sprejemna stran
    print("\nZACETEK SPREJEMNE STRANI")

    synced = print_costas(modulated)
    demodulated = print_demodulated_bpsk(synced)
    decoded = print_decoded_hamming(demodulated)
    print_received_frame(decoded)


if __name__ == "__main__":
    main()