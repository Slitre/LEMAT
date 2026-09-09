# =========================================================
# main.py
# =========================================================

import time

import config
import hardware
import ui
import lessons
import hardware_tests
import sensors

from songs import SONGS, NOTES


display = hardware.display


# =========================================================
# MENUS
# =========================================================

MAIN_MENU = [
    "Song List",
    "How to Use",
    "Hardware Test",
    "Sleep"
]

selected_main = 0
selected_song = 0


# =========================================================
# BOOT SCREEN
# =========================================================

def show_boot_screen():

    display.fill(
        config.BACKGROUND
    )


    display.text_center(
        "LEMAT",
        75,
        config.WHITE,
        config.BACKGROUND,
        scale=5
    )


    display.text_center(
        "Learn Easy Music",
        150,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=2
    )


    display.text_center(
        "Any Time",
        185,
        config.GREY,
        config.BACKGROUND,
        scale=2
    )


    display.fill_rect(
        100,
        240,
        280,
        3,
        config.SELECTED
    )


    boot_notes = [
        "C4",
        "D4",
        "E4",
        "F4",
        "G4",
        "A4",
        "B4",
        "C5"
    ]


    for note_name in boot_notes:

        key_index = NOTES[
            note_name
        ]["index"]


        hardware.show_led_for_key(
            key_index
        )


        hardware.play_tone(
            NOTES[
                note_name
            ]["frequency"],
            110
        )


        hardware.leds_off()

        time.sleep_ms(25)


    hardware.speaker_off()

    time.sleep_ms(200)

# =========================================================
# SENSOR INITIALISATION
#
# Failure here does NOT stop LEMAT.
# =========================================================

display.fill(
    config.BACKGROUND
)

display.text_center(
    "Starting sensors...",
    125,
    config.WHITE,
    config.BACKGROUND,
    scale=2
)

display.text_center(
    "Please wait",
    170,
    config.GREY,
    config.BACKGROUND,
    scale=1
)


try:

    sensor_count = sensors.initialise()

    display.fill(
        config.BACKGROUND
    )

    display.text_center(
        "%d / 13 sensors ready"
        % sensor_count,
        135,
        config.WHITE,
        config.BACKGROUND,
        scale=2
    )

    time.sleep_ms(800)


except Exception as e:

    print(
        "Sensor system error:",
        e
    )

    display.fill(
        config.BACKGROUND
    )

    display.text_center(
        "Sensor startup failed",
        125,
        config.YELLOW,
        config.BACKGROUND,
        scale=2
    )

    display.text_center(
        "Continuing anyway",
        170,
        config.GREY,
        config.BACKGROUND,
        scale=1
    )

    time.sleep_ms(800)

# =========================================================
# SONG LIST
# =========================================================


# =========================================================
# SONG ACTION MENU
# =========================================================

def show_song_action_menu(song):

    options = [
        "Start Lesson",
        "Play Song"
    ]

    selected_action = 0

    ui.draw_menu_full(
        song["title"],
        options,
        selected_action,
        True
    )

    # Prevent the RIGHT press used to open this menu from
    # immediately selecting "Start Lesson".
    while (
        hardware.button_up.value() == 0
        or hardware.button_down.value() == 0
        or hardware.button_left.value() == 0
        or hardware.button_right.value() == 0
    ):
        time.sleep_ms(10)

    time.sleep_ms(120)

    while True:

        if hardware.button_pressed(
            hardware.button_up
        ):

            old = selected_action

            selected_action = (
                selected_action - 1
            ) % len(options)

            ui.update_menu_selection(
                options,
                old,
                selected_action
            )

        elif hardware.button_pressed(
            hardware.button_down
        ):

            old = selected_action

            selected_action = (
                selected_action + 1
            ) % len(options)

            ui.update_menu_selection(
                options,
                old,
                selected_action
            )

        elif hardware.button_pressed(
            hardware.button_right
        ):

            if selected_action == 0:

                lessons.start_lesson(
                    song
                )

            else:

                lessons.play_song(
                    song
                )

            ui.draw_menu_full(
                song["title"],
                options,
                selected_action,
                True
            )

        elif hardware.button_pressed(
            hardware.button_left
        ):

            hardware.leds_off()
            hardware.speaker_off()

            return

        time.sleep_ms(10)


