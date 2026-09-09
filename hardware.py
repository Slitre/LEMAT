# =========================================================
# hardware.py
# =========================================================

from machine import Pin, SPI, PWM
from ili9488 import ILI9488
import neopixel
import time

import config


# =========================================================
# TFT
# =========================================================

tft_backlight = Pin(
    config.PIN_TFT_BACKLIGHT,
    Pin.OUT
)

tft_backlight.value(1)

time.sleep_ms(100)


spi = SPI(
    1,
    baudrate=config.SPI_BAUDRATE,
    polarity=0,
    phase=0,
    sck=Pin(config.PIN_TFT_SCK),
    mosi=Pin(config.PIN_TFT_MOSI)
)


display = ILI9488(
    spi,
    Pin(
        config.PIN_TFT_CS,
        Pin.OUT,
        value=1
    ),
    Pin(
        config.PIN_TFT_DC,
        Pin.OUT,
        value=1
    ),
    Pin(
        config.PIN_TFT_RESET,
        Pin.OUT,
        value=1
    )
)


# =========================================================
# BUTTONS
# =========================================================

button_up = Pin(
    config.PIN_UP,
    Pin.IN,
    Pin.PULL_UP
)

button_down = Pin(
    config.PIN_DOWN,
    Pin.IN,
    Pin.PULL_UP
)

button_left = Pin(
    config.PIN_LEFT,
    Pin.IN,
    Pin.PULL_UP
)

button_right = Pin(
    config.PIN_RIGHT,
    Pin.IN,
    Pin.PULL_UP
)


def button_pressed(button):

    if button.value() == 0:

        time.sleep_ms(25)

        if button.value() == 0:

            while button.value() == 0:
                time.sleep_ms(10)

            return True

    return False


# =========================================================
# WS2812 LEDs
# =========================================================

np = neopixel.NeoPixel(
    Pin(config.PIN_LED),
    config.NUM_LEDS
)


def wheel(pos):

    pos %= 256

    if pos < 85:

        r = 255 - pos * 3
        g = pos * 3
        b = 0

    elif pos < 170:

        pos -= 85

        r = 0
        g = 255 - pos * 3
        b = pos * 3

    else:

        pos -= 170

        r = pos * 3
        g = 0
        b = 255 - pos * 3

    return (
        int(r * config.LED_BRIGHTNESS),
        int(g * config.LED_BRIGHTNESS),
        int(b * config.LED_BRIGHTNESS)
    )


def leds_off():

    for i in range(config.NUM_LEDS):
        np[i] = (0, 0, 0)

    np.write()


def show_single_led(index, colour):

    # LEDs are physically wired in reverse order.
    physical_index = (
        config.NUM_LEDS - 1 - index
    )

    for i in range(config.NUM_LEDS):

        if i == physical_index:
            np[i] = colour
        else:
            np[i] = (0, 0, 0)

    np.write()


def show_led_for_key(index):

    hue = (
        index
        * 256
        // config.NUM_LEDS
    )

    show_single_led(
        index,
        wheel(hue)
    )




# =========================================================
# SPEAKER
# =========================================================

speaker_pwm = PWM(
    Pin(config.PIN_SPEAKER_PWM)
)

speaker_pwm.duty_u16(0)


speaker_sd = Pin(
    config.PIN_SPEAKER_SD,
    Pin.OUT
)

speaker_sd.value(0)


SPEAKER_DUTY = int(
    65535 * config.SPEAKER_VOLUME
)


def play_tone(frequency, duration_ms=120):

    speaker_sd.value(1)

    speaker_pwm.freq(
        int(frequency)
    )

    speaker_pwm.duty_u16(
        SPEAKER_DUTY
    )

    time.sleep_ms(duration_ms)

    speaker_pwm.duty_u16(0)


def speaker_off():

    speaker_pwm.duty_u16(0)
    speaker_sd.value(0)


# =========================================================
# POWER / DISPLAY HELPERS
# =========================================================

def screen_on():

    tft_backlight.value(1)


def screen_off():

    tft_backlight.value(0)