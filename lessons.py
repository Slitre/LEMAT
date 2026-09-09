# =========================================================
# lessons.py
# =========================================================

import time

import config
import hardware
import ui
import sensors

from songs import NOTES


display = hardware.display


# =========================================================
# FULL LESSON SCREEN
# =========================================================

def draw_lesson_screen_full(
    song,
    note_number,
    note_name
):

    total_notes = len(
        song["notes"]
    )

    key_index = NOTES[
        note_name
    ]["index"]


    display.fill(
        config.BACKGROUND
    )


    # =====================================================
    # HEADER
    # =====================================================

    display.fill_rect(
        0,
        0,
        480,
        58,
        config.HEADER
    )

    display.text(
        song["title"],
        15,
        19,
        config.WHITE,
        config.HEADER,
        scale=2
    )

    display.text(
        "LEFT",
        410,
        12,
        config.GREY,
        config.HEADER,
        scale=1
    )

    display.text(
        "Exit",
        410,
        31,
        config.WHITE,
        config.HEADER,
        scale=1
    )


    # =====================================================
    # NOTE NAME
    # =====================================================

    display.text_center(
        note_name,
        68,
        config.WHITE,
        config.BACKGROUND,
        scale=4
    )


    # =====================================================
    # PIANO GRAPHIC
    # =====================================================

    ui.draw_keyboard(
        key_index
    )


    # =====================================================
    # INSTRUCTION
    # =====================================================

    display.text_center(
        "Play the highlighted key",
        226,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=1
    )


    # =====================================================
    # NOTE COUNTER
    # =====================================================

    progress_text = (
        "Note %d / %d"
        % (
            note_number + 1,
            total_notes
        )
    )

    display.text_center(
        progress_text,
        250,
        config.GREY,
        config.BACKGROUND,
        scale=1
    )


    # =====================================================
    # PROGRESS BAR
    # =====================================================

    bar_width = 380

    completed = (
        bar_width
        * (note_number + 1)
        // total_notes
    )

    display.fill_rect(
        50,
        275,
        bar_width,
        10,
        config.CARD
    )

    display.fill_rect(
        50,
        275,
        completed,
        10,
        config.SELECTED
    )


# =========================================================
# PARTIAL LESSON UPDATE
# =========================================================

def update_lesson_screen(
    song,
    old_note_number,
    old_note_name,
    new_note_number,
    new_note_name
):

    total_notes = len(
        song["notes"]
    )

    old_key_index = NOTES[
        old_note_name
    ]["index"]

    new_key_index = NOTES[
        new_note_name
    ]["index"]


    # =====================================================
    # KEYBOARD
    # =====================================================

    ui.update_keyboard(
        old_key_index,
        new_key_index
    )


    # =====================================================
    # NOTE NAME
    # =====================================================

    display.fill_rect(
        140,
        62,
        200,
        55,
        config.BACKGROUND
    )

    display.text_center(
        new_note_name,
        68,
        config.WHITE,
        config.BACKGROUND,
        scale=4
    )


    # =====================================================
    # NOTE COUNTER
    # =====================================================

    display.fill_rect(
        145,
        244,
        190,
        20,
        config.BACKGROUND
    )

    progress_text = (
        "Note %d / %d"
        % (
            new_note_number + 1,
            total_notes
        )
    )

    display.text_center(
        progress_text,
        250,
        config.GREY,
        config.BACKGROUND,
        scale=1
    )


    # =====================================================
    # PROGRESS BAR
    # =====================================================

    bar_width = 380

    completed = (
        bar_width
        * (new_note_number + 1)
        // total_notes
    )

    display.fill_rect(
        50,
        275,
        bar_width,
        10,
        config.CARD
    )

    display.fill_rect(
        50,
        275,
        completed,
        10,
        config.SELECTED
    )


# =========================================================
# SENSOR STATUS MESSAGE
# =========================================================

def show_sensor_status(text, colour):

    display.fill_rect(
        115,
        228,
        250,
        18,
        config.BACKGROUND
    )

    display.text_center(
        text,
        230,
        colour,
        config.BACKGROUND,
        scale=1
    )


# =========================================================
# WAIT FOR TARGET KEY
# =========================================================

