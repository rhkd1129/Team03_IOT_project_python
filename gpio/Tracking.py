import RPi.GPIO as GPIO
import time

class Tracking:

    def __init__(self, Tracking):
        self.__Tracking = Tracking
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__Tracking, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setwarnings(False)

    def read(self):
        if GPIO.input(self.__Tracking) == GPIO.LOW:
            return 'white'

        else:
            return 'black'

    def destroy(self):
        GPIO.cleanup()

if __name__ == '__main__':

    tr = Tracking(Tracking=36)


