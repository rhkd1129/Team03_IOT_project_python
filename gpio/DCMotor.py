import RPi.GPIO as GPIO
from gpio.Pca9685 import Pca9685
from gpio.HcSr04 import HcSr04
import time

class DCMotor():
    def __init__(self, IN1, IN2, pca9685, pwm, frequency = 50):
        self.__IN1 = IN1
        self.__IN2 = IN2
        self.__pca9685 = pca9685
        self.__pwm = pwm
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        GPIO.setup(self.__IN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.__IN2, GPIO.OUT, initial=GPIO.LOW)

    def setSpeed(self, step):
        self.__pca9685.write(self.__pwm, step)

    def forword(self):
        GPIO.output(self.__IN1, GPIO.HIGH)
        GPIO.output(self.__IN2, GPIO.LOW)

    def backword(self):
        GPIO.output(self.__IN1, GPIO.LOW)
        GPIO.output(self.__IN2, GPIO.HIGH)

    def stop(self):
        GPIO.output(self.__IN1, GPIO.LOW)
        GPIO.output(self.__IN2, GPIO.LOW)
        self.setSpeed(0)



if __name__ == '__main__':
    pca9685 = Pca9685()
    dcMotor1 = DCMotor(IN1=11, IN2=12, pca9685=pca9685, pwm=5)
    dcMotor2 = DCMotor(IN1=13, IN2=15, pca9685=pca9685, pwm=4)
    hcsr04 = HcSr04(trigpin=38, echopin=40)

    dcMotor1.setSpeed(1023)
    dcMotor2.setSpeed(1023)
    dcMotor1.forword()
    dcMotor2.forword()
    time.sleep(5)
    dcMotor1.backword()
    dcMotor2.backword()
    time.sleep(5)
    dcMotor1.stop()
    dcMotor2.stop()

    # while True:
    #     distance = hcsr04.distance()
    #     print("거리: {}".format(distance))
    #     time.sleep(0.3)
    #     if distance < 15:
    #         time.sleep(1)
    #         dcMotor1.backword()
    #         dcMotor2.backword()
    #         time.sleep(5)
    #         dcMotor1.stop()
    #         dcMotor2.stop()








