# =========================================================
# ui.py
# =========================================================

import config
import hardware


display = hardware.display


# =========================================================
# GENERIC HEADER
# =========================================================

def draw_header(title, show_back=True):

    display.fill_rect(
        0,
        0,
        480,
        58,
        config.HEADER
    )

    display.text(
        title,
        20,
        16,
        config.WHITE,
        config.HEADER,
        scale=3
    )

    if show_back:

        display.text(
            "LEFT",
            410,
            12,
            config.GREY,
            config.HEADER,
            scale=1
        )

        display.text(
            "Back",
            410,
            31,
            config.WHITE,
            config.HEADER,
            scale=1
        )


# =========================================================
# GENERIC FOOTER
# =========================================================

def draw_menu_footer():

    display.fill_rect(
        0,
        286,
        480,
        34,
        config.HEADER
    )

    display.text(
        "UP/DOWN",
        15,
        298,
        config.GREY,
        config.HEADER,
        scale=1
    )

    display.text(
        "Navigate",
        90,
        298,
        config.WHITE,
        config.HEADER,
        scale=1
    )

    display.text(
        "RIGHT",
        290,
        298,
        config.GREY,
        config.HEADER,
        scale=1
    )

    display.text(
        "Open",
        355,
        298,
        config.WHITE,
        config.HEADER,
        scale=1
    )


# =========================================================
# GENERIC MENU CARD
# =========================================================

def draw_menu_item(
    index,
    text,
    selected,
    start_y=75,
    spacing=49,
    height=40
):

    x = 35
    y = start_y + index * spacing

    width = 410

    if selected:

        bg = config.SELECTED
        colour = config.WHITE

        display.fill_rect(
            x,
            y,
            width,
            height,
            bg
        )

        display.fill_rect(
            x,
            y,
            6,
            height,
            config.WHITE
        )

        display.text(
            ">",
            x + 20,
            y + 9,
            config.WHITE,
            bg,
            scale=2
        )

    else:

        bg = config.CARD
        colour = config.GREY

        display.fill_rect(
            x,
            y,
            width,
            height,
            bg
        )

        display.fill_rect(
            x + 6,
            y,
            42,
            height,
            bg
        )

    display.text(
        text,
        x + 55,
        y + 11,
        colour,
        bg,
        scale=2
    )


# =========================================================
# FULL GENERIC MENU
# =========================================================

def draw_menu_full(
    title,
    items,
    selected,
    show_back=True
):

    display.fill(
        config.BACKGROUND
    )

    draw_header(
        title,
        show_back
    )

    for index, item in enumerate(items):

        draw_menu_item(
            index,
            item,
            index == selected
        )

    draw_menu_footer()


# =========================================================
# PARTIAL MENU UPDATE
# =========================================================

def update_menu_selection(
    items,
    old_index,
    new_index
):

    draw_menu_item(
        old_index,
        items[old_index],
        False
    )

    draw_menu_item(
        new_index,
        items[new_index],
        True
    )


# =========================================================
# PIANO CONFIGURATION
# =========================================================

KEYBOARD_X = 44
KEYBOARD_Y = 140

WHITE_WIDTH = 49
WHITE_HEIGHT = 82

BLACK_WIDTH = 28
BLACK_HEIGHT = 48


# Physical index -> white-key position
WHITE_KEY_MAP = {

    0: 0,     # C4
    2: 1,     # D4
    4: 2,     # E4
    5: 3,     # F4
    7: 4,     # G4
    9: 5,     # A4
    11: 6,    # B4
    12: 7     # C5
}


WHITE_KEY_LABELS = {

    0: "C",
    2: "D",
    4: "E",
    5: "F",
    7: "G",
    9: "A",
    11: "B",
    12: "C"
}


# Physical index -> white-key boundary
BLACK_KEY_MAP = {

    1: 1,     # C#4
    3: 2,     # D#4
    6: 4,     # F#4
    8: 5,     # G#4
    10: 6     # A#4
}


# =========================================================
# DRAW ONE WHITE KEY
# =========================================================

def draw_white_key(
    physical_index,
    active=False
):

    position = WHITE_KEY_MAP[
        physical_index
    ]

    x = (
        KEYBOARD_X
        + position * WHITE_WIDTH
    )


    if active:

        fill_colour = config.SELECTED
        text_colour = config.WHITE

    else:

        fill_colour = config.WHITE
        text_colour = config.BACKGROUND


    display.fill_rect(
        x,
        KEYBOARD_Y,
        WHITE_WIDTH - 1,
        WHITE_HEIGHT,
        fill_colour
    )


    display.rect(
        x,
        KEYBOARD_Y,
        WHITE_WIDTH - 1,
        WHITE_HEIGHT,
        config.BACKGROUND
    )


    display.text(
        WHITE_KEY_LABELS[
            physical_index
        ],
        x + 20,
        KEYBOARD_Y + 61,
        text_colour,
        fill_colour,
        scale=1
    )


# =========================================================
# DRAW ONE BLACK KEY
# =========================================================

def draw_black_key(
    physical_index,
    active=False
):

    boundary = BLACK_KEY_MAP[
        physical_index
    ]


    x = (
        KEYBOARD_X
        + boundary * WHITE_WIDTH
        - BLACK_WIDTH // 2
    )


    if active:

        fill_colour = config.SELECTED

    else:

        fill_colour = config.BACKGROUND


    display.fill_rect(
        x,
        KEYBOARD_Y,
        BLACK_WIDTH,
        BLACK_HEIGHT,
        fill_colour
    )


    if active:

        display.rect(
            x,
            KEYBOARD_Y,
            BLACK_WIDTH,
            BLACK_HEIGHT,
            config.LIGHT_BLUE
        )

        display.rect(
            x + 1,
            KEYBOARD_Y + 1,
            BLACK_WIDTH - 2,
            BLACK_HEIGHT - 2,
            config.LIGHT_BLUE
        )


# =========================================================
# REDRAW ALL BLACK KEYS
#
# Needed after changing a white key because black keys
# visually overlap the white keys.
# =========================================================

def redraw_black_keys(active_index=None):

    for physical_index in BLACK_KEY_MAP:

        draw_black_key(
            physical_index,
            physical_index == active_index
        )


# =========================================================
# DRAW COMPLETE PIANO
# =========================================================

def draw_keyboard(active_index):

    # White keys first
    for physical_index in WHITE_KEY_MAP:

        draw_white_key(
            physical_index,
            physical_index == active_index
        )


    # Black keys on top
    redraw_black_keys(
        active_index
    )


# =========================================================
# PARTIAL PIANO KEY UPDATE
#
# Only old + new keys are changed.
# =========================================================

def update_keyboard(
    old_index,
    new_index
):

    if old_index == new_index:
        return


    # -----------------------------------------------------
    # REMOVE OLD HIGHLIGHT
    # -----------------------------------------------------

    if old_index in WHITE_KEY_MAP:

        draw_white_key(
            old_index,
            False
        )

        # White redraw may cover black keys,
        # so restore black keys.
        redraw_black_keys(
            new_index
        )

    else:

        draw_black_key(
            old_index,
            False
        )


    # -----------------------------------------------------
    # ADD NEW HIGHLIGHT
    # -----------------------------------------------------

    if new_index in WHITE_KEY_MAP:

        draw_white_key(
            new_index,
            True
        )

        # Restore black keys over white key.
        redraw_black_keys(
            new_index
        )

    else:

        draw_black_key(
            new_index,
            True
        )