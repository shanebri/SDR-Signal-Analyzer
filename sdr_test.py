from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt

sdr = RtlSdr()

sdr.sample_rate = 2.4e6
sdr.center_freq = 100e6  # FM band
sdr.gain = 'auto'

samples = sdr.read_samples(256*1024)

fft = np.fft.fftshift(np.fft.fft(samples))
freqs = np.fft.fftshift(np.fft.fftfreq(len(fft), 1/sdr.sample_rate))

plt.plot(freqs, np.abs(fft))
plt.title("SDR Spectrum")
plt.show()

sdr.close()