import time


# =========================================================
# VL53L1X DEFAULT CONFIG
#
# Based on the PiicoDev-style configuration already used
# successfully in this project. The final byte corresponds
# to SYSTEM__MODE_START = 0x40, so ranging begins after the
# configuration block is written.
# =========================================================

DEFAULT_CONFIG = bytes([
    0x00, 0x00, 0x00, 0x01, 0x02, 0x00, 0x02, 0x08,
    0x00, 0x08, 0x10, 0x01, 0x01, 0x00, 0x00, 0x00,
    0x00, 0xFF, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x20, 0x0B, 0x00, 0x00, 0x02, 0x0A, 0x21,
    0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x00, 0xC8,
    0x00, 0x00, 0x38, 0xFF, 0x01, 0x00, 0x08, 0x00,
    0x00, 0x01, 0xDB, 0x0F, 0x01, 0xF1, 0x0D, 0x01,
    0x68, 0x00, 0x80, 0x08, 0xB8, 0x00, 0x00, 0x00,
    0x00, 0x0F, 0x89, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x01, 0x0F, 0x0D, 0x0E, 0x0E, 0x00,
    0x00, 0x02, 0xC7, 0xFF, 0x9B, 0x00, 0x00, 0x00,
    0x01, 0x01, 0x40
])


# =========================================================
# REGISTERS USED BY THE RANGING LOOP
# =========================================================

GPIO_HV_MUX_CTRL = 0x0030
GPIO_TIO_HV_STATUS = 0x0031
SYSTEM_INTERRUPT_CLEAR = 0x0086
SYSTEM_MODE_START = 0x0087
RESULT_RANGE_STATUS = 0x0089


class VL53L1X:

    def __init__(self, i2c, address=0x29):

        self.i2c = i2c
        self.address = address
        self.status = None
        self.ranging = False
        self._next_read_ms = time.ticks_ms()

        self.reset()
        time.sleep_ms(5)

        model_id = self.read_reg16(0x010F)
        print("VL53L1X model ID:", hex(model_id))

        if model_id != 0xEACC:
            raise RuntimeError(
                "VL53L1X not detected. ID = %s"
                % hex(model_id)
            )

        # Known-good configuration. The final configuration byte writes
        # 0x40 to SYSTEM__MODE_START, which starts continuous ranging.
        self.i2c.writeto_mem(
            self.address,
            0x002D,
            DEFAULT_CONFIG,
            addrsize=16
        )

        self.ranging = True
        time.sleep_ms(100)

        # Same calibration step used by the previous PiicoDev-style driver.
        self.write_reg16(
            0x001E,
            self.read_reg16(0x0022) * 4
        )

        time.sleep_ms(100)


    # =====================================================
    # BASIC REGISTER ACCESS
    # =====================================================

    def write_reg(self, reg, value):
        self.i2c.writeto_mem(
            self.address,
            reg,
            bytes([value & 0xFF]),
            addrsize=16
        )


    def write_reg16(self, reg, value):
        self.i2c.writeto_mem(
            self.address,
            reg,
            bytes([
                (value >> 8) & 0xFF,
                value & 0xFF
            ]),
            addrsize=16
        )


    def read_reg(self, reg):
        return self.i2c.readfrom_mem(
            self.address,
            reg,
            1,
            addrsize=16
        )[0]


    def read_reg16(self, reg):
        data = self.i2c.readfrom_mem(
            self.address,
            reg,
            2,
            addrsize=16
        )

        return (
            (data[0] << 8)
            | data[1]
        )


    # =====================================================
    # RESET / ADDRESS
    # =====================================================

    def reset(self):
        self.write_reg(0x0000, 0x00)
        time.sleep_ms(100)

        self.write_reg(0x0000, 0x01)
        time.sleep_ms(100)


    def set_address(self, new_address):
        self.write_reg(
            0x0001,
            new_address & 0x7F
        )

        time.sleep_ms(10)
        self.address = new_address & 0x7F


    # =====================================================
    # SHORT DISTANCE MODE
    # =====================================================

    def set_short_mode(self):
        # RANGE_CONFIG__VCSEL_PERIOD_A
        self.write_reg(0x0060, 0x07)

        # RANGE_CONFIG__VCSEL_PERIOD_B
        self.write_reg(0x0063, 0x05)

        # RANGE_CONFIG__VALID_PHASE_HIGH
        self.write_reg(0x0069, 0x38)

        # SD_CONFIG__WOI_SD0
        self.write_reg(0x0078, 0x07)

        # SD_CONFIG__WOI_SD1
        self.write_reg(0x0079, 0x05)

        # SD_CONFIG__INITIAL_PHASE_SD0
        self.write_reg(0x007A, 0x06)

        # SD_CONFIG__INITIAL_PHASE_SD1
        self.write_reg(0x007B, 0x06)

        time.sleep_ms(20)


    # =====================================================
    # RANGING CONTROL
    # =====================================================

    def start_ranging(self):
        self.clear_interrupt()
        self.write_reg(SYSTEM_MODE_START, 0x40)
        self.ranging = True
        # Allow the sensor time to produce the first new sample.
        self._next_read_ms = time.ticks_add(time.ticks_ms(), 55)


    def stop_ranging(self):
        self.write_reg(SYSTEM_MODE_START, 0x00)
        self.ranging = False


    def clear_interrupt(self):
        self.write_reg(SYSTEM_INTERRUPT_CLEAR, 0x01)


    # =====================================================
    # READ DISTANCE
    # =====================================================

    def read(self, timeout_ms=120):
        """Return one time-separated measurement without tight status polling.

        Reads are spaced by 55 ms, followed by one result-block transaction
        and an interrupt clear. This avoids repeatedly polling I2C status
        registers in a tight loop.
        """

        if not self.ranging:
            return None

        now = time.ticks_ms()
        remaining = time.ticks_diff(self._next_read_ms, now)

        if remaining > 0:
            # Cap the wait by timeout_ms, although with the normal 55 ms
            # cadence this should never hit the timeout.
            if remaining > timeout_ms:
                self.status = "TIMEOUT"
                return None
            time.sleep_ms(remaining)

        data = self.i2c.readfrom_mem(
            self.address,
            RESULT_RANGE_STATUS,
            17,
            addrsize=16
        )

        range_status = data[0]
        distance = (data[13] << 8) | data[14]

        if range_status == 9:
            self.status = "OK"
        elif range_status == 8:
            self.status = "MIN_RANGE_CLIPPED"
        elif range_status in (4, 6):
            self.status = "SIGNAL_FAIL"
        elif range_status == 12:
            self.status = "XTALK_FAIL"
        elif range_status == 5:
            self.status = "OUT_OF_BOUNDS"
        else:
            self.status = "STATUS_%d" % range_status

        self.clear_interrupt()

        # Schedule the next independent sample.
        self._next_read_ms = time.ticks_add(time.ticks_ms(), 55)

        return distance