# SDR Signal Analyzer

Real-time RTL-SDR spectrum and waterfall viewer built with Python, NumPy, and Matplotlib.

## What it does

- Streams IQ samples from an RTL-SDR dongle.
- Computes FFT power spectrum in real time.
- Displays:
  - live spectrum
  - rolling waterfall
  - peak markers and simple threshold-based peak count
- Lets you quit from the plot window using configurable keys (default: `f`).

## Project files

- `sdr_waterfall.py`: main real-time spectrum + waterfall + peak detection app
- `sdr_test.py`: basic single-shot SDR spectrum test
- `test_plot.py`: local plotting sanity check without SDR hardware

## Requirements

- Python 3.10+
- RTL-SDR hardware (for `sdr_waterfall.py` and `sdr_test.py`) (I use RTL-SDR Blog V4)
- System RTL-SDR library/driver available (commonly `librtlsdr`)

Install Python dependencies:

```bash
python3 -m venv sdr_env
source sdr_env/bin/activate
pip install -r requirements.txt
```

If needed, install RTL-SDR system package first:

- macOS (Homebrew): `brew install librtlsdr`
- Debian/Ubuntu: `sudo apt-get install rtl-sdr`


