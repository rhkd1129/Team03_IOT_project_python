import time
from Pcf8591 import Pcf8591
from Buzzer import ActiveBuzzer
from RgbLed import RgbLed

class Flame:
    def __init__(self, pcf8591, ain):
        self.__pcf8591 = pcf8591
        self.__ain = ain

    def read(self):
        value = self.__pcf8591.read(self.__ain)
        return value

if __name__ == '__main__':
    try:
        pcf8591 = Pcf8591(0x48)
        flame = Flame(pcf8591, ain=0)
        buzzer = ActiveBuzzer(11)
        led = RgbLed(redpin=12)
        while True:
            value = flame.read()
            print('value: {}'.format(value))
            time.sleep(1)
    finally:
        print('Program Exit')