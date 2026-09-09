from machine import Pin
import framebuf
import time


class ILI9488:
    """
    Small, direct-draw MicroPython driver for an ILI9488 SPI TFT.

    Designed for the RP2040 without allocating a full 480x320 framebuffer.
    Drawing commands are sent directly to the TFT's GRAM.

    Colour format:
        (R, G, B), each 0..255

    Supported helpers:
        fill()
        fill_rect()
        hline()
        vline()
        rect()
        text()
        text_center()
        sleep()
    """

    WIDTH = 480
    HEIGHT = 320

    def __init__(self, spi, cs, dc, rst):
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst

        self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=1)
        self.rst.init(Pin.OUT, value=1)

        self._reset()
        self._init_display()

    # ---------------------------------------------------------
    # LOW-LEVEL CONTROL
    # ---------------------------------------------------------

    def _reset(self):
        self.rst.value(1)
        time.sleep_ms(10)
        self.rst.value(0)
        time.sleep_ms(20)
        self.rst.value(1)
        time.sleep_ms(150)

    def _command(self, command, data=None):
        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(bytes((command,)))

        if data is not None:
            self.dc.value(1)
            self.spi.write(data)

        self.cs.value(1)

    def _init_display(self):
        self._command(0x01)               # Software reset
        time.sleep_ms(150)

        self._command(0x11)               # Sleep out
        time.sleep_ms(150)

        # ILI9488 SPI interface normally uses 18-bit / 3-byte colour.
        self._command(0x3A, b"\x66")

        # Landscape orientation, BGR.
        # If the image is mirrored/rotated on your particular panel,
        # this is the byte to change.
        self._command(0x36, b"\xE8")

        self._command(0xB1, b"\xB0")
        self._command(0xB4, b"\x02")
        self._command(0xB6, b"\x02\x02")
        self._command(0xC0, b"\x17\x15")
        self._command(0xC1, b"\x41")
        self._command(0xC5, b"\x00\x12\x80")

        self._command(
            0xE0,
            bytes((
                0x00, 0x07, 0x0F, 0x0D, 0x1B,
                0x0A, 0x3C, 0x78, 0x4A, 0x07,
                0x0E, 0x09, 0x1B, 0x1E, 0x0F
            ))
        )

        self._command(
            0xE1,
            bytes((
                0x00, 0x22, 0x24, 0x06, 0x12,
                0x07, 0x36, 0x47, 0x47, 0x06,
                0x0A, 0x07, 0x30, 0x37, 0x0F
            ))
        )

        self._command(0x29)               # Display on
        time.sleep_ms(50)

    def _set_window(self, x0, y0, x1, y1):
        self._command(
            0x2A,
            bytes((
                (x0 >> 8) & 0xFF,
                x0 & 0xFF,
                (x1 >> 8) & 0xFF,
                x1 & 0xFF
            ))
        )

        self._command(
            0x2B,
            bytes((
                (y0 >> 8) & 0xFF,
                y0 & 0xFF,
                (y1 >> 8) & 0xFF,
                y1 & 0xFF
            ))
        )

        self.cs.value(0)
        self.dc.value(0)
        self.spi.write(b"\x2C")
        self.dc.value(1)

    def _end_write(self):
        self.cs.value(1)

    # ---------------------------------------------------------
    # BASIC DRAWING
    # ---------------------------------------------------------

    def fill_rect(self, x, y, width, height, colour):
        if width <= 0 or height <= 0:
            return

        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.WIDTH - 1, x + width - 1)
        y1 = min(self.HEIGHT - 1, y + height - 1)

        if x0 > x1 or y0 > y1:
            return

        self._set_window(x0, y0, x1, y1)

        pixel = bytes((
            colour[0] & 0xFF,
            colour[1] & 0xFF,
            colour[2] & 0xFF
        ))

        total_pixels = (x1 - x0 + 1) * (y1 - y0 + 1)

        # Chunk the transfer so we don't allocate a huge temporary object.
        chunk_pixels = 256
        chunk = pixel * chunk_pixels

        while total_pixels >= chunk_pixels:
            self.spi.write(chunk)
            total_pixels -= chunk_pixels

        if total_pixels:
            self.spi.write(pixel * total_pixels)

        self._end_write()

    def fill(self, colour):
        self.fill_rect(0, 0, self.WIDTH, self.HEIGHT, colour)

    def hline(self, x, y, width, colour):
        self.fill_rect(x, y, width, 1, colour)

    def vline(self, x, y, height, colour):
        self.fill_rect(x, y, 1, height, colour)

    def rect(self, x, y, width, height, colour):
        self.hline(x, y, width, colour)
        self.hline(x, y + height - 1, width, colour)
        self.vline(x, y, height, colour)
        self.vline(x + width - 1, y, height, colour)

    # ---------------------------------------------------------
    # TEXT
    # ---------------------------------------------------------

    def _draw_character(self, char, x, y, fg, bg, scale):
        """
        Draw one 8x8 MicroPython framebuf character directly to the TFT.
        Background is drawn first, then horizontal runs of foreground pixels.
        """

        mono = bytearray(8)
        fb = framebuf.FrameBuffer(mono, 8, 8, framebuf.MONO_VLSB)
        fb.fill(0)
        fb.text(char, 0, 0, 1)

        self.fill_rect(
            x,
            y,
            8 * scale,
            8 * scale,
            bg
        )

        for row in range(8):
            run_start = -1

            for col in range(9):
                pixel_on = False

                if col < 8:
                    pixel_on = fb.pixel(col, row) != 0

                if pixel_on and run_start < 0:
                    run_start = col

                if not pixel_on and run_start >= 0:
                    run_width = col - run_start

                    self.fill_rect(
                        x + run_start * scale,
                        y + row * scale,
                        run_width * scale,
                        scale,
                        fg
                    )

                    run_start = -1

    def text(self, text, x, y, fg, bg, scale=1):
        cursor_x = x

        for char in str(text):
            self._draw_character(
                char,
                cursor_x,
                y,
                fg,
                bg,
                scale
            )

            cursor_x += 8 * scale

    def text_center(self, text, y, fg, bg, scale=1):
        width = len(str(text)) * 8 * scale
        x = (self.WIDTH - width) // 2
        self.text(text, x, y, fg, bg, scale)

    # ---------------------------------------------------------
    # POWER
    # ---------------------------------------------------------

    def sleep(self, enabled=True):
        if enabled:
            self._command(0x28)  # Display off
            self._command(0x10)  # Sleep in
            time.sleep_ms(120)
        else:
            self._command(0x11)  # Sleep out
            time.sleep_ms(120)
            self._command(0x29)  # Display o