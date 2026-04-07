import random
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from transmitter import bpsk_modulate, awgn_noise
from receiver import bpsk_demodulate


def generate_bits(num_bits):
    bits = []
    for i in range(num_bits):
        bits.append(random.randint(0, 1))
    return bits


def calculate_ber(transmitted_bits, received_bits):
    errors = 0

    for tx, rx in zip(transmitted_bits, received_bits):
        if tx != rx:
            errors += 1

    return errors / len(transmitted_bits)


def ber_simulation(num_bits, snr_values):
    ber_results = []

    for snr_db in snr_values:
        transmitted_bits = generate_bits(num_bits)

        transmitted_symbols = bpsk_modulate(transmitted_bits)
        received_symbols = awgn_noise(transmitted_symbols, snr_db)
        received_bits = bpsk_demodulate(received_symbols)

        ber = calculate_ber(transmitted_bits, received_bits)
        ber_results.append(ber)

        print("SNR =", snr_db, "dB   BER =", ber)

    return ber_results


def plot_graph(snr_values, ber_results):
    plt.plot(snr_values, ber_results, marker='o')
    plt.yscale('log')
    plt.xlabel("SNR [dB]")
    plt.ylabel("BER")
    plt.title("BPSK + AWGN")
    plt.grid(True)
    plt.show()


num_bits = 10000
snr_values = [-2, 0, 2, 4, 6, 8, 10]

ber_results = ber_simulation(num_bits, snr_values)
plot_graph(snr_values, ber_results)