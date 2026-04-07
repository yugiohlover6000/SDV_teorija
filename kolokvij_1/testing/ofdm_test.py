import numpy as np
import matplotlib.pyplot as plt


def generate_bits(num_bits):
    return np.random.randint(0, 2, num_bits).tolist()


def bpsk_map(bits):
    symbols = []
    for bit in bits:
        if bit == 1:
            symbols.append(1)
        else:
            symbols.append(-1)
    return np.array(symbols, dtype=complex)


def bpsk_demap(symbols):
    bits = []
    for s in symbols:
        if s.real > 0:
            bits.append(1)
        else:
            bits.append(0)
    return bits


def add_complex_awgn(signal, snr_db):
    snr_linear = 10 ** (snr_db / 10)
    signal_power = np.mean(np.abs(signal) ** 2)
    noise_power = signal_power / snr_linear

    noise = np.sqrt(noise_power / 2) * (
        np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))
    )

    return signal + noise


def calculate_ber(tx_bits, rx_bits):
    errors = 0
    for tx, rx in zip(tx_bits, rx_bits):
        if tx != rx:
            errors += 1
    return errors / len(tx_bits)


def ofdm_bpsk_simulation(num_bits, snr_values, num_subcarriers=64):
    ber_results = []

    for snr_db in snr_values:
        tx_bits = generate_bits(num_bits)
        tx_symbols = bpsk_map(tx_bits)

        rx_symbols_all = []

        for i in range(0, len(tx_symbols), num_subcarriers):
            block = tx_symbols[i:i + num_subcarriers]
            original_len = len(block)

            if len(block) < num_subcarriers:
                padding = np.zeros(num_subcarriers - len(block), dtype=complex)
                block = np.concatenate((block, padding))

            ofdm_time_signal = np.fft.ifft(block)
            noisy_signal = add_complex_awgn(ofdm_time_signal, snr_db)
            rx_block = np.fft.fft(noisy_signal)

            rx_symbols_all.extend(rx_block[:original_len])

        rx_bits = bpsk_demap(rx_symbols_all)
        rx_bits = rx_bits[:len(tx_bits)]

        ber = calculate_ber(tx_bits, rx_bits)
        ber_results.append(ber)

        print("SNR =", snr_db, "dB   BER =", ber)

    return ber_results


def plot_graph(snr_values, ber_results):
    plt.plot(snr_values, ber_results, marker='o')
    plt.yscale('log')
    plt.xlabel("SNR [dB]")
    plt.ylabel("BER")
    plt.title("OFDM-BPSK + AWGN")
    plt.grid(True)
    plt.show()


num_bits = 10000
snr_values = [-2, 0, 2, 4, 6, 8, 10]

ber_results = ofdm_bpsk_simulation(num_bits, snr_values)
plot_graph(snr_values, ber_results)