# =========================================================
# hardware_tests.py
# =========================================================

import time

import config
import hardware
import ui
import sensors

from songs import NOTES


display = hardware.display


# =========================================================
# HARDWARE TEST MENU
# =========================================================

HARDWARE_MENU = [
    "LED Test",
    "Sensor Test",
    "Speaker Test"
]

selected_hardware = 0


# =========================================================
# CLEAR PAGE
# =========================================================

def clear_page():

    display.fill(
        config.BACKGROUND
    )


# =========================================================
# LED TEST
# =========================================================

def led_test():

    hardware.leds_off()

    clear_page()

    ui.draw_header(
        "LED TEST",
        True
    )


    while True:

        for i in range(
            config.NUM_LEDS
        ):

            if hardware.button_pressed(
                hardware.button_left
            ):

                hardware.leds_off()
                return


            hardware.show_led_for_key(
                i
            )


            display.fill_rect(
                0,
                65,
                480,
                215,
                config.BACKGROUND
            )


            display.text_center(
                "Testing LED",
                90,
                config.GREY,
                config.BACKGROUND,
                scale=2
            )


            display.text_center(
                str(i + 1),
                135,
                config.WHITE,
                config.BACKGROUND,
                scale=6
            )


            display.text_center(
                "of 13",
                210,
                config.LIGHT_BLUE,
                config.BACKGROUND,
                scale=2
            )


            time.sleep_ms(350)


        hardware.leds_off()


        display.fill_rect(
            0,
            65,
            480,
            215,
            config.BACKGROUND
        )


        display.text_center(
            "LED TEST COMPLETE",
            115,
            config.GREEN,
            config.BACKGROUND,
            scale=2
        )


        display.text_center(
            "RIGHT = Again",
            175,
            config.WHITE,
            config.BACKGROUND,
            scale=1
        )


        display.text_center(
            "LEFT = Back",
            210,
            config.GREY,
            config.BACKGROUND,
            scale=1
        )


        while True:

            if hardware.button_pressed(
                hardware.button_left
            ):

                return


            if hardware.button_pressed(
                hardware.button_right
            ):

                break


            time.sleep_ms(10)


# =========================================================
# SENSOR -> NOTE NAME
#
# Remember sensor order is reversed.
# =========================================================

SENSOR_NOTE_NAMES = [
    "C5",     # Sensor 1
    "B4",     # Sensor 2
    "A#4",    # Sensor 3
    "A4",     # Sensor 4
    "G#4",    # Sensor 5
    "G4",     # Sensor 6
    "F#4",    # Sensor 7
    "F4",     # Sensor 8
    "E4",     # Sensor 9
    "D#4",    # Sensor 10
    "D4",     # Sensor 11
    "C#4",    # Sensor 12
    "C4"      # Sensor 13
]


# =========================================================
# SENSOR SELECTION SCREEN
# =========================================================

def draw_sensor_selection(
    selected_sensor
):

    clear_page()


    ui.draw_header(
        "SENSOR TEST",
        True
    )


    display.text_center(
        "Select Sensor",
        82,
        config.GREY,
        config.BACKGROUND,
        scale=2
    )


    # Sensor number
    display.text_center(
        "Sensor %d"
        % (selected_sensor + 1),
        125,
        config.WHITE,
        config.BACKGROUND,
        scale=3
    )


    # Musical note
    display.text_center(
        SENSOR_NOTE_NAMES[
            selected_sensor
        ],
        180,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=3
    )


    display.text_center(
        "UP/DOWN  Select",
        235,
        config.GREY,
        config.BACKGROUND,
        scale=1
    )


    display.text_center(
        "RIGHT  Start Test",
        260,
        config.WHITE,
        config.BACKGROUND,
        scale=1
    )


# =========================================================
# PARTIAL SENSOR SELECTION UPDATE
# =========================================================

def update_sensor_selection(
    selected_sensor
):

    # Clear only changing centre region
    display.fill_rect(
        100,
        110,
        280,
        110,
        config.BACKGROUND
    )


    display.text_center(
        "Sensor %d"
        % (selected_sensor + 1),
        125,
        config.WHITE,
        config.BACKGROUND,
        scale=3
    )


    display.text_center(
        SENSOR_NOTE_NAMES[
            selected_sensor
        ],
        180,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=3
    )


# =========================================================
# LIVE SINGLE SENSOR TEST
# =========================================================

