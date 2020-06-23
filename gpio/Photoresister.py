import time
from gpio.Pcf8591 import Pcf8591
from gpio.RgbLed import RgbLed

class Photoresister:
    def __init__(self, pcf8591, ain):
        self.__pcf8591 = pcf8591
        self.__ain = ain

    def read(self):
        temp = self.__pcf8591.read(self.__ain)

        return temp

if __name__ == '__main__':
    try:
        pcf8591 = Pcf8591(0x48)
        photo = Photoresister(pcf8591, ain=0)
        led = RgbLed(redpin=16)
        while True:
            value = 255 - photo.read()
            print('조도 : {}'.format(value))
            if value < 55:
                led.red()
                time.sleep(0.2)
                led.off()
            time.sleep(1)
    finally:
        print('Program exit')