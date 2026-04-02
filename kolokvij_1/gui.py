import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

from SDV_teorija.kolokvij_1.protocol import build_frame, parse_frame, frame_to_bits


def bytes_to_hex(data: bytes) -> str:
    return " ".join(f"{byte:02X}" for byte in data)


def bits_to_nrz(bits: list[int]) -> list[int]:
    return [1 if bit == 1 else -1 for bit in bits]


class ProtocolGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Physical Layer Protocol Demo")
        self.root.geometry("1000x700")

        self.current_frame = None
        self.current_parsed = None

        self._build_layout()

    def _build_layout(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        input_box = ttk.LabelFrame(main, text="Input", padding=10)
        input_box.pack(fill="x", pady=5)

        ttk.Label(input_box, text="Message:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.message_var = tk.StringVar(value="Niko Korošec M10141263 Slovenia")
        ttk.Entry(input_box, textvariable=self.message_var, width=70).grid(
            row=0, column=1, padx=5, pady=5, sticky="ew"
        )

        input_box.columnconfigure(1, weight=1)

        button_box = ttk.Frame(main)
        button_box.pack(fill="x", pady=8)

        ttk.Button(button_box, text="Encode", command=self.encode_frame).pack(side="left", padx=5)
        ttk.Button(button_box, text="Decode", command=self.decode_frame).pack(side="left", padx=5)
        ttk.Button(button_box, text="Plot NRZ", command=self.plot_nrz).pack(side="left", padx=5)
        ttk.Button(button_box, text="Clear", command=self.clear_all).pack(side="left", padx=5)

        output_box = ttk.LabelFrame(main, text="Protocol Output", padding=10)
        output_box.pack(fill="both", expand=True, pady=5)

        ttk.Label(output_box, text="Frame (HEX):").pack(anchor="w")
        self.frame_text = tk.Text(output_box, height=6, wrap="word")
        self.frame_text.pack(fill="x", pady=5)

        info_grid = ttk.Frame(output_box)
        info_grid.pack(fill="x", pady=8)

        self.crc_var = tk.StringVar(value="-")
        self.crc_status_var = tk.StringVar(value="-")
        self.frame_type_var = tk.StringVar(value="-")
        self.src_var = tk.StringVar(value="-")
        self.dst_var = tk.StringVar(value="-")
        self.length_var = tk.StringVar(value="-")
        self.eof_var = tk.StringVar(value="-")

        ttk.Label(info_grid, text="CRC32:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.crc_var).grid(row=0, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="CRC Status:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.crc_status_var).grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Frame Type:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.frame_type_var).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Source:").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.src_var).grid(row=1, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Destination:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.dst_var).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Payload Length:").grid(row=2, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.length_var).grid(row=2, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="EOF:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.eof_var).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(output_box, text="Decoded Message:").pack(anchor="w")
        self.decoded_text = tk.Text(output_box, height=5, wrap="word")
        self.decoded_text.pack(fill="x", pady=5)

    def encode_frame(self) -> None:
        message = self.message_var.get().strip()

        if not message:
            messagebox.showwarning("Warning", "Please enter a message.")
            return

        try:
            self.current_frame = build_frame(message)
            self.current_parsed = None

            self.frame_text.delete("1.0", tk.END)
            self.frame_text.insert(tk.END, bytes_to_hex(self.current_frame))

            self.decoded_text.delete("1.0", tk.END)

            self.crc_var.set("-")
            self.crc_status_var.set("-")
            self.frame_type_var.set("-")
            self.src_var.set("-")
            self.dst_var.set("-")
            self.length_var.set("-")
            self.eof_var.set("-")

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def decode_frame(self) -> None:
        if self.current_frame is None:
            messagebox.showinfo("Info", "Encode a frame first.")
            return

        try:
            parsed = parse_frame(self.current_frame)
            self.current_parsed = parsed

            self.crc_var.set(f"0x{parsed['received_crc']:08X}")
            self.crc_status_var.set("OK" if parsed["crc_ok"] else "FAIL")
            self.frame_type_var.set(f"0x{parsed['frame_type']:02X}")
            self.src_var.set(f"0x{parsed['src_addr']:02X}")
            self.dst_var.set(f"0x{parsed['dst_addr']:02X}")
            self.length_var.set(str(parsed["payload_len"]))
            self.eof_var.set(f"0x{parsed['eof']:02X}")

            self.decoded_text.delete("1.0", tk.END)
            self.decoded_text.insert(tk.END, parsed["payload_text"])

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_nrz(self) -> None:
        if self.current_frame is None:
            messagebox.showinfo("Info", "Encode a frame first.")
            return

        bits = frame_to_bits(self.current_frame)
        bits = bits[:80]
        levels = bits_to_nrz(bits)

        x = []
        y = []

        for i, level in enumerate(levels):
            x.extend([i, i + 1])
            y.extend([level, level])

        plt.figure(figsize=(12, 4))
        plt.plot(x, y)
        plt.ylim(-1.5, 1.5)
        plt.xlim(0, len(levels))
        plt.xlabel("Bit index")
        plt.ylabel("Amplitude")
        plt.title("Polar NRZ signal")
        plt.grid(True)
        plt.show()

    def clear_all(self) -> None:
        self.current_frame = None
        self.current_parsed = None

        self.frame_text.delete("1.0", tk.END)
        self.decoded_text.delete("1.0", tk.END)

        self.crc_var.set("-")
        self.crc_status_var.set("-")
        self.frame_type_var.set("-")
        self.src_var.set("-")
        self.dst_var.set("-")
        self.length_var.set("-")
        self.eof_var.set("-")


def main() -> None:
    root = tk.Tk()
    app = ProtocolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()