def run_single_sensor_test(
    sensor_index
):

    clear_page()


    ui.draw_header(
        "SENSOR TEST",
        True
    )


    display.text_center(
        "Sensor %d"
        % (sensor_index + 1),
        75,
        config.WHITE,
        config.BACKGROUND,
        scale=2
    )


    display.text_center(
        SENSOR_NOTE_NAMES[
            sensor_index
        ],
        105,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=2
    )


    # =====================================================
    # SELECT THIS SENSOR FOR RANGING
    # =====================================================

    display.text_center(
        "Starting...",
        160,
        config.GREY,
        config.BACKGROUND,
        scale=2
    )


    success = sensors.activate_only(
        sensor_index
    )


    # Clear status region
    display.fill_rect(
        0,
        135,
        480,
        130,
        config.BACKGROUND
    )


    if not success:

        display.text_center(
            "SENSOR FAILED",
            155,
            config.RED,
            config.BACKGROUND,
            scale=2
        )


        display.text_center(
            "LEFT to return",
            220,
            config.GREY,
            config.BACKGROUND,
            scale=1
        )


        while True:

            if hardware.button_pressed(
                hardware.button_left
            ):

                sensors.deactivate()

                return


            time.sleep_ms(10)


    # =====================================================
    # LIVE READINGS
    # =====================================================

    last_distance = None


    while True:

        # LEFT = return to selector
        if hardware.button_pressed(
            hardware.button_left
        ):

            sensors.deactivate()

            return


        distance = sensors.read_stable(
            sensor_index
        )


        if distance is not None:

            # Only redraw when number actually changes
            if distance != last_distance:

                display.fill_rect(
                    110,
                    140,
                    260,
                    75,
                    config.BACKGROUND
                )


                display.text_center(
                    "%d mm" % distance,
                    145,
                    config.WHITE,
                    config.BACKGROUND,
                    scale=5
                )


                if sensors.get_status(sensor_index) == "OK":

                    display.text_center(
                        "OK",
                        205,
                        config.GREEN,
                        config.BACKGROUND,
                        scale=1
                    )

                else:

                    display.text_center(
                        sensors.get_status(sensor_index),
                        205,
                        config.YELLOW,
                        config.BACKGROUND,
                        scale=1
                    )


                last_distance = (
                    distance
                )


        else:

            display.fill_rect(
                110,
                140,
                260,
                75,
                config.BACKGROUND
            )


            display.text_center(
                "NO READING",
                165,
                config.RED,
                config.BACKGROUND,
                scale=2
            )


        display.text_center(
            "LEFT to return",
            260,
            config.GREY,
            config.BACKGROUND,
            scale=1
        )


        time.sleep_ms(20)


# =========================================================
# SENSOR TEST MENU
# =========================================================

def sensor_test():

    selected_sensor = 12

    # Start at Sensor 13 because that's your low C.

    draw_sensor_selection(
        selected_sensor
    )


    while True:

        # =================================================
        # UP
        # =================================================

        if hardware.button_pressed(
            hardware.button_up
        ):

            selected_sensor = (
                selected_sensor - 1
            ) % 13


            update_sensor_selection(
                selected_sensor
            )


        # =================================================
        # DOWN
        # =================================================

        elif hardware.button_pressed(
            hardware.button_down
        ):

            selected_sensor = (
                selected_sensor + 1
            ) % 13


            update_sensor_selection(
                selected_sensor
            )


        # =================================================
        # RIGHT = TEST THIS SENSOR
        # =================================================

        elif hardware.button_pressed(
            hardware.button_right
        ):

            run_single_sensor_test(
                selected_sensor
            )


            # Returning from live test
            draw_sensor_selection(
                selected_sensor
            )


        # =================================================
        # LEFT = HARDWARE MENU
        # =================================================

        elif hardware.button_pressed(
            hardware.button_left
        ):

            sensors.deactivate()

            return


        time.sleep_ms(10)


# =========================================================
# SPEAKER TEST
# =========================================================

def speaker_test():

    hardware.speaker_off()

    clear_page()


    ui.draw_header(
        "SPEAKER TEST",
        True
    )


    display.text_center(
        "RIGHT to play scale",
        130,
        config.WHITE,
        config.BACKGROUND,
        scale=2
    )


    display.text_center(
        "LEFT to return",
        220,
        config.GREY,
        config.BACKGROUND,
        scale=1
    )


    scale = [
        "C4",
        "D4",
        "E4",
        "F4",
        "G4",
        "A4",
        "B4",
        "C5"
    ]


    while True:

        if hardware.button_pressed(
            hardware.button_left
        ):

            hardware.speaker_off()
            hardware.leds_off()

            return


        if hardware.button_pressed(
            hardware.button_right
        ):

            for note_name in scale:

                note = NOTES[
                    note_name
                ]


                hardware.show_led_for_key(
                    note["index"]
                )


                hardware.play_tone(
                    note["frequency"],
                    180
                )


                hardware.leds_off()

                time.sleep_ms(40)


        time.sleep_ms(10)


# =========================================================
# HARDWARE SUBMENU
# =========================================================

def show_hardware_menu():

    global selected_hardware


    ui.draw_menu_full(
        "HARDWARE TEST",
        HARDWARE_MENU,
        selected_hardware,
        True
    )


    while True:

        # UP
        if hardware.button_pressed(
            hardware.button_up
        ):

            old = selected_hardware


            selected_hardware = (
                selected_hardware - 1
            ) % len(HARDWARE_MENU)


            ui.update_menu_selection(
                HARDWARE_MENU,
                old,
                selected_hardware
            )


        # DOWN
        elif hardware.button_pressed(
            hardware.button_down
        ):

            old = selected_hardware


            selected_hardware = (
                selected_hardware + 1
            ) % len(HARDWARE_MENU)


            ui.update_menu_selection(
                HARDWARE_MENU,
                old,
                selected_hardware
            )


        # RIGHT
        elif hardware.button_pressed(
            hardware.button_right
        ):

            item = HARDWARE_MENU[
                selected_hardware
            ]


            if item == "LED Test":

                led_test()


            elif item == "Sensor Test":

                sensor_test()


            elif item == "Speaker Test":

                speaker_test()


            # Full redraw when returning from another page.
            ui.draw_menu_full(
                "HARDWARE TEST",
                HARDWARE_MENU,
                selected_hardware,
                True
            )


        # LEFT
        elif hardware.button_pressed(
            hardware.button_left
        ):

            sensors.deactivate()

            hardware.leds_off()
            hardware.speaker_off()

            return


        time.sleep_ms(10)