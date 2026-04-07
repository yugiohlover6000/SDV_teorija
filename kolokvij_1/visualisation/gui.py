import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import math

try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
except Exception as exc:  # pragma: no cover
    raise RuntimeError("Matplotlib with TkAgg backend is required for this GUI.") from exc

from transmitter import (
    build_payload,
    build_frame,
    parse_frame,
    frame_to_bits,
    hamming_kodiraj_bistream,
    bpsk_modulate,
    awgn_noise,
)
from receiver import (
    costas_loop,
    bpsk_demodulate,
    hamming_dekodiraj,
)
from visualisation.display import bytes_to_hex, bytes_to_bitstring


class CommunicationGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("SDV – Komunikacijska shema (BPSK / Hamming / CRC)")
        self.root.geometry("1400x900")

        self._build_state()
        self._build_layout()

    def _build_state(self) -> None:
        self.ime_var = tk.StringVar(value="Niko")
        self.priimek_var = tk.StringVar(value="Korosec")
        self.vpisna_var = tk.StringVar(value="12345")
        self.drzava_var = tk.StringVar(value="Slovenija")
        self.snr_var = tk.DoubleVar(value=5.0)
        self.max_points_var = tk.IntVar(value=80)

        self.payload_text = ""
        self.frame = b""
        self.parsed = {}
        self.raw_bits = []
        self.hamming_bits = []
        self.symbols = []
        self.noisy_symbols = []
        self.synced_symbols = []
        self.demodulated_bits = []
        self.decoded_bits = []
        self.detected_errors = []
        self.received_frame = b""
        self.received_parsed = {}

    def _build_layout(self) -> None:
        top = ttk.Frame(self.root, padding=10)
        top.pack(fill="x")

        self._build_controls(top)

        body = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(body, padding=5)
        right = ttk.Frame(body, padding=5)
        body.add(left, weight=2)
        body.add(right, weight=3)

        self._build_tables(left)
        self._build_plots(right)

    def _build_controls(self, parent: ttk.Frame) -> None:
        form = ttk.LabelFrame(parent, text="Vhodni podatki", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Ime").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.ime_var, width=18).grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Priimek").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.priimek_var, width=18).grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(form, text="Vpisna").grid(row=0, column=4, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.vpisna_var, width=18).grid(row=0, column=5, padx=4, pady=4)

        ttk.Label(form, text="Država").grid(row=0, column=6, sticky="w", padx=4, pady=4)
        ttk.Entry(form, textvariable=self.drzava_var, width=18).grid(row=0, column=7, padx=4, pady=4)

        ttk.Label(form, text="SNR [dB]").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Spinbox(form, from_=-5, to=30, increment=1, textvariable=self.snr_var, width=10).grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(form, text="Št. točk na grafu").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        ttk.Spinbox(form, from_=20, to=300, increment=10, textvariable=self.max_points_var, width=10).grid(row=1, column=3, padx=4, pady=4)

        ttk.Button(form, text="Zaženi celoten potek", command=self.run_pipeline).grid(row=1, column=6, padx=6, pady=4)
        ttk.Button(form, text="Počisti", command=self.clear_output).grid(row=1, column=7, padx=6, pady=4)

        for i in range(8):
            form.columnconfigure(i, weight=1)

    def _build_tables(self, parent: ttk.Frame) -> None:
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True)

        self.summary_tab = ttk.Frame(notebook)
        self.frame_tab = ttk.Frame(notebook)
        self.rx_tab = ttk.Frame(notebook)
        notebook.add(self.summary_tab, text="Povzetek")
        notebook.add(self.frame_tab, text="Okvir")
        notebook.add(self.rx_tab, text="Sprejem")

        self.summary_box = ScrolledText(self.summary_tab, wrap="word", font=("Courier New", 10))
        self.summary_box.pack(fill="both", expand=True)

        self.frame_box = ScrolledText(self.frame_tab, wrap="word", font=("Courier New", 10))
        self.frame_box.pack(fill="both", expand=True)

        self.rx_box = ScrolledText(self.rx_tab, wrap="word", font=("Courier New", 10))
        self.rx_box.pack(fill="both", expand=True)

    def _build_plots(self, parent: ttk.Frame) -> None:
        self.figure = Figure(figsize=(8, 8), dpi=100)
        self.ax1 = self.figure.add_subplot(311)
        self.ax2 = self.figure.add_subplot(312)
        self.ax3 = self.figure.add_subplot(313)
        self.figure.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._reset_axes()
        self.canvas.draw()

    def _reset_axes(self) -> None:
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax1.set_title("BPSK simboli")
        self.ax2.set_title("Noisy vs synced")
        self.ax3.set_title("Biti: original / demod / decoded")
        self.ax1.set_xlabel("Indeks")
        self.ax2.set_xlabel("Indeks")
        self.ax3.set_xlabel("Indeks")
        self.ax1.grid(True)
        self.ax2.grid(True)
        self.ax3.grid(True)

    def clear_output(self) -> None:
        for box in (self.summary_box, self.frame_box, self.rx_box):
            box.delete("1.0", tk.END)
        self._reset_axes()
        self.canvas.draw()

    def run_pipeline(self) -> None:
        try:
            max_points = max(20, int(self.max_points_var.get()))
            snr = float(self.snr_var.get())

            self.payload_text = build_payload(
                self.ime_var.get().strip(),
                self.priimek_var.get().strip(),
                self.vpisna_var.get().strip(),
                self.drzava_var.get().strip(),
            )

            self.frame = build_frame(self.payload_text)
            self.parsed = parse_frame(self.frame)
            self.raw_bits = frame_to_bits(self.frame)
            self.hamming_bits = hamming_kodiraj_bistream(self.raw_bits)
            self.symbols = bpsk_modulate(self.hamming_bits)
            self.noisy_symbols = awgn_noise(self.symbols, snr)
            self.synced_symbols = costas_loop(self.noisy_symbols)
            self.demodulated_bits = bpsk_demodulate(self.synced_symbols)
            self.decoded_bits, self.detected_errors = hamming_dekodiraj(self.demodulated_bits)

            from transmitter import bits_to_bytes  # local reuse without circular redesign
            self.received_frame = bits_to_bytes(self.decoded_bits)
            self.received_parsed = parse_frame(self.received_frame)

            self._fill_summary(snr)
            self._fill_frame_view()
            self._fill_rx_view()
            self._draw_plots(max_points)
        except Exception as exc:
            messagebox.showerror("Napaka", f"Pri izvajanju je prišlo do napake:\n\n{exc}")

    def _fill_summary(self, snr: float) -> None:
        self.summary_box.delete("1.0", tk.END)

        bit_errors_after_demod = sum(
            1 for a, b in zip(self.hamming_bits, self.demodulated_bits) if a != b
        )
        corrected_blocks = sum(1 for e in self.detected_errors if e != 0)

        text = []
        text.append("=== POVZETEK CELOTNEGA POTEKA ===\n")
        text.append(f"Vhodno sporočilo      : {self.payload_text}\n")
        text.append(f"SNR [dB]             : {snr}\n")
        text.append(f"Dolžina payload-a    : {len(self.parsed['payload'])} B\n")
        text.append(f"Dolžina okvirja      : {len(self.frame)} B\n")
        text.append(f"Število bitov frame  : {len(self.raw_bits)}\n")
        text.append(f"Število Hamming bitov: {len(self.hamming_bits)}\n")
        text.append(f"Bitne napake po demod: {bit_errors_after_demod}\n")
        text.append(f"Popravljeni bloki    : {corrected_blocks}\n")
        text.append(f"CRC na sprejemu OK   : {self.received_parsed['crc_ok']}\n")
        text.append(f"Sprejeto sporočilo   : {self.received_parsed['payload_text']}\n\n")

        text.append("Pipeline:\n")
        text.append("message -> frame -> bits -> Hamming -> BPSK -> AWGN -> Costas -> demod -> decode -> frame\n")

        self.summary_box.insert(tk.END, "".join(text))

    def _fill_frame_view(self) -> None:
        self.frame_box.delete("1.0", tk.END)

        sections = {
            "PREAMBLE": self.parsed["preamble"],
            "SOF": self.parsed["sof"],
            "FRAME_TYPE": self.parsed["frame_type"],
            "SRC_ADDR": self.parsed["src_addr"],
            "DST_ADDR": self.parsed["dst_addr"],
            "PAYLOAD_LEN": len(self.parsed["payload"]).to_bytes(2, byteorder="big"),
            "PAYLOAD": self.parsed["payload"],
            "CRC32": self.parsed["received_crc"],
            "EOF": self.parsed["eof"],
        }

        text = []
        text.append("=== ORIGINALNI OKVIR ===\n")
        text.append(f"HEX : {bytes_to_hex(self.frame)}\n")
        text.append(f"BITS: {bytes_to_bitstring(self.frame)}\n\n")
        text.append("=== SECTIONS ===\n")
        for name, value in sections.items():
            text.append(f"{name:<12} | HEX: {bytes_to_hex(value):<40} | BITS: {bytes_to_bitstring(value)}\n")

        text.append("\n=== PRVI HAMMING BLOKI ===\n")
        text.append(f"{'Blok':<6} | {'Orig(4b)':<10} | {'Kodiran(7b)'}\n")
        for i in range(0, min(len(self.hamming_bits), 10 * 7), 7):
            blok = self.hamming_bits[i:i+7]
            orig = self.raw_bits[(i // 7) * 4:(i // 7) * 4 + 4]
            text.append(f"{i//7 + 1:<6} | {''.join(map(str, orig)):<10} | {''.join(map(str, blok))}\n")

        self.frame_box.insert(tk.END, "".join(text))

    def _fill_rx_view(self) -> None:
        self.rx_box.delete("1.0", tk.END)

        text = []
        text.append("=== SPREJEMNA STRAN ===\n")
        text.append(f"Sprejeti okvir (HEX): {bytes_to_hex(self.received_frame)}\n")
        text.append(f"CRC OK             : {self.received_parsed['crc_ok']}\n")
        text.append(f"Payload            : {self.received_parsed['payload_text']}\n\n")

        text.append("=== PRVI DEMODULIRANI BLOKI ===\n")
        text.append(f"{'Blok':<6} | {'Demod(7b)':<12} | {'Dec(4b)':<10} | Napaka\n")
        num_blocks = min(len(self.detected_errors), 10)
        for i in range(num_blocks):
            dem = self.demodulated_bits[i*7:i*7+7]
            dec = self.decoded_bits[i*4:i*4+4]
            err = self.detected_errors[i]
            err_text = f"pos {err}" if err else "brez"
            text.append(f"{i+1:<6} | {''.join(map(str, dem)):<12} | {''.join(map(str, dec)):<10} | {err_text}\n")

        self.rx_box.insert(tk.END, "".join(text))

    def _draw_plots(self, max_points: int) -> None:
        self._reset_axes()

        n = min(max_points, len(self.symbols), len(self.noisy_symbols), len(self.synced_symbols))
        x = list(range(n))

        self.ax1.plot(x, self.symbols[:n], marker="o", linewidth=1)
        self.ax1.set_ylabel("Amplituda")

        self.ax2.plot(x, self.noisy_symbols[:n], marker="o", linewidth=1, label="Noisy")
        self.ax2.plot(x, self.synced_symbols[:n], marker="x", linewidth=1, label="Synced")
        self.ax2.set_ylabel("Amplituda")
        self.ax2.legend()

        m = min(max_points, len(self.raw_bits), len(self.decoded_bits))
        xb = list(range(m))
        self.ax3.step(xb, self.raw_bits[:m], where="post", label="Frame bits")
        self.ax3.step(xb, self.decoded_bits[:m], where="post", label="Decoded bits")
        self.ax3.set_ylabel("Bit")
        self.ax3.legend()

        self.figure.tight_layout(pad=2.0)
        self.canvas.draw()

def run_gui() -> None:
    root = tk.Tk()
    app = CommunicationGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
