import numpy as np
import matplotlib.pyplot as plt
import random
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from transmitter import bpsk_modulate
from receiver import bpsk_demodulate


def generate_bits(num_bits):
    bits = []
    for _ in range(num_bits):
        bits.append(random.randint(0, 1))
    return bits


def calculate_ber(tx_bits, rx_bits):
    errors = 0
    for tx, rx in zip(tx_bits, rx_bits):
        if tx != rx:
            errors += 1
    return errors / len(tx_bits)


def add_complex_awgn(signal, snr_db):
    signal = np.array(signal, dtype=complex)

    snr_linear = 10 ** (snr_db / 10)
    signal_power = np.mean(np.abs(signal) ** 2)
    noise_power = signal_power / snr_linear

    noise = np.sqrt(noise_power / 2) * (
        np.random.randn(len(signal)) + 1j * np.random.randn(len(signal))
    )

    return signal + noise


def ofdm_bpsk_simulation(num_bits, snr_values, num_subcarriers=64):
    ber_results = []

    for snr_db in snr_values:
        tx_bits = generate_bits(num_bits)
        tx_symbols = np.array(bpsk_modulate(tx_bits), dtype=complex)

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

        rx_bits = bpsk_demodulate(rx_symbols_all)
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