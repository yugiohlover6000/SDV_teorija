from protocol import build_frame, parse_frame
from visualisation import (
    bytes_to_hex,
    bytes_to_bitstring,
    print_frame_sections,
    print_original_message,
    print_hamming_coded_bits,
    print_bpsk,
    print_costas,
    print_demodulated_bpsk,
    print_decoded_hamming,
    print_received_frame
    

    
)


def main():


    # ═══ ODDAJNA STRAN - START ═══════════════════════════════

    #    Ustvarimo sporočilo, ga zapakiramo v okvir in prikažemo
    #    Dodamo še hammingov kodirnik in BPSK modulacijo z dodanim šumom


    message = "Niko Korošec M10141263 Slovenia"
    snr = 10 # SNR in dB for noise simulation

    print_original_message(message)

    # Build the frame from the original message
    frame = build_frame(message)
    parsed = parse_frame(frame)
    
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

# ═══ ODDAJNA STRAN - END═══════════════════════════════
    


# ═══ KANAL - START ═══════════════════════════════════════
#     Potuje po kanalu...
# ═══ KANAL - END ═══════════════════════════════════════


# ═══ SPREJEMNA STRAN - START   ═════════════════════════════
#    Sprejme okvir, ga dekodira in prikaže vsebino
#    Impelemtiramo Costasovo zanko za sinhronizacijo in korekcijo napak

    print("\nZACETEK SPREJEMNE STRANI")


    # Prikazemo Costasov sprejemnik, ki sledi fazi in popravlja napake v BPSK 
    synced = print_costas(modulated)

    # BPSK demodulacija 
    demodulated =print_demodulated_bpsk(synced)


    # Hamming dekodiranje in prikaz napak
    decoded = print_decoded_hamming(demodulated) 

    # Sestavi okvir
    received_frame = print_received_frame(decoded)

# ═══ SPREJEMNA STRAN - END   ═════════════════════════════






#from gui import main as gui_main


#def main():
#    gui_main()


if __name__ == "__main__":
    main()