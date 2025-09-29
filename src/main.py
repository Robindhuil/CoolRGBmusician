from microdot import Microdot
from machine import Pin, PWM
import network
import time

# Konfigurácia Wi-Fi
WIFI_SSID = "meno"
WIFI_PASSWORD = "heslo"
STATIC_IP = '192.168.1.100'
SUBNET_MASK = '255.255.255.0'
GATEWAY = '192.168.1.1'
DNS = '8.8.8.8'

# Definovanie pinov pre obe RGB LED
pins = [13, 14, 15, 10, 11, 12]  # LED1: R,G,B; LED2: R,G,B
pwms = [PWM(Pin(pin)) for pin in pins]
STATUS_LED_PIN = "LED"
status_led = Pin(STATUS_LED_PIN, Pin.OUT)

# Nastavenie PWM frekvencie
for pwm in pwms:
    pwm.freq(1000)

# Inicializácia Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Pripojenie na Wi-Fi
def connect_to_wifi():
    print("Connecting to Wi-Fi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    timeout = 10
    start_time = time.time()
    while not wlan.isconnected():
        if time.time() - start_time > timeout:
            print("Failed to connect to Wi-Fi. Retrying...")
            return False
        status_led.on()
        time.sleep(0.3)
        status_led.off()
        time.sleep(0.3)

    wlan.ifconfig((STATIC_IP, SUBNET_MASK, GATEWAY, DNS))
    ip_address = wlan.ifconfig()[0]
    print("Connected to Wi-Fi. IP address:", ip_address)
    status_led.on()
    return ip_address

# Vytvorenie webového servera
app = Microdot()

# Pôvodný endpoint pre jednu LED
@app.route('/set_color/<led_index>/<r>/<g>/<b>')
def set_color(request, led_index, r, g, b):
    try:
        led_index = int(led_index)
        r = int(r)
        g = int(g)
        b = int(b)
        values = [
            65535 - int(r * 65535 / 255),
            65535 - int(g * 65535 / 255),
            65535 - int(b * 65535 / 255)
        ]
        pwms[led_index * 3].duty_u16(values[0])
        pwms[led_index * 3 + 1].duty_u16(values[1])
        pwms[led_index * 3 + 2].duty_u16(values[2])
        return f'LED {led_index} color set to R:{r}, G:{g}, B:{b}'
    except Exception as e:
        print("Error:", e)
        return 'Internal server error', 500

# Nový endpoint pre nastavenie oboch LED naraz
@app.route('/set_colors/<r>/<g>/<b>')
def set_colors(request, r, g, b):
    try:
        r = int(r)
        g = int(g)
        b = int(b)
        values = [
            65535 - int(r * 65535 / 255),
            65535 - int(g * 65535 / 255),
            65535 - int(b * 65535 / 255)
        ]
        # Nastavenie farby pre obe LED
        for led_index in [0, 1]:
            pwms[led_index * 3].duty_u16(values[0])
            pwms[led_index * 3 + 1].duty_u16(values[1])
            pwms[led_index * 3 + 2].duty_u16(values[2])
        return f'Both LEDs set to R:{r}, G:{g}, B:{b}'
    except Exception as e:
        print("Error:", e)
        return 'Internal server error', 500

# Hlavná funkcia
def main():
    while True:
        ip_address = connect_to_wifi()
        if ip_address:
            print("Web server running on http://" + ip_address + ":80")
            try:
                app.run(port=80)
            except Exception as e:
                print(f"Chyba pri spustení servera: {e}")
            break
        else:
            print("Retrying Wi-Fi connection in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    main()
