import time
import gpio.Pca9685 as Pca9685

class Sg90:
    def __init__(self, pca9685, channel, frequency=50):
        self.__pca9685 = pca9685
        self.__channel = channel
        # Pca9685의 출력 Hz를 설정
        # 대부분의 모터는 50hz 를 사용
        pca9685.frequency = frequency

    def __map(self, angle):
        return int(164 + angle*((553-164)/180))

    def angle(self, angle):
        self.__pca9685.write(self.__channel, self.__map(angle))

if __name__ == '__main__':
    pca9685 = Pca9685.Pca9685()
    sg = Sg90(pca9685, channel=13)

    sg.angle(180)
