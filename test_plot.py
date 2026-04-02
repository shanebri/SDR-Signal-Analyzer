import numpy as np
import matplotlib.pyplot as plt

# Fake signal
fs = 1e6
t = np.arange(1024) / fs
signal = np.sin(2 * np.pi * 100e3 * t)

# FFT
fft = np.fft.fft(signal)
freqs = np.fft.fftfreq(len(fft), 1/fs)

plt.plot(freqs, np.abs(fft))
plt.title("Test FTT")
plt.show()