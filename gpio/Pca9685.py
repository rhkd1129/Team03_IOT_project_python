import smbus
import math
import time

class Pca9685:
    _MODE1              = 0x00
    _MODE2              = 0x01
    _SUBADR1            = 0x02
    _SUBADR2            = 0x03
    _SUBADR3            = 0x04
    _PRESCALE           = 0xFE
    _LED0_ON_L          = 0x06
    _LED0_ON_H          = 0x07
    _LED0_OFF_L         = 0x08
    _LED0_OFF_H         = 0x09
    _ALL_LED_ON_L       = 0xFA
    _ALL_LED_ON_H       = 0xFB
    _ALL_LED_OFF_L      = 0xFC
    _ALL_LED_OFF_H      = 0xFD

    _RESTART            = 0x80
    _SLEEP              = 0x10
    _ALLCALL            = 0x01
    _INVRT              = 0x10
    _OUTDRV             = 0x04

    def __init__(self, bus_number=1, address=0x40):
        self.address = address
        self.bus_number = bus_number
        self.bus = smbus.SMBus(self.bus_number)
        self.write_all_value(0)
        self.__write_byte_data(self._MODE2, self._OUTDRV)
        self.__write_byte_data(self._MODE1, self._ALLCALL)
        time.sleep(0.005)

        mode1 = self._read_byte_data(self._MODE1)
        mode1 = mode1 & ~self._SLEEP
        self.__write_byte_data(self._MODE1, mode1)
        time.sleep(0.005)
        self.__frequency = None

    def __write_byte_data(self, reg, value):
        self.bus.write_byte_data(self.address, reg, value)

    def _read_byte_data(self, reg):
        results = self.bus.read_byte_data(self.address, reg)
        return results

    @property
    def frequency(self):
        return self.__frequency

    @frequency.setter
    def frequency(self, freq):
        self.__frequency = freq
        prescale_value = 25000000.0
        prescale_value /= 4096.0
        prescale_value /= float(freq)
        prescale_value -= 1.0
        prescale = math.floor(prescale_value + 0.5)

        old_mode = self._read_byte_data(self._MODE1);
        new_mode = (old_mode & 0x7F) | 0x10
        self.__write_byte_data(self._MODE1, new_mode)
        self.__write_byte_data(self._PRESCALE, int(math.floor(prescale)))
        self.__write_byte_data(self._MODE1, old_mode)
        time.sleep(0.005)
        self.__write_byte_data(self._MODE1, old_mode | 0x80)

    def write(self, channel, step):
        self.__write_byte_data(self._LED0_ON_L + 4 * channel, 0 & 0xFF)
        self.__write_byte_data(self._LED0_ON_H + 4 * channel, 0 >> 8)
        self.__write_byte_data(self._LED0_OFF_L + 4 * channel, step & 0xFF)
        self.__write_byte_data(self._LED0_OFF_H + 4 * channel, step >> 8)

    def write_all_value(self, step):
        self.__write_byte_data(self._ALL_LED_ON_L, 0 & 0xFF)
        self.__write_byte_data(self._ALL_LED_ON_H, 0 >> 8)
        self.__write_byte_data(self._ALL_LED_OFF_L, step & 0xFF)
        self.__write_byte_data(self._ALL_LED_OFF_H, step >> 8)

    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
