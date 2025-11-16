class OledDisplay:
    def __init__(self):
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import ssd1306
            from PIL import Image, ImageDraw, ImageFont

            serial = i2c(port=1, address=0x3C)
            self.device = ssd1306(serial)
            self.draw = ImageDraw.Draw
            self.Image = Image
            self.font = ImageFont.load_default()
            self.enabled = True
        except Exception:
            # OLED not connected or libraries missing
            self.device = None
            self.enabled = False
            print("[OLED] Disabled (no hardware)")

    def show_message(self, text: str):
        if not self.enabled:
            print("[OLED]", text)
            return

        image = self.Image.new("1", (self.device.width, self.device.height))
        draw = self.draw(image)
        draw.text((0, 0), text, fill=255, font=self.font)
        self.device.display(image)