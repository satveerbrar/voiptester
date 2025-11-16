class LedButtonIO:
    def __init__(self):
        try:
            import RPi.GPIO as GPIO
            self.gpio_enabled = True
            GPIO.setmode(GPIO.BCM)
            # setup pins here later
        except Exception:
            self.gpio_enabled = False
            print("[GPIO] Disabled (running without hardware)")

    def led_idle(self):
        print("[LED] idle")

    def led_busy(self):
        print("[LED] busy")

    def led_success(self):
        print("[LED] success")

    def led_error(self):
        print("[LED] error")

    def read_button_event(self):
        # Placeholder: always waits for Enter key
        input("[Button] Press Enter for SINGLE click")
        return "single"