def show_song_list():

    global selected_song


    song_titles = [
        song["title"]
        for song in SONGS
    ]


    ui.draw_menu_full(
        "SONG LIST",
        song_titles,
        selected_song,
        True
    )


    while True:

        # UP
        if hardware.button_pressed(
            hardware.button_up
        ):

            old = selected_song

            selected_song = (
                selected_song - 1
            ) % len(SONGS)


            ui.update_menu_selection(
                song_titles,
                old,
                selected_song
            )


        # DOWN
        elif hardware.button_pressed(
            hardware.button_down
        ):

            old = selected_song

            selected_song = (
                selected_song + 1
            ) % len(SONGS)


            ui.update_menu_selection(
                song_titles,
                old,
                selected_song
            )


        # RIGHT = song options
        elif hardware.button_pressed(
            hardware.button_right
        ):

            show_song_action_menu(
                SONGS[selected_song]
            )


            ui.draw_menu_full(
                "SONG LIST",
                song_titles,
                selected_song,
                True
            )


        # LEFT = back
        elif hardware.button_pressed(
            hardware.button_left
        ):

            return


        time.sleep_ms(10)


# =========================================================
# HOW TO USE
# =========================================================

def show_how_to_use():

    display.fill(
        config.BACKGROUND
    )


    ui.draw_header(
        "HOW TO USE",
        True
    )


    display.text(
        "1. Choose a song",
        35,
        90,
        config.WHITE,
        config.BACKGROUND,
        scale=2
    )


    display.text(
        "2. Follow the LEDs",
        35,
        135,
        config.WHITE,
        config.BACKGROUND,
        scale=2
    )


    display.text(
        "3. Play highlighted key",
        35,
        180,
        config.WHITE,
        config.BACKGROUND,
        scale=2
    )


    display.text_center(
        "LEFT to return",
        260,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=1
    )


    while True:

        if hardware.button_pressed(
            hardware.button_left
        ):

            return

        time.sleep_ms(10)


# =========================================================
# SLEEP
# =========================================================

def show_sleep():

    hardware.leds_off()
    hardware.speaker_off()


    display.fill(
        config.BACKGROUND
    )


    display.text_center(
        "LEMAT",
        95,
        config.WHITE,
        config.BACKGROUND,
        scale=4
    )


    display.text_center(
        "Sleeping",
        160,
        config.GREY,
        config.BACKGROUND,
        scale=2
    )


    display.text_center(
        "RIGHT to wake",
        220,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=1
    )


    hardware.screen_off()


    while True:

        if hardware.button_pressed(
            hardware.button_right
        ):

            hardware.screen_on()

            time.sleep_ms(100)

            return


        time.sleep_ms(20)


# =========================================================
# OPEN MAIN MENU ITEM
# =========================================================

def open_main_item():

    item = MAIN_MENU[
        selected_main
    ]


    if item == "Song List":

        show_song_list()


    elif item == "How to Use":

        show_how_to_use()


    elif item == "Hardware Test":

        hardware_tests.show_hardware_menu()


    elif item == "Sleep":

        show_sleep()


# =========================================================
# STARTUP
# =========================================================

hardware.leds_off()
hardware.speaker_off()

show_boot_screen()


ui.draw_menu_full(
    "LEMAT",
    MAIN_MENU,
    selected_main,
    False
)


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    # -----------------------------------------------------
    # UP
    # -----------------------------------------------------

    if hardware.button_pressed(
        hardware.button_up
    ):

        old = selected_main

        selected_main = (
            selected_main - 1
        ) % len(MAIN_MENU)


        ui.update_menu_selection(
            MAIN_MENU,
            old,
            selected_main
        )


    # -----------------------------------------------------
    # DOWN
    # -----------------------------------------------------

    elif hardware.button_pressed(
        hardware.button_down
    ):

        old = selected_main

        selected_main = (
            selected_main + 1
        ) % len(MAIN_MENU)


        ui.update_menu_selection(
            MAIN_MENU,
            old,
            selected_main
        )


    # -----------------------------------------------------
    # RIGHT
    # -----------------------------------------------------

    elif hardware.button_pressed(
        hardware.button_right
    ):

        open_main_item()


        # Returning from a page:
        # redraw main menu once.

        ui.draw_menu_full(
            "LEMAT",
            MAIN_MENU,
            selected_main,
            False
        )

    time.sleep_ms(10)