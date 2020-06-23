import smbus

class Pcf8591:
    def __init__(self, addr):
        # Jetson Nano Board의 I2C Bus 번호 설정
        self.__bus = smbus.SMBus(1)
        # pCD8591의 I2C 장치 번호
        self.__addr = addr

    # channel: AIN0 ~ AIN3
    def read(self, channel):
        try:
            if channel == 0:
                self.__bus.write_byte(self.__addr, 0x40)
            elif channel == 1:
                self.__bus.write_byte(self.__addr, 0x41)
            elif channel == 2:
                self.__bus.write_byte(self.__addr, 0x42)
            elif channel == 3:
                self.__bus.write_byte(self.__addr, 0x43)
            self.__bus.read_byte(self.__addr)
            value = self.__bus.read_byte(self.__addr)
        except Exception as e:
            print(e)
            value = -1
        return value

    # value: AOUT으로 출력되는 값
    def write(self, value):
        try:
            value = int(value)
            self.__bus.write_byte_data(self.__addr, 0x40, value)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    pcf8591 = Pcf8591(0x48)
    while True:
        value = pcf8591.read(0)
        light = value * (255-125) / 255 + 125
        pcf8591.write(light)
        print('value : {}'.format(value))