import time

from gpio.Buzzer import ActiveBuzzer
from gpio.Pcf8591 import Pcf8591
from gpio.RgbLed import RgbLed


class Gas:
    def __init__(self, pcf8591, ain):
        self.__pcf8591 = pcf8591
        self.__ain = ain
        self.buzzer = ActiveBuzzer(35)
        self.rgbLed = RgbLed(redpin=16)

    def read(self):
        value = self.__pcf8591.read(self.__ain)
        if value > 205:
            self.buzzer.on()
            self.rgbLed.red()
        else:
            self.buzzer.off()
            self.rgbLed.off()
        return value

if __name__ == '__main__':
    try:
        pcf8591 = Pcf8591(0x48)
        gas = Gas(pcf8591, ain=2)
        buzzer = ActiveBuzzer(35)
        led = RgbLed(redpin=16)
        while True:
            value = gas.read()
            print('value: {}'.format(value))
            time.sleep(1)
    finally:
        print('Program Exit')