import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import random
import struct
import zlib

# ═══════════════════════════════════════════════════════════════
# PROTOKOL — inline kopija da GUI dela samostojno
# ═══════════════════════════════════════════════════════════════
PREAMBLE   = bytes([0xAA] * 3)
SOF        = bytes([0xAB])
FRAME_TYPE = bytes([0x08])
SRC_ADDR   = bytes([0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF])
DST_ADDR   = bytes([0x11, 0x22, 0x33, 0x44, 0x55, 0x66])
EOF        = bytes([0xFF, 0xFE])

def calculate_crc32(data):
    return struct.pack('<I', zlib.crc32(data) & 0xFFFFFFFF)

def build_frame(text):
    payload    = text.encode('utf-8')
    length     = struct.pack('>H', len(payload))
    protected  = FRAME_TYPE + SRC_ADDR + DST_ADDR + length + payload
    crc        = calculate_crc32(protected)
    return PREAMBLE + SOF + protected + crc + EOF

def parse_frame(frame):
    pl  = len(PREAMBLE)
    sl  = len(SOF)
    ftl = len(FRAME_TYPE)
    sal = len(SRC_ADDR)
    dal = len(DST_ADDR)
    p0 = 0; p1 = pl; p2 = p1+sl; p3 = p2+ftl; p4 = p3+sal; p5 = p4+dal; p6 = p5+2
    plen = struct.unpack('>H', frame[p5:p6])[0]
    p7 = p6 + plen
    payload       = frame[p6:p7]
    received_crc  = frame[p7:p7+4]
    eof_          = frame[p7+4:p7+6]
    protected     = frame[p2:p7]
    calc_crc      = calculate_crc32(protected)
    return {
        'preamble': frame[p0:p1], 'sof': frame[p1:p2],
        'frame_type': frame[p2:p3], 'src': frame[p3:p4],
        'dst': frame[p4:p5], 'payload_len': plen,
        'payload': payload, 'payload_text': payload.decode('utf-8', errors='replace'),
        'received_crc': received_crc, 'calculated_crc': calc_crc,
        'crc_ok': received_crc == calc_crc, 'eof': eof_,
    }

def frame_to_bits(frame):
    bits = []
    for byte in frame:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)
    return bits

def bits_to_bytes(bits):
    while len(bits) % 8 != 0:
        bits = bits + [0]
    result = []
    for i in range(0, len(bits), 8):
        byte = 0
        for b in bits[i:i+8]:
            byte = (byte << 1) | b
        result.append(byte)
    return bytes(result)

def hamming_encode_nibble(data_bits):
    d1, d2, d3, d4 = data_bits
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p4 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p4, d2, d3, d4]

def hamming_kodiraj(bits):
    while len(bits) % 4 != 0:
        bits = bits + [0]
    kodirani = []
    for i in range(0, len(bits), 4):
        kodirani.extend(hamming_encode_nibble(bits[i:i+4]))
    return kodirani

def hamming_decode_nibble(coded_bits):
    p1, p2, d1, p4, d2, d3, d4 = coded_bits
    s1 = p1 ^ d1 ^ d2 ^ d4
    s2 = p2 ^ d1 ^ d3 ^ d4
    s4 = p4 ^ d2 ^ d3 ^ d4
    error_pos = s1 * 1 + s2 * 2 + s4 * 4
    if error_pos != 0:
        coded_bits = list(coded_bits)
        coded_bits[error_pos - 1] ^= 1
    _, _, d1, _, d2, d3, d4 = coded_bits
    return [d1, d2, d3, d4], error_pos

def hamming_dekodiraj(bits):
    dekodirani = []; napake = []
    for i in range(0, len(bits), 7):
        blok = bits[i:i+7]
        if len(blok) < 7:
            break
        data, err = hamming_decode_nibble(blok)
        dekodirani.extend(data); napake.append(err)
    return dekodirani, napake

def bpsk_modulate(bits):
    return [1.0 if b == 0 else -1.0 for b in bits]

def bpsk_demodulate(symbols):
    return [0 if s >= 0 else 1 for s in symbols]

def awgn_noise(symbols, snr_db):
    snr_lin   = 10 ** (snr_db / 10)
    noise_std = math.sqrt(1 / (2 * snr_lin))
    return [s + random.gauss(0, noise_std) for s in symbols]

def costas_loop(noisy_symbols, alpha=0.05):
    phase = 0.0; synced = []
    for symbol in noisy_symbols:
        I = symbol * math.cos(phase)
        Q = symbol * math.sin(phase)
        phase += alpha * (I * Q)
        synced.append(I)
    return synced

