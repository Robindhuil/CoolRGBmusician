import tkinter as tk  # GUI pre vizualizáciu
import numpy as np  # Práca s číselnými dátami
import soundcard as sc  # Spracovanie zvuku
import threading  # Spustenie audia v samostatnom vlákne
import requests  # Odosielanie farieb na ESP32
import colorsys  # Konverzia farieb HSV → RGB
import warnings  # Potlačenie varovaní
import time  # Pre časovanie

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="soundcard.mediafoundation")

# Nastavenia zvuku a spracovania amplitúdy
SAMPLE_RATE = 44100
BLOCK_SIZE = 512  # Menší blok pre nižšiu latenciu
DECAY_RATE = 0.1  # Pomalší útlm pre plynulosť
BEAT_THRESHOLD = 1.1  # Veľmi citlivý threshold pre jemné vlny
FLASH_DURATION = 0.1  # Jemné bliknutie
ESP32_IP = "192.168.1.100"
SMOOTHING_FACTOR = 0.5  # Silnejšie vyhladzovanie
MIN_BRIGHTNESS = 0.2  # Minimálny jas pre náladové skladby
MIN_SATURATION = 0.3  # Minimálna saturácia

# Vytvorenie GUI
root = tk.Tk()
root.title("Zvuková vizualizácia - Plynulé Blikanie")
canvas = tk.Canvas(root, width=800, height=600, bg="black")
canvas.pack()

# Definovanie pozícií dvoch kruhov
circle_positions = [(300, 300), (500, 300)]
circles = [canvas.create_oval(x - 100, y - 100, x + 100, y + 100, outline="white", width=4, fill="black") for x, y in circle_positions]

# Globálne premenné
energy_history = []  # História energií
max_history = 15  # Kratšia história pre rýchlu reakciu
hue_offset = 0  # Rotácia farieb
hue_speed = 0.002  # Veľmi pomalá zmena farieb pre náladové skladby
smoothed_level = MIN_BRIGHTNESS  # Začneme s minimálnym jasom
flash_timer = 0  # Časovač blikania

# Konverzia HSV na RGB
def hsv_to_rgb(h, s, v):
    h = h % 1.0
    r, g, b = [int(c * 255) for c in colorsys.hsv_to_rgb(h, s, v)]
    return r, g, b

# Odoslanie farby pre obe LED
def send_colors(color):
    r, g, b = color
    try:
        threading.Thread(target=lambda: requests.get(
            f"http://{ESP32_IP}/set_colors/{r}/{g}/{b}", timeout=0.5
        )).start()
    except requests.RequestException:
        pass  # Preskočíme chybu, aby slučka pokračovala

# Hlavná funkcia na spracovanie audia
def process_audio():
    global smoothed_level, hue_offset, flash_timer
    try:
        speaker = sc.default_speaker()
        previous_energy = 0

        with sc.get_microphone(id=str(speaker.id), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
            while True:
                start_time = time.time()
                try:
                    data = mic.record(numframes=BLOCK_SIZE)
                    if data.size == 0:
                        smoothed_level = max(MIN_BRIGHTNESS, smoothed_level - DECAY_RATE)
                    else:
                        mono_data = np.mean(data, axis=1)
                        current_energy = np.sqrt(np.mean(mono_data ** 2))  # RMS amplitúda

                        # Normalizácia a vyhladenie
                        raw_level = min(1, current_energy * 4)  # Veľmi citlivá normalizácia
                        smoothed_level = SMOOTHING_FACTOR * raw_level + (1 - SMOOTHING_FACTOR) * smoothed_level
                        smoothed_level = max(MIN_BRIGHTNESS, smoothed_level)  # Minimálny jas

                        # Detekcia rytmu
                        energy_history.append(current_energy)
                        if len(energy_history) > max_history:
                            energy_history.pop(0)
                        avg_energy = np.mean(energy_history) if energy_history else 0

                        # Blikanie pri vysokej amplitúde
                        if current_energy > avg_energy * BEAT_THRESHOLD and flash_timer <= 0:
                            smoothed_level = 1.0
                            flash_timer = FLASH_DURATION
                            hue_offset += 0.15  # Rýchla zmena farby pri beate

                        # Jemné pulzovanie pri nízkych amplitúdach
                        if current_energy > previous_energy * 1.05:  # Veľmi jemná detekcia
                            hue_offset += 0.03  # Pomalá zmena farby
                        previous_energy = current_energy

                        # Decay
                        smoothed_level = max(MIN_BRIGHTNESS, smoothed_level - DECAY_RATE)

                    # Generovanie farby
                    hue_offset += hue_speed
                    sat = min(1.0, MIN_SATURATION + smoothed_level * (1 - MIN_SATURATION))  # Saturácia nikdy nie je 0
                    val = smoothed_level  # Jas vždy aspoň MIN_BRIGHTNESS
                    color = hsv_to_rgb(hue_offset, sat, val)

                    # Aktualizácia GUI a ESP32
                    hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                    for circle in circles:
                        canvas.itemconfig(circle, fill=hex_color)
                    send_colors(color)

                    # Update flash timer
                    elapsed = time.time() - start_time
                    flash_timer = max(0, flash_timer - elapsed)

                    root.update()
                except Exception as e:
                    print(f"Chyba pri spracovaní zvuku: {e}")
    except Exception as e:
        print(f"Chyba pri inicializácii zvuku: {e}")

# Spustenie spracovania audia
audio_thread = threading.Thread(target=process_audio, daemon=True)
audio_thread.start()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Program ukončený.")