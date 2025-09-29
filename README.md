RGB Music Visualizer
====================

Synchronizes two RGB LEDs to music, creating visual effects based on audio waveforms. Smooth color transitions for moody tracks, vibrant flashes for rhythmic beats.

Overview
--------

This Python script analyzes real-time audio and sends color commands to an ESP32 controlling two RGB LEDs. The LEDs are synchronized, with a GUI showing the effect. Works for both energetic and calm music, always emitting light.

Features
--------

- Synchronized LEDs reacting to audio amplitude
- Smooth transitions for ambient music
- Flashing for rhythmic beats
- GUI with two circles mirroring LEDs
- HTTP communication between Python and ESP32

Files
-----

- CoolRGBmusician.py – Python script for audio processing and LED control
- main.py – ESP32 firmware for HTTP color commands
- microdot.py – Microdot library for ESP32 HTTP server

Requirements
------------

Hardware:

- ESP32 (e.g., DevKitC) with two RGB LEDs:
  - LED 1: Red (Pin 13), Green (Pin 14), Blue (Pin 15)
  - LED 2: Red (Pin 10), Green (Pin 11), Blue (Pin 12)
- Computer with audio output

Software:

- Python 3.10+
- Python dependencies: numpy, soundcard, requests
- ESP32 with MicroPython firmware
- microdot.py (included)

Setup
-----

1. Clone repository:
   git clone https://github.com/Robindhuil/CoolRGBmusician.git
2. Install Python dependencies:
   pip install numpy soundcard requests
3. Configure ESP32:
   - Install MicroPython
   - Update WIFI_SSID and WIFI_PASSWORD in main.py
   - Upload main.py and microdot.py to ESP32 (using Thonny or ampy)
   - Check ESP32 IP (default: 192.168.1.100) and update ESP32_IP in CoolRGBmusician.py if needed

Usage
-----

1. Run the Python script:
   python CoolRGBmusician.py
2. Play music. LEDs will display synchronized colors, with smooth transitions for low amplitudes and flashes for beats.

Troubleshooting
---------------

No LED light:
- Check Wi-Fi and ESP32 IP
- Test in browser: http://192.168.1.100/set_colors/255/0/0 (sets red)
- Verify LED wiring and pins in main.py

ConnectTimeout errors:
- Increase timeout in CoolRGBmusician.py (e.g., timeout=0.7)
- Ensure stable Wi-Fi

For moody songs:
- Adjust MIN_BRIGHTNESS or MIN_SATURATION in CoolRGBmusician.py
