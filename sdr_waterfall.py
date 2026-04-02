from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# SDR configuration
# -----------------------------
sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.center_freq = 100e6
sdr.gain = 'auto'

num_samples = 64 * 1024
waterfall_rows = 100
pause_time = 0.01
quit_keys = {"f"}  # Add keys here, e.g. {"f", "q", "escape"}

# -----------------------------
# Frequency axis
# -----------------------------
freqs = np.fft.fftshift(np.fft.fftfreq(num_samples, 1 / sdr.sample_rate))
freqs_mhz = (freqs + sdr.center_freq) / 1e6

# -----------------------------
# Waterfall buffer
# -----------------------------
waterfall = np.full((waterfall_rows, num_samples), -120.0)

# -----------------------------
# Plot setup
# -----------------------------
plt.ion()
fig, (ax1, ax2) = plt.subplots(
    2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [1, 2]}
)

running = True

def on_key(event):
    global running
    key = (event.key or "").lower()
    if key in quit_keys:
        running = False
        plt.close(fig)


def on_close(_event):
    global running
    running = False

fig.canvas.mpl_connect('key_press_event', on_key)
fig.canvas.mpl_connect('close_event', on_close)

line, = ax1.plot(freqs_mhz, np.zeros(num_samples), lw=1)
peak_scatter, = ax1.plot([], [], 'ro', markersize=4)
peak_text = ax1.text(0.01, 0.95, "", transform=ax1.transAxes, va='top')

ax1.set_title("Live RTL-SDR Spectrum with Peak Detection")
ax1.set_xlabel("Frequency (MHz)")
ax1.set_ylabel("Power (dB)")
ax1.grid(True)
ax1.set_xlim(freqs_mhz[0], freqs_mhz[-1])
ax1.set_ylim(-80, 50)

im = ax2.imshow(
    waterfall,
    aspect='auto',
    origin='lower',
    cmap='viridis',
    extent=[freqs_mhz[0], freqs_mhz[-1], 0, waterfall_rows],
    vmin=-60,
    vmax=50
)

ax2.set_title(f"Live RTL-SDR Waterfall (Press {', '.join(sorted(quit_keys))} to exit)")
ax2.set_xlabel("Frequency (MHz)")
ax2.set_ylabel("Frame Index")

cbar = fig.colorbar(im, ax=ax2)
cbar.set_label("Power (dB)")

plt.tight_layout()

print(f"Starting live display. Press {', '.join(sorted(quit_keys))} in the plot window to exit.")

try:
    while running and plt.fignum_exists(fig.number):
        samples = sdr.read_samples(num_samples)

        window = np.hanning(len(samples))
        samples = samples * window

        fft_vals = np.fft.fftshift(np.fft.fft(samples))
        power = 20 * np.log10(np.abs(fft_vals) + 1e-12)
        power_clipped = np.clip(power, -60, 50)

        # -----------------------------
        # Noise floor + threshold
        # -----------------------------
        noise_floor = np.median(power_clipped)
        threshold = noise_floor + 10  # adjust this if needed

        # Simple local-max peak detection
        peak_mask = (
            (power_clipped[1:-1] > power_clipped[:-2]) &
            (power_clipped[1:-1] > power_clipped[2:]) &
            (power_clipped[1:-1] > threshold)
        )

        peak_indices = np.where(peak_mask)[0] + 1

        # Limit markers so the plot doesn't get cluttered
        if len(peak_indices) > 20:
            strongest = np.argsort(power_clipped[peak_indices])[-20:]
            peak_indices = peak_indices[strongest]

        min_spacing_hz = 200e3  # 200 kHz (FM station width)
        min_spacing_bins = int(min_spacing_hz / (sdr.sample_rate / num_samples))

        filtered_peaks = []
        for idx in peak_indices:
            if all(abs(idx - fp) > min_spacing_bins for fp in filtered_peaks):
                filtered_peaks.append(idx)

        peak_indices = np.array(filtered_peaks)

        peak_freqs = freqs_mhz[peak_indices]
        peak_powers = power_clipped[peak_indices]

        # Update spectrum
        line.set_ydata(power_clipped)
        peak_scatter.set_data(peak_freqs, peak_powers)
        peak_text.set_text(
            f"Noise floor: {noise_floor:.1f} dB\n"
            f"Threshold: {threshold:.1f} dB\n"
            f"Detected peaks: {len(peak_indices)}"
        )

        # Update waterfall
        waterfall[:-1] = waterfall[1:]
        waterfall[-1] = power_clipped
        im.set_data(waterfall)

        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(pause_time)

except KeyboardInterrupt:
    print("Stopped by keyboard interrupt.")

finally:
    sdr.close()
    if plt.fignum_exists(fig.number):
        plt.close(fig)
