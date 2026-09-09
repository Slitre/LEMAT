# =========================================================
# sensors.py
#
# 13 x VL53L1X
#
# IMPORTANT:
# Only ONE sensor is powered/ranging at a time.
#
# This avoids optical interference between the 13 sensors.
# =========================================================

from machine import Pin, I2C
from vl53l1x import VL53L1X
import time


# =========================================================
# CONFIGURATION
# =========================================================

NUM_SENSORS = 13


# =========================================================
# I2C
#
# SDA = GPIO0
# SCL = GPIO1
# =========================================================

i2c = I2C(
    0,
    sda=Pin(0),
    scl=Pin(1),
    freq=400_000
)


# =========================================================
# XSHUT MAPPING
#
# Sensor 1  -> GPIO29
# Sensor 2  -> GPIO28
# ...
# Sensor 13 -> GPIO17
#
# Physical musical mapping is reversed:
#
# Sensor 13 = C4
# Sensor 12 = C#4
# ...
# Sensor 1  = C5
# =========================================================

XSHUT_PINS = [
    29,     # Sensor 1
    28,     # Sensor 2
    27,     # Sensor 3
    26,     # Sensor 4
    25,     # Sensor 5
    24,     # Sensor 6
    23,     # Sensor 7
    22,     # Sensor 8
    21,     # Sensor 9
    20,     # Sensor 10
    19,     # Sensor 11
    18,     # Sensor 12
    17      # Sensor 13
]


# =========================================================
# PRESS DETECTION
#
# Distance INCREASES when your piano key is pressed.
# =========================================================

PRESS_MOVEMENT_MM = 4

PRESS_CONFIRM_COUNT = 2


# =========================================================
# FILTER
#
# New driver is already fairly stable.
# =========================================================

FILTER_SAMPLES = 3


# =========================================================
# XSHUT OBJECTS
# =========================================================

xshut = []

for gpio in XSHUT_PINS:

    pin = Pin(
        gpio,
        Pin.OUT
    )

    pin.value(0)

    xshut.append(pin)


# =========================================================
# CURRENTLY ACTIVE SENSOR
# =========================================================

active_sensor = None
active_index = None


# =========================================================
# INITIALISE SENSOR SYSTEM
#
# We NO LONGER initialise all 13 sensors here.
#
# We simply ensure they're all powered down.
# Each sensor is initialised only when required.
# =========================================================

def initialise():

    global active_sensor
    global active_index

    print()
    print("==============================")
    print("VL53L1X SENSOR SYSTEM")
    print("Single-sensor XSHUT mode")
    print("==============================")

    for pin in xshut:
        pin.value(0)

    active_sensor = None
    active_index = None

    time.sleep_ms(200)

    print("All sensors standby")
    print("Only one sensor wakes at a time")
    print("==============================")
    print()

    return NUM_SENSORS


# =========================================================
# TURN EVERYTHING OFF
# =========================================================

def deactivate():

    global active_sensor
    global active_index

    for pin in xshut:
        pin.value(0)

    active_sensor = None
    active_index = None

    time.sleep_ms(30)



# =========================================================
# ACTIVATE ONE SENSOR ONLY
# =========================================================

def activate_only(index):

    global active_sensor
    global active_index

    if index < 0 or index >= NUM_SENSORS:
        return False

    if (
        active_sensor is not None
        and active_index == index
    ):
        return True

    # Power everything down first
    deactivate()

    print()
    print("Activating sensor", index + 1)

    # Wake only the requested sensor
    xshut[index].value(1)

    # Allow full hardware boot
    time.sleep_ms(300)

    try:
        sensor = VL53L1X(
            i2c,
            address=0x29
        )

        sensor.set_short_mode()

        # If this method exists in your current driver, use 50 ms timing budget.
        try:
            sensor.set_timing_budget_50ms()
        except AttributeError:
            pass

        time.sleep_ms(50)

        distance = sensor.read()

        print(
            "Sensor",
            index + 1,
            "active:",
            distance,
            "mm",
            sensor.status
        )

        active_sensor = sensor
        active_index = index

        return True

    except Exception as e:

        print(
            "Sensor",
            index + 1,
            "activation FAILED:",
            e
        )

        xshut[index].value(0)

        active_sensor = None
        active_index = None

        return False



# =========================================================
# IS SENSOR ACTIVE?
# =========================================================

def is_available(index):

    return (
        active_sensor is not None
        and active_index == index
    )


# =========================================================
# RAW READ
# =========================================================

def read_raw(index):

    if active_sensor is None:

        return None


    if active_index != index:

        return None


    try:

        distance = active_sensor.read()


        if distance is None:

            return None


        # -------------------------------------------------
        # Only use useful range statuses
        # -------------------------------------------------

        if active_sensor.status not in (
            "OK",
            "MIN_RANGE_CLIPPED"
        ):

            print(
                "Sensor",
                index + 1,
                "status:",
                active_sensor.status
            )

            return None


        return int(distance)


    except Exception as e:

        print(
            "Sensor",
            index + 1,
            "read error:",
            e
        )

        return None


# =========================================================
# FILTERED READ
#
# Simple median.
# =========================================================

def read_filtered(
    index,
    samples=FILTER_SAMPLES
):

    values = []


    for _ in range(samples):

        value = read_raw(index)


        if value is not None:

            values.append(
                value
            )


        time.sleep_ms(55)


    if len(values) == 0:

        return None


    values.sort()


    return values[
        len(values) // 2
    ]


# =========================================================
# STABLE READ
#
# Compatibility with the rest of LEMAT.
# =========================================================

def read_stable(index):

    return read_filtered(
        index,
        FILTER_SAMPLES
    )


# =========================================================
# SENSOR STATUS
# =========================================================

def get_status(index):

    if (
        active_sensor is None
        or active_index != index
    ):
        return "INACTIVE"

    return active_sensor.status


# =========================================================
# GET BASELINE
# =========================================================

def get_baseline(index):

    if not is_available(index):
        return None

    values = []

    print(
        "Calibrating sensor",
        index + 1
    )

    # Seven fresh measurements. The driver time-gates each read,
    # so these are independent sensor samples.
    for _ in range(7):

        value = read_raw(index)

        if value is not None:
            values.append(value)

    if len(values) < 3:

        print("Baseline failed")
        return None

    values.sort()

    # Use a high idle reference, but ignore one possible low outlier.
    # Example: [84, 85, 85, 86, 86, 87, 87] -> baseline 85.
    baseline = values[1]

    print(
        "Sensor",
        index + 1,
        "baseline:",
        baseline,
        "mm"
    )

    return baseline



# =========================================================
# KEY PRESS DETECTION
#
# Distance INCREASE = pressed.
# =========================================================

def key_pressed(
    index,
    baseline,
    confirm_state
):

    # Use one fresh sample per detection cycle.
    # Two consecutive samples still have to exceed the threshold,
    # which filters one-off noise without the latency of a 3-sample median.
    current = read_raw(index)

    if current is None:
        return (
            False,
            confirm_state,
            None
        )

    movement = current - baseline

    if movement >= PRESS_MOVEMENT_MM:
        confirm_state += 1
    else:
        confirm_state = 0

    pressed = (
        confirm_state
        >= PRESS_CONFIRM_COUNT
    )

    return (
        pressed,
        confirm_state,
        current
    )