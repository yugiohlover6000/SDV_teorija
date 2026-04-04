from protocol import build_frame, parse_frame
from visualisation import (
    bytes_to_hex,
    bytes_to_bitstring,
    print_frame_sections,
    print_original_message
    
)


def main() -> None:
    message = "Niko Korošec M10141263 Slovenia"

    print_original_message(message)

    
    # Build the frame from the original message

    frame = build_frame(message)
    parsed = parse_frame(frame)
    
    print("\nFULL FRAME (HEX):")
    print(bytes_to_hex(frame))

    print("\nFULL FRAME (BITS):")
    print(bytes_to_bitstring(frame))

    
    print_frame_sections(frame)

    print("/n")
    print(bytes_to_bitstring(frame))
    
    #print_parsed_frame(parsed)

    #plot_frame_bits(frame, max_bits=80)
    #plot_nrz(frame, max_bits=80)

#from gui import main as gui_main


#def main():
#    gui_main()


if __name__ == "__main__":
    main()