# ═══════════════════════════════════════════════════════════════
# BARVE IN STIL
# ═══════════════════════════════════════════════════════════════
BG       = "#0f1117"
PANEL    = "#1a1d27"
CARD     = "#21253a"
ACCENT   = "#4f8ef7"
ACCENT2  = "#7c5af7"
GREEN    = "#3dd68c"
RED      = "#f74f6a"
AMBER    = "#f7a84f"
TEXT     = "#e8eaf6"
MUTED    = "#7b82a8"
BORDER   = "#2e3252"
MONO     = "Courier New"

# ═══════════════════════════════════════════════════════════════
# GLAVNO OKNO
# ═══════════════════════════════════════════════════════════════
class ProtocolGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SDV KOLOKVIJ 1 - Vizualizacija fizične plasti")
        self.root.configure(bg=BG)
        self.root.geometry("1280x820")
        self.root.minsize(900, 600)

        self.snr_var  = tk.DoubleVar(value=10.0)
        self.msg_var  = tk.StringVar(value="Niko Korošec M10141263 Slovenia")
        self.frame    = None
        self.results  = {}

        self._build_ui()

    # ─── GRADNJA UI ──────────────────────────────────────────
    def _build_ui(self):
        # ── zgornja vrstica: naslov + kontrole ──
        top = tk.Frame(self.root, bg=BG, pady=14)
        top.pack(fill=tk.X, padx=20)

        tk.Label(top, text="SDV PROTOKOL", font=("Courier New", 18, "bold"),
                 bg=BG, fg=ACCENT).pack(side=tk.LEFT)
        tk.Label(top, text="vizualizacija fizične plasti",
                 font=("Courier New", 10), bg=BG, fg=MUTED).pack(side=tk.LEFT, padx=12)

        # ── vnosna vrstica ──
        inp_frame = tk.Frame(self.root, bg=PANEL, pady=12, padx=16,
                             highlightbackground=BORDER, highlightthickness=1)
        inp_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(inp_frame, text="Sporočilo:", font=(MONO, 10),
                 bg=PANEL, fg=MUTED).pack(side=tk.LEFT, padx=(0, 8))

        self.msg_entry = tk.Entry(inp_frame, textvariable=self.msg_var,
                                  font=(MONO, 11), bg=CARD, fg=TEXT,
                                  insertbackground=ACCENT, relief=tk.FLAT,
                                  highlightbackground=BORDER, highlightthickness=1,
                                  width=38)
        self.msg_entry.pack(side=tk.LEFT, padx=(0, 16), ipady=4)

        tk.Label(inp_frame, text="SNR (dB):", font=(MONO, 10),
                 bg=PANEL, fg=MUTED).pack(side=tk.LEFT)

        self.snr_label = tk.Label(inp_frame, text="10.0", font=(MONO, 10, "bold"),
                                  bg=PANEL, fg=ACCENT, width=5)
        self.snr_label.pack(side=tk.LEFT, padx=4)

        snr_slider = tk.Scale(inp_frame, from_=1, to=30, resolution=0.5,
                              orient=tk.HORIZONTAL, variable=self.snr_var,
                              bg=PANEL, fg=TEXT, troughcolor=CARD,
                              highlightthickness=0, showvalue=False, length=140,
                              command=lambda v: self.snr_label.config(text=f"{float(v):.1f}"))
        snr_slider.pack(side=tk.LEFT, padx=(0, 16))

        btn = tk.Button(inp_frame, text="▶  KODIRAJ & POŠLJI",
                        font=(MONO, 10, "bold"), bg=ACCENT, fg="#fff",
                        activebackground=ACCENT2, activeforeground="#fff",
                        relief=tk.FLAT, padx=16, pady=6, cursor="hand2",
                        command=self.run_pipeline)
        btn.pack(side=tk.LEFT)

        # ── notebook z zavihki ──
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.TNotebook", background=BG, borderwidth=0)
        style.configure("Dark.TNotebook.Tab",
                        background=CARD, foreground=MUTED,
                        font=(MONO, 9, "bold"), padding=[14, 6],
                        borderwidth=0)
        style.map("Dark.TNotebook.Tab",
                  background=[("selected", PANEL)],
                  foreground=[("selected", ACCENT)])

        self.nb = ttk.Notebook(self.root, style="Dark.TNotebook")
        self.nb.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 16))

        self.tabs = {}
        tab_names = [
            ("okvir",    "📦  Okvir"),
            ("hamming",  "🔒  Hamming"),
            ("bpsk",     "📡  BPSK"),
            ("costas",   "🔄  Costas"),
            ("sprejem",  "📬  Sprejem"),
            ("nrz",      "〰  NRZ"),
        ]
        for key, label in tab_names:
            frame = tk.Frame(self.nb, bg=PANEL)
            self.nb.add(frame, text=label)
            self.tabs[key] = frame

        # zgradi vsebino vsakega zavihka
        self._build_frame_tab()
        self._build_hamming_tab()
        self._build_bpsk_tab()
        self._build_costas_tab()
        self._build_sprejem_tab()
        self._build_nrz_tab()

        # ── statusna vrstica ──
        self.status = tk.Label(self.root, text="Vnesi sporočilo in pritisni KODIRAJ & POŠLJI",
                               font=(MONO, 9), bg=BG, fg=MUTED, anchor=tk.W)
        self.status.pack(fill=tk.X, padx=22, pady=(0, 8))

    # ─── POMOŽNE: ustvari scrolled text ──────────────────────
    def _make_text(self, parent, height=20):
        txt = scrolledtext.ScrolledText(
            parent, font=(MONO, 9), bg=CARD, fg=TEXT,
            insertbackground=ACCENT, relief=tk.FLAT,
            highlightbackground=BORDER, highlightthickness=1,
            height=height, wrap=tk.NONE, state=tk.DISABLED)
        txt.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)
        return txt

    def _write(self, widget, text, clear=True):
        widget.config(state=tk.NORMAL)
        if clear:
            widget.delete("1.0", tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _tag(self, widget, pattern, color, start="1.0"):
        import re
        content = widget.get("1.0", tk.END)
        for m in re.finditer(pattern, content):
            s = f"1.0 + {m.start()} chars"
            e = f"1.0 + {m.end()} chars"
            widget.tag_add(color, s, e)
            widget.tag_config(color, foreground=color)

    # ─── ZAVIHEK: OKVIR ──────────────────────────────────────
    def _build_frame_tab(self):
        t = self.tabs["okvir"]
        tk.Label(t, text="Podatkovni okvir", font=(MONO, 11, "bold"),
                 bg=PANEL, fg=ACCENT).pack(anchor=tk.W, padx=12, pady=(10, 0))
        tk.Label(t, text="Razčlenitev po poljih — hex in biti",
                 font=(MONO, 9), bg=PANEL, fg=MUTED).pack(anchor=tk.W, padx=12)

        # barvna legenda
        leg = tk.Frame(t, bg=PANEL)
        leg.pack(fill=tk.X, padx=12, pady=4)
        items = [("Preambula/SOF/EOF", MUTED), ("Naslovi", ACCENT),
                 ("Payload", GREEN), ("CRC", AMBER)]
        for label, color in items:
            dot = tk.Label(leg, text="●", font=(MONO, 10), bg=PANEL, fg=color)
            dot.pack(side=tk.LEFT, padx=(0, 2))
            tk.Label(leg, text=label, font=(MONO, 9), bg=PANEL, fg=MUTED).pack(side=tk.LEFT, padx=(0, 12))

        self.frame_txt = self._make_text(t, height=28)

        # tag barve
        for tag, color in [("green", GREEN), ("amber", AMBER),
                           ("accent", ACCENT), ("muted", MUTED), ("red", RED)]:
            self.frame_txt.tag_config(tag, foreground=color)

    # ─── ZAVIHEK: HAMMING ────────────────────────────────────
    def _build_hamming_tab(self):
        t = self.tabs["hamming"]
        tk.Label(t, text="Hamming(7,4) kodiranje",
                 font=(MONO, 11, "bold"), bg=PANEL, fg=ACCENT).pack(anchor=tk.W, padx=12, pady=(10, 0))
        tk.Label(t, text="4 podatkovni biti → 7-bitni blok (3 paritetni)",
                 font=(MONO, 9), bg=PANEL, fg=MUTED).pack(anchor=tk.W, padx=12)

        # stat kartice
        self.h_stats = tk.Frame(t, bg=PANEL)
        self.h_stats.pack(fill=tk.X, padx=12, pady=6)
        self.h_cards = {}
        for key, label in [("orig", "Original"), ("kodirano", "Kodirano"),
                           ("bloki", "Blokov"), ("overhead", "Overhead")]:
            c = tk.Frame(self.h_stats, bg=CARD, padx=14, pady=8,
                         highlightbackground=BORDER, highlightthickness=1)
            c.pack(side=tk.LEFT, padx=(0, 8))
            tk.Label(c, text=label, font=(MONO, 8), bg=CARD, fg=MUTED).pack()
            lbl = tk.Label(c, text="—", font=(MONO, 12, "bold"), bg=CARD, fg=ACCENT)
            lbl.pack()
            self.h_cards[key] = lbl

        self.hamming_txt = self._make_text(t, height=22)
        for tag, color in [("green", GREEN), ("amber", AMBER),
                           ("accent", ACCENT), ("red", RED), ("muted", MUTED)]:
            self.hamming_txt.tag_config(tag, foreground=color)

    # ─── ZAVIHEK: BPSK ───────────────────────────────────────
    def _build_bpsk_tab(self):
        t = self.tabs["bpsk"]
        tk.Label(t, text="BPSK Modulacija",
                 font=(MONO, 11, "bold"), bg=PANEL, fg=ACCENT).pack(anchor=tk.W, padx=12, pady=(10, 0))
        tk.Label(t, text="bit 0 → +1.0 (faza 0°)   bit 1 → -1.0 (faza 180°)",
                 font=(MONO, 9), bg=PANEL, fg=MUTED).pack(anchor=tk.W, padx=12)

        # canvas za vizualni prikaz signalov
        self.bpsk_canvas = tk.Canvas(t, bg=CARD, height=160,
                                     highlightbackground=BORDER, highlightthickness=1)
        self.bpsk_canvas.pack(fill=tk.X, padx=12, pady=(6, 0))

        self.bpsk_txt = self._make_text(t, height=16)
        for tag, color in [("green", GREEN), ("amber", AMBER),
                           ("accent", ACCENT), ("red", RED), ("muted", MUTED)]:
            self.bpsk_txt.tag_config(tag, foreground=color)

    # ─── ZAVIHEK: COSTAS ─────────────────────────────────────
    def _build_costas_tab(self):
        t = self.tabs["costas"]
        tk.Label(t, text="Costasov sprejemnik — sinhronizacija faze",
                 font=(MONO, 11, "bold"), bg=PANEL, fg=ACCENT).pack(anchor=tk.W, padx=12, pady=(10, 0))
        tk.Label(t, text="PLL zanka: I = s·cos(φ)   Q = s·sin(φ)   napaka = I·Q   φ += α·napaka",
                 font=(MONO, 9), bg=PANEL, fg=MUTED).pack(anchor=tk.W, padx=12)

        self.costas_canvas = tk.Canvas(t, bg=CARD, height=160,
                                       highlightbackground=BORDER, highlightthickness=1)
        self.costas_canvas.pack(fill=tk.X, padx=12, pady=(6, 0))

        self.costas_txt = self._make_text(t, height=16)
        for tag, color in [("green", GREEN), ("amber", AMBER),
                           ("accent", ACCENT), ("red", RED), ("muted", MUTED)]:
            self.costas_txt.tag_config(tag, foreground=color)

    # ─── ZAVIHEK: SPREJEM ────────────────────────────────────
    def _build_sprejem_tab(self):
        t = self.tabs["sprejem"]
        tk.Label(t, text="Sprejemna stran — dekodiranje",
                 font=(MONO, 11, "bold"), bg=PANEL, fg=ACCENT).pack(anchor=tk.W, padx=12, pady=(10, 0))
        tk.Label(t, text="Hamming korekcija napak → rekonstrukcija okvirja → payload",
                 font=(MONO, 9), bg=PANEL, fg=MUTED).pack(anchor=tk.W, padx=12)

        # CRC status badge
        self.crc_badge = tk.Label(t, text="  CRC: —  ", font=(MONO, 10, "bold"),
                                  bg=CARD, fg=MUTED, padx=10, pady=4)
        self.crc_badge.pack(anchor=tk.W, padx=12, pady=4)

        self.sprejem_txt = self._make_text(t, height=26)
        for tag, color in [("green", GREEN), ("amber", AMBER),
                           ("accent", ACCENT), ("red", RED), ("muted", MUTED)]:
            self.sprejem_txt.tag_config(tag, foreground=color)

    # ─── ZAVIHEK: NRZ ────────────────────────────────────────
    def _build_nrz_tab(self):
        t = self.tabs["nrz"]
        tk.Label(t, text="NRZ-L nivoji — prvih 64 bitov okvirja",
                 font=(MONO, 11, "bold"), bg=PANEL, fg=ACCENT).pack(anchor=tk.W, padx=12, pady=(10, 0))
        tk.Label(t, text="bit 0 → +1 V (visok)   bit 1 → -1 V (nizek)",
                 font=(MONO, 9), bg=PANEL, fg=MUTED).pack(anchor=tk.W, padx=12)

        self.nrz_canvas = tk.Canvas(t, bg=CARD, height=220,
                                    highlightbackground=BORDER, highlightthickness=1)
        self.nrz_canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

    # ═══ PIPELINE ════════════════════════════════════════════
    def run_pipeline(self):
        msg = self.msg_var.get().strip()
        if not msg:
            messagebox.showwarning("Napaka", "Vnesi sporočilo!")
            return
        snr = self.snr_var.get()
        self.status.config(text="⏳  Obdelujem...", fg=AMBER)
        self.root.update()

        try:
            # ── ODDAJNA STRAN ──
            frame        = build_frame(msg)
            parsed       = parse_frame(frame)
            raw_bits     = frame_to_bits(frame)
            hamming_bits = hamming_kodiraj(raw_bits)
            symbols      = bpsk_modulate(hamming_bits)
            noisy        = awgn_noise(symbols, snr)

            # ── KANAL ──
            synced       = costas_loop(noisy)

            # ── SPREJEMNA STRAN ──
            demod_bits          = bpsk_demodulate(synced)
            corrected, napake   = hamming_dekodiraj(demod_bits)
            received_frame      = bits_to_bytes(corrected)

            try:
                recv_parsed = parse_frame(received_frame)
            except Exception:
                recv_parsed = None

            self.results = {
                'frame': frame, 'parsed': parsed,
                'raw_bits': raw_bits, 'hamming_bits': hamming_bits,
                'symbols': symbols, 'noisy': noisy,
                'synced': synced, 'demod_bits': demod_bits,
                'corrected': corrected, 'napake': napake,
                'received_frame': received_frame, 'recv_parsed': recv_parsed,
                'msg': msg, 'snr': snr,
            }

            self._update_frame_tab()
            self._update_hamming_tab()
            self._update_bpsk_tab()
            self._update_costas_tab()
            self._update_sprejem_tab()
            self._update_nrz_tab()

            bit_errors = sum(1 for a, b in zip(hamming_bits, demod_bits) if a != b)
            corr_count = sum(1 for n in napake if n != 0)
            self.status.config(
                text=f"✓  Uspešno | Okvir: {len(frame)} B | "
                     f"Hamming blokov: {len(hamming_bits)//7} | "
                     f"Bitnih napak: {bit_errors} | "
                     f"Hamming korekcij: {corr_count} | SNR: {snr} dB",
                fg=GREEN)
        except Exception as e:
            self.status.config(text=f"✗  Napaka: {e}", fg=RED)
            raise

    # ─── UPDATE: OKVIR ───────────────────────────────────────
    def _update_frame_tab(self):
        r = self.results
        frame  = r['frame']
        parsed = r['parsed']

        def hex_str(b): return ' '.join(f'{x:02X}' for x in b)
        def bit_str(b): return ' '.join(f'{x:08b}' for x in b)

        lines = []
        lines.append("═" * 72)
        lines.append("PODATKOVNI OKVIR")
        lines.append("═" * 72)
        lines.append(f"Skupna dolžina : {len(frame)} bajtov\n")

        sections = [
            ("PREAMBLE",    parsed['preamble'],    MUTED),
            ("SOF",         parsed['sof'],          MUTED),
            ("FRAME_TYPE",  parsed['frame_type'],   MUTED),
            ("SRC_ADDR",    parsed['src'],          ACCENT),
            ("DST_ADDR",    parsed['dst'],          ACCENT),
            ("PAYLOAD_LEN", struct.pack('>H', parsed['payload_len']), MUTED),
            ("PAYLOAD",     parsed['payload'],      GREEN),
            ("CRC32",       parsed['received_crc'], AMBER),
            ("EOF",         parsed['eof'],          MUTED),
        ]

        lines.append(f"{'Polje':<12} │ {'Dolž':>4} │ {'HEX':<28} │ BITI")
        lines.append("─" * 72)
        for name, data, _ in sections:
            h = hex_str(data)
            b = bit_str(data)
            lines.append(f"{name:<12} │ {len(data):>4} B │ {h:<28} │ {b}")

        lines.append("═" * 72)
        lines.append(f"\nPayload text : {parsed['payload_text']}")
        lines.append(f"CRC OK       : {'✓ DA' if parsed['crc_ok'] else '✗ NE'}")
        lines.append(f"\nSRC : {':'.join(f'{x:02X}' for x in parsed['src'])}")
        lines.append(f"DST : {':'.join(f'{x:02X}' for x in parsed['dst'])}")

        txt = self.frame_txt
        self._write(txt, '\n'.join(lines))

        # pobarvaj vrstice
        txt.config(state=tk.NORMAL)
        content = txt.get("1.0", tk.END).split('\n')
        for i, line in enumerate(content):
            ln = f"{i+1}.0"
            le = f"{i+1}.end"
            if any(x in line for x in ["PREAMBLE", "SOF", "FRAME_TYPE", "EOF", "PAYLOAD_LEN"]):
                txt.tag_add("muted", ln, le)
            elif "SRC_ADDR" in line or "DST_ADDR" in line:
                txt.tag_add("accent", ln, le)
            elif "PAYLOAD" in line and "LEN" not in line:
                txt.tag_add("green", ln, le)
            elif "CRC32" in line:
                txt.tag_add("amber", ln, le)
            elif "✓" in line:
                txt.tag_add("green", ln, le)
            elif "✗" in line:
                txt.tag_add("red", ln, le)
        txt.config(state=tk.DISABLED)

    # ─── UPDATE: HAMMING ─────────────────────────────────────
    def _update_hamming_tab(self):
        r = self.results
        raw  = r['raw_bits']
        coded = r['hamming_bits']

        self.h_cards["orig"].config(text=f"{len(raw)} b")
        self.h_cards["kodirano"].config(text=f"{len(coded)} b")
        self.h_cards["bloki"].config(text=str(len(coded)//7))
        self.h_cards["overhead"].config(text="75.0%")

        lines = []
        lines.append(f"{'Blok':>5} │ {'Orig (4b)':^10} │ {'Kodiran (7b)':^14} │ {'p1':^3} {'p2':^3} {'p4':^3} │ Napaka")
        lines.append("─" * 60)

        num = min(len(coded)//7, 80)
        for i in range(num):
            orig   = raw  [i*4 : i*4+4]
            blok   = coded[i*7 : i*7+7]
            os     = ''.join(map(str, orig))
            bs     = ''.join(map(str, blok))
            p1, p2, _, p4, _, _, _ = blok
            lines.append(f"{i+1:>5} │ {os:^10} │ {bs:^14} │ {p1:^3} {p2:^3} {p4:^3} │")

        if len(coded)//7 > 80:
            lines.append(f"  ... ({len(coded)//7 - 80} blokov skritih)")

        txt = self.hamming_txt
        self._write(txt, '\n'.join(lines))

        txt.config(state=tk.NORMAL)
        content = txt.get("1.0", tk.END).split('\n')
        for i, line in enumerate(content):
            if i > 1 and line.strip():
                ln = f"{i+1}.0"; le = f"{i+1}.end"
                parts = line.split('│')
                if len(parts) >= 3:
                    # pobarvaj kodirani del
                    start = line.find('│', line.find('│')+1) + 2
                    end   = line.find('│', start)
                    txt.tag_add("green", f"{i+1}.{start}", f"{i+1}.{end}")
        txt.config(state=tk.DISABLED)

    # ─── UPDATE: BPSK ────────────────────────────────────────
    def _update_bpsk_tab(self):
        r = self.results
        hb    = r['hamming_bits']
        syms  = r['symbols']
        noisy = r['noisy']

        # nariši signal na canvasu
        c = self.bpsk_canvas
        c.delete("all")
        c.update()
        W = c.winfo_width() or 900
        H = 160
        mid = H // 2

        c.create_line(0, mid, W, mid, fill=BORDER, width=1)
        c.create_text(8, 20, text="+1", font=(MONO, 8), fill=MUTED, anchor=tk.W)
        c.create_text(8, H-20, text="−1", font=(MONO, 8), fill=MUTED, anchor=tk.W)
        c.create_text(W//2, 12, text="BPSK moduliran signal (prvih 64 bitov)",
                      font=(MONO, 8), fill=MUTED)

        n_show = min(64, len(syms))
        step = (W - 40) / n_show
        margin = 30

        for i in range(n_show):
            x0 = margin + i * step
            x1 = margin + (i+1) * step
            y_sym   = mid - syms[i] * (mid - 20)
            y_noisy = mid - noisy[i] * (mid - 20)
            y_noisy = max(5, min(H-5, y_noisy))

            # pravokoten signal
            if i > 0:
                y_prev = mid - syms[i-1] * (mid - 20)
                c.create_line(x0, y_prev, x0, y_sym, fill=ACCENT, width=2)
            c.create_line(x0, y_sym, x1, y_sym, fill=ACCENT, width=2)

            # noisy točka
            color = GREEN if (noisy[i] >= 0) == (syms[i] >= 0) else RED
            c.create_oval(x0+step/2-2, y_noisy-2, x0+step/2+2, y_noisy+2,
                          fill=color, outline="")

        # legenda
        c.create_line(W-120, 20, W-100, 20, fill=ACCENT, width=2)
        c.create_text(W-96, 20, text="signal", font=(MONO, 8), fill=ACCENT, anchor=tk.W)
        c.create_oval(W-123, 33, W-117, 39, fill=GREEN, outline="")
        c.create_text(W-112, 36, text="OK", font=(MONO, 8), fill=GREEN, anchor=tk.W)
        c.create_oval(W-123, 47, W-117, 53, fill=RED, outline="")
        c.create_text(W-112, 50, text="napaka", font=(MONO, 8), fill=RED, anchor=tk.W)

        # tabela
        demod  = bpsk_demodulate(noisy)
        napake = sum(1 for a, b in zip(hb, demod) if a != b)
        lines  = []
        lines.append(f"{'Blok':>5} │ {'Hamming (7b)':^14} │ {'Simboli':^28} │ {'Noisy (7)':^42} │ Napake")
        lines.append("─" * 100)

        n_blok = min(len(hb)//7, 40)
        for i in range(n_blok):
            hblok  = hb   [i*7:i*7+7]
            sblok  = syms [i*7:i*7+7]
            nblok  = noisy[i*7:i*7+7]
            dblok  = demod[i*7:i*7+7]
            hs  = ''.join(map(str, hblok))
            ss  = ' '.join(f"{s:+.0f}" for s in sblok)
            ns  = ' '.join(f"{n:+.2f}" for n in nblok)
            err = sum(1 for a, b in zip(hblok, dblok) if a != b)
            es  = f"{'✗ '+str(err) if err else '✓':^6}"
            lines.append(f"{i+1:>5} │ {hs:^14} │ {ss:^28} │ {ns:^42} │ {es}")

        lines.append("─" * 100)
        lines.append(f"Skupaj bitnih napak: {napake} / {len(hb)} ({napake/len(hb)*100:.2f}%)")

        txt = self.bpsk_txt
        self._write(txt, '\n'.join(lines))
        txt.config(state=tk.NORMAL)
        content = txt.get("1.0", tk.END).split('\n')
        for i, line in enumerate(content):
            ln = f"{i+1}.0"; le = f"{i+1}.end"
            if "✓" in line: txt.tag_add("green", ln, le)
            if "✗" in line: txt.tag_add("red", ln, le)
        txt.config(state=tk.DISABLED)

    # ─── UPDATE: COSTAS ──────────────────────────────────────
    def _update_costas_tab(self):
        r = self.results
        noisy  = r['noisy']
        synced = r['synced']

        # nariši primerjavo noisy vs synced
        c = self.costas_canvas
        c.delete("all")
        c.update()
        W = c.winfo_width() or 900
        H = 160; mid = H // 2

        c.create_line(0, mid, W, mid, fill=BORDER, width=1)
        c.create_text(W//2, 12, text="Noisy (rdeča) vs Synced/Costas (zelena) — prvih 80 simbolov",
                      font=(MONO, 8), fill=MUTED)

        n_show = min(80, len(noisy))
        step   = (W - 40) / n_show
        margin = 20

        pts_noisy  = []
        pts_synced = []
        for i in range(n_show):
            x  = margin + i * step + step/2
            yn = mid - max(-1.8, min(1.8, noisy [i])) * (mid - 20)
            ys = mid - max(-1.8, min(1.8, synced[i])) * (mid - 20)
            pts_noisy.append((x, yn))
            pts_synced.append((x, ys))

        for i in range(1, len(pts_noisy)):
            c.create_line(*pts_noisy[i-1],  *pts_noisy[i],  fill=RED,   width=1)
            c.create_line(*pts_synced[i-1], *pts_synced[i], fill=GREEN, width=1)

        c.create_line(W-140, 20, W-120, 20, fill=RED,   width=1)
        c.create_text(W-116, 20, text="noisy",  font=(MONO, 8), fill=RED,   anchor=tk.W)
        c.create_line(W-140, 34, W-120, 34, fill=GREEN, width=1)
        c.create_text(W-116, 34, text="synced", font=(MONO, 8), fill=GREEN, anchor=tk.W)

        # tabela
        b_noisy  = bpsk_demodulate(noisy)
        b_synced = bpsk_demodulate(synced)
        popr     = sum(1 for a, b in zip(b_noisy, b_synced) if a != b)

        lines = []
        lines.append(f"{'Sim':>5} │ {'Noisy':^10} │ {'Synced':^10} │ {'Bit(noisy)':^12} │ {'Bit(sync)':^12} │ Status")
        lines.append("─" * 72)

        for i in range(min(30, len(noisy))):
            bn = 0 if noisy [i] >= 0 else 1
            bs = 0 if synced[i] >= 0 else 1
            st = "✓" if bn == bs else "✗ POPRAVLJEN"
            lines.append(f"{i+1:>5} │ {noisy[i]:+.4f}{'':>3} │ {synced[i]:+.4f}{'':>3} │ "
                         f"{bn:^12} │ {bs:^12} │ {st}")

        lines.append("─" * 72)
        lines.append(f"Popravljenih simbolov: {popr} / {len(noisy)}")
        lines.append(f"α (loop gain): 0.05")

        txt = self.costas_txt
        self._write(txt, '\n'.join(lines))
        txt.config(state=tk.NORMAL)
        content = txt.get("1.0", tk.END).split('\n')
        for i, line in enumerate(content):
            ln = f"{i+1}.0"; le = f"{i+1}.end"
            if "✓" in line and "POPRAVLJEN" not in line:
                txt.tag_add("green", ln, le)
            if "POPRAVLJEN" in line:
                txt.tag_add("amber", ln, le)
        txt.config(state=tk.DISABLED)

    # ─── UPDATE: SPREJEM ─────────────────────────────────────
    def _update_sprejem_tab(self):
        r = self.results
        napake      = r['napake']
        corrected   = r['corrected']
        recv_parsed = r['recv_parsed']
        demod_bits  = r['demod_bits']
        hb          = r['hamming_bits']

        popravljeni = sum(1 for n in napake if n != 0)
        crc_ok = recv_parsed['crc_ok'] if recv_parsed else False

        self.crc_badge.config(
            text=f"  CRC: {'✓ VELJAVNO' if crc_ok else '✗ NAPAKA'}  ",
            bg=CARD,
            fg=GREEN if crc_ok else RED)

        lines = []
        lines.append("═" * 72)
        lines.append("HAMMING DEKODIRANJE — KOREKCIJA NAPAK")
        lines.append("═" * 72)
        lines.append(f"{'Blok':>5} │ {'Sprejeto (7b)':^14} │ {'Dekodirano (4b)':^16} │ Status")
        lines.append("─" * 60)

        num = min(len(napake), 80)
        for i in range(num):
            blok_in  = demod_bits[i*7 : i*7+7]
            blok_out = corrected [i*4 : i*4+4]
            bi = ''.join(map(str, blok_in))
            bo = ''.join(map(str, blok_out))
            ep = napake[i]
            st = f"✗ napaka pos {ep} → popravljena" if ep != 0 else "✓"
            lines.append(f"{i+1:>5} │ {bi:^14} │ {bo:^16} │ {st}")

        if len(napake) > 80:
            lines.append(f"  ... ({len(napake)-80} blokov skritih)")

        lines.append("─" * 60)
        lines.append(f"Blokov skupaj  : {len(napake)}")
        lines.append(f"Popravljenih   : {popravljeni}")
        lines.append(f"Brez napake    : {len(napake) - popravljeni}")

        if recv_parsed:
            lines.append("")
            lines.append("═" * 72)
            lines.append("REKONSTRUIRAN OKVIR")
            lines.append("═" * 72)
            lines.append(f"Payload text : {recv_parsed['payload_text']}")
            lines.append(f"CRC OK       : {'✓ DA' if recv_parsed['crc_ok'] else '✗ NE'}")
            lines.append(f"Ujemanje     : {'✓ IDENTIČNO' if recv_parsed['payload_text'] == r['msg'] else '✗ RAZLIKA'}")

            orig = r['msg']
            recv = recv_parsed['payload_text']
            if orig != recv:
                lines.append(f"\nOriginal : {orig}")
                lines.append(f"Prejeto  : {recv}")

        txt = self.sprejem_txt
        self._write(txt, '\n'.join(lines))
        txt.config(state=tk.NORMAL)
        content = txt.get("1.0", tk.END).split('\n')
        for i, line in enumerate(content):
            ln = f"{i+1}.0"; le = f"{i+1}.end"
            if "✓" in line and "napaka" not in line.lower():
                txt.tag_add("green", ln, le)
            if "✗" in line or "napaka" in line.lower():
                txt.tag_add("amber", ln, le)
            if "IDENTIČNO" in line:
                txt.tag_add("green", ln, le)
        txt.config(state=tk.DISABLED)

    # ─── UPDATE: NRZ ─────────────────────────────────────────
    def _update_nrz_tab(self):
        c = self.nrz_canvas
        c.delete("all")
        c.update()
        W = c.winfo_width() or 900
        H = c.winfo_height() or 220

        bits    = self.results['raw_bits']
        n_show  = min(64, len(bits))
        margin  = 40
        mid     = H // 2
        amp     = (H - 60) // 2
        step    = (W - 2*margin) / n_show

        # osi
        c.create_line(margin, mid, W-margin, mid, fill=BORDER, width=1, dash=(4,4))
        c.create_line(margin, mid-amp-10, margin, mid+amp+10, fill=BORDER, width=1)

        c.create_text(margin-8, mid-amp, text="+1V", font=(MONO, 8), fill=MUTED, anchor=tk.E)
        c.create_text(margin-8, mid+amp, text="−1V", font=(MONO, 8), fill=MUTED, anchor=tk.E)
        c.create_text(W//2, 12, text=f"NRZ-L — prvih {n_show} bitov okvirja",
                      font=(MONO, 9), fill=MUTED)

        # signal
        for i in range(n_show):
            bit    = bits[i]
            level  = -1 if bit == 1 else 1
            x0     = margin + i * step
            x1     = margin + (i+1) * step
            y      = mid - level * amp
            color  = ACCENT if bit == 0 else ACCENT2

            # vodoravna črta
            c.create_line(x0, y, x1, y, fill=color, width=2)

            # navpična črta (prehod)
            if i > 0:
                prev_level = -1 if bits[i-1] == 1 else 1
                y_prev     = mid - prev_level * amp
                c.create_line(x0, y_prev, x0, y, fill=MUTED, width=1)

            # bit oznaka (vsak 4. bit)
            if i % 4 == 0:
                c.create_text(x0 + step/2, mid + amp + 16,
                              text=str(bit), font=(MONO, 7),
                              fill=MUTED)

        # legenda
        c.create_line(W-180, H-30, W-160, H-30, fill=ACCENT,  width=2)
        c.create_text(W-156, H-30, text="bit 0 (+1V)", font=(MONO, 8), fill=ACCENT,  anchor=tk.W)
        c.create_line(W-180, H-15, W-160, H-15, fill=ACCENT2, width=2)
        c.create_text(W-156, H-15, text="bit 1 (−1V)", font=(MONO, 8), fill=ACCENT2, anchor=tk.W)

# ═══════════════════════════════════════════════════════════════
# ZAGON
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    app  = ProtocolGUI(root)
    root.mainloop()