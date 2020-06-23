import time
import math
import socket
from gpio.Pcf8591 import Pcf8591
from gpio.Buzzer import ActiveBuzzer
from gpio.RgbLed import RgbLed
from gpio.Lcd1602 import Lcd1602

class Thermistor:

    def __init__(self, pcf8591, ain):
        self.__pcf8591 = pcf8591
        self.__ain = ain
        self.__lcd1602 = Lcd1602(0x27)

    def read(self):
        temp = self.__pcf8591.read(self.__ain) # 0 ~ 255
        temp = 5 * float(temp) / 255
        temp = 10000 * temp / (5-temp)

        temp = 1 / (((math.log(temp/10000)) / 3950) + (1 / (273.15+25)))
        tempSet= temp-273.15
        temperature = round(tempSet, 3)
        return tempSet


#################################################

if __name__ == '__main__':
    try:
        pcf8591 = Pcf8591(0x48)
        sensor = Thermistor(pcf8591,1)
        lcd1602 = Lcd1602(0x27)

        while True:
            temperature = round(sensor.read(), 3)
            print('섭씨온도: {}도'.format(temperature))
            time.sleep(1)
            lcd1602.write(0, 0, "Temperature")
            lcd1602.write(0, 1, str(temperature))


    finally:
        lcd1602.write(0, 0, 'Program Exit')
        print('Program Exit')