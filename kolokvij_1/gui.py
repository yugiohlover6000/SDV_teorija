import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt

from protocol import build_frame, parse_frame, frame_to_bits, nrz_encode


def bytes_to_hex(data):
    return " ".join(f"{byte:02X}" for byte in data)


class ProtocolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SDV Protocol GUI")
        self.root.geometry("1000x720")

        self.current_frame = None
        self.current_parsed = None

        self._build_layout()

    def _build_layout(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        input_box = ttk.LabelFrame(main, text="Input message", padding=10)
        input_box.pack(fill="x", pady=5)

        ttk.Label(input_box, text="Message:").grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.message_var = tk.StringVar(value="Niko Korošec M10141263 Slovenia")
        self.message_entry = ttk.Entry(input_box, textvariable=self.message_var, width=70)
        self.message_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        input_box.columnconfigure(1, weight=1)

        button_box = ttk.Frame(main)
        button_box.pack(fill="x", pady=8)

        ttk.Button(button_box, text="1. Build frame", command=self.build_frame_action).pack(side="left", padx=5)
        ttk.Button(button_box, text="2. Parse frame", command=self.parse_frame_action).pack(side="left", padx=5)
        ttk.Button(button_box, text="3. Plot NRZ", command=self.plot_nrz).pack(side="left", padx=5)
        ttk.Button(button_box, text="Clear", command=self.clear_all).pack(side="left", padx=5)

        output_box = ttk.LabelFrame(main, text="Protocol output", padding=10)
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

        ttk.Label(info_grid, text="CRC status:").grid(row=0, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.crc_status_var).grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Frame type:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.frame_type_var).grid(row=1, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Source:").grid(row=1, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.src_var).grid(row=1, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Destination:").grid(row=2, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.dst_var).grid(row=2, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="Payload length:").grid(row=2, column=2, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.length_var).grid(row=2, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(info_grid, text="EOF:").grid(row=3, column=0, sticky="w", padx=5, pady=3)
        ttk.Label(info_grid, textvariable=self.eof_var).grid(row=3, column=1, sticky="w", padx=5, pady=3)

        ttk.Label(output_box, text="Decoded message:").pack(anchor="w")
        self.decoded_text = tk.Text(output_box, height=5, wrap="word")
        self.decoded_text.pack(fill="x", pady=5)

    def build_frame_action(self):
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

    def parse_frame_action(self):
        if self.current_frame is None:
            messagebox.showinfo("Info", "Build the frame first.")
            return

        try:
            parsed = parse_frame(self.current_frame)
            self.current_parsed = parsed

            self.crc_var.set(bytes_to_hex(parsed["received_crc"]))
            self.crc_status_var.set("OK" if parsed["crc_ok"] else "FAIL")
            self.frame_type_var.set(bytes_to_hex(parsed["frame_type"]))
            self.src_var.set(bytes_to_hex(parsed["src_addr"]))
            self.dst_var.set(bytes_to_hex(parsed["dst_addr"]))
            self.length_var.set(str(parsed["payload_len"]))
            self.eof_var.set(bytes_to_hex(parsed["eof"]))

            self.decoded_text.delete("1.0", tk.END)
            self.decoded_text.insert(tk.END, parsed["payload_text"])

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def plot_nrz(self):
        if self.current_frame is None:
            messagebox.showinfo("Info", "Build the frame first.")
            return

        bits = frame_to_bits(self.current_frame)
        bits = bits[:80]
        levels = nrz_encode(bits)

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
        plt.title("NRZ signal")
        plt.grid(True)
        plt.show()

    def clear_all(self):
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


def main():
    root = tk.Tk()
    app = ProtocolGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()