def wait_for_target_key(key_index):

    # Sensor order is reversed relative to musical key order.
    target_sensor_index = 12 - key_index

    # =====================================================
    # ACTIVATE ONLY THE TARGET SENSOR
    # =====================================================

    show_sensor_status(
        "Starting sensor...",
        config.GREY
    )

    if not sensors.activate_only(
        target_sensor_index
    ):

        show_sensor_status(
            "Sensor failed - RIGHT",
            config.YELLOW
        )

        # Manual fallback if a sensor is unavailable.
        while True:

            if hardware.button_pressed(
                hardware.button_left
            ):
                sensors.deactivate()
                return False

            if hardware.button_pressed(
                hardware.button_right
            ):
                sensors.deactivate()
                return True

            time.sleep_ms(10)

    # =====================================================
    # IDLE CALIBRATION - TARGET SENSOR ONLY
    # =====================================================

    show_sensor_status(
        "Release key...",
        config.GREY
    )

    time.sleep_ms(300)

    show_sensor_status(
        "Calibrating...",
        config.GREY
    )

    baseline = sensors.get_baseline(
        target_sensor_index
    )

    if baseline is None:

        sensors.deactivate()

        show_sensor_status(
            "Calibration failed",
            config.YELLOW
        )

        return False

    confirm_state = 0

    show_sensor_status(
        "Ready - play key",
        config.GREEN
    )

    # =====================================================
    # WAIT FOR CORRECT KEY
    # =====================================================

    while True:

        if hardware.button_pressed(
            hardware.button_left
        ):
            sensors.deactivate()
            return False

        # Keep RIGHT as the existing manual/demo fallback.
        if hardware.button_pressed(
            hardware.button_right
        ):
            sensors.deactivate()
            return True

        pressed, confirm_state, current = (
            sensors.key_pressed(
                target_sensor_index,
                baseline,
                confirm_state
            )
        )

        if current is not None:

            print(
                "Sensor",
                target_sensor_index + 1,
                "baseline",
                baseline,
                "current",
                current,
                "movement",
                current - baseline
            )

        if pressed:

            show_sensor_status(
                "Correct!",
                config.GREEN
            )

            sensors.deactivate()
            return True

        time.sleep_ms(5)



# =========================================================
# LESSON COMPLETE
# =========================================================

def lesson_complete(song):

    hardware.leds_off()
    hardware.speaker_off()

    display.fill(
        config.BACKGROUND
    )


    display.text_center(
        "LESSON COMPLETE!",
        65,
        config.WHITE,
        config.BACKGROUND,
        scale=3
    )

    display.text_center(
        song["title"],
        130,
        config.LIGHT_BLUE,
        config.BACKGROUND,
        scale=2
    )

    display.text_center(
        "Great job!",
        180,
        config.GREEN,
        config.BACKGROUND,
        scale=2
    )

    display.text_center(
        "LEFT to return",
        250,
        config.GREY,
        config.BACKGROUND,
        scale=1
    )


    # =====================================================
    # LED CELEBRATION
    # =====================================================

    for frame in range(6):

        for i in range(
            config.NUM_LEDS
        ):

            hue = (
                i * 256
                // config.NUM_LEDS
                + frame * 25
            )

            hardware.np[i] = (
                hardware.wheel(hue)
            )

        hardware.np.write()

        time.sleep_ms(160)


    hardware.leds_off()


    while True:

        if hardware.button_pressed(
            hardware.button_left
        ):

            return

        time.sleep_ms(10)


# =========================================================
# START LESSON
# =========================================================


# =========================================================
# PLAY FULL SONG
# =========================================================

def play_song(song):

    hardware.leds_off()
    hardware.speaker_off()

    notes = song["notes"]

    if len(notes) == 0:
        return

    tempo = song.get("tempo", 100)

    # Duration of one beat in milliseconds.
    beat_ms = int(
        60000 / tempo
    )

    for note_name, beats in notes:

        note = NOTES[
            note_name
        ]

        key_index = note[
            "index"
        ]

        frequency = note[
            "frequency"
        ]

        duration_ms = int(
            beat_ms * beats
        )

        hardware.show_led_for_key(
            key_index
        )

        hardware.play_tone(
            frequency,
            duration_ms
        )

        hardware.leds_off()

        # Small separation between notes.
        time.sleep_ms(40)

    hardware.leds_off()
    hardware.speaker_off()


def start_lesson(song):

    hardware.leds_off()
    hardware.speaker_off()


    notes = song["notes"]

    if len(notes) == 0:
        return


    # =====================================================
    # FIRST NOTE
    # =====================================================

    first_note_name = (
        notes[0][0]
    )

    draw_lesson_screen_full(
        song,
        0,
        first_note_name
    )


    # =====================================================
    # LESSON LOOP
    # =====================================================

    for note_number, note_data in enumerate(
        notes
    ):

        note_name = note_data[0]

        note = NOTES[
            note_name
        ]

        key_index = note[
            "index"
        ]

        frequency = note[
            "frequency"
        ]


        # =================================================
        # PARTIAL SCREEN UPDATE
        # =================================================

        if note_number > 0:

            old_note_name = (
                notes[
                    note_number - 1
                ][0]
            )

            update_lesson_screen(
                song,
                note_number - 1,
                old_note_name,
                note_number,
                note_name
            )


        # =================================================
        # LIGHT ONLY TARGET LED
        # =================================================

        hardware.show_led_for_key(
            key_index
        )

        # Play the note when it is presented to the learner.
        hardware.play_tone(
            frequency,
            1000
        )


        # =================================================
        # READ ONLY TARGET SENSOR
        # =================================================

        correct = wait_for_target_key(
            key_index
        )


        if not correct:

            hardware.leds_off()
            hardware.speaker_off()

            return


        # =================================================
        # CORRECT NOTE FEEDBACK
        # =================================================

        hardware.leds_off()

        time.sleep_ms(100)


    # =====================================================
    # COMPLETE
    # =====================================================

    lesson_complete(
        song
    )