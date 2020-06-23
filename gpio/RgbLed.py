import RPi.GPIO as GPIO
import time

class RgbLed:
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

    def __init__(self, redpin = None, greenpin = None, bluepin = None):
        self.__redpin = redpin
        self.__greenpin = greenpin
        self.__bluepin = bluepin
        self.state = None
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)        
        if redpin is not None:
            GPIO.setup(redpin, GPIO.OUT, initial=GPIO.HIGH)
        if greenpin is not None:
            GPIO.setup(greenpin, GPIO.OUT, initial=GPIO.HIGH)
        if bluepin is not None:
            GPIO.setup(bluepin, GPIO.OUT, initial=GPIO.HIGH)

    def red(self):
        self.state = RgbLed.RED
        if self.__redpin is not None:
            GPIO.output(self.__redpin, GPIO.LOW)
        if self.__greenpin is not None:
            GPIO.output(self.__greenpin, GPIO.HIGH)
        if self.__bluepin is not None:
            GPIO.output(self.__bluepin, GPIO.HIGH)

    def green(self):
        self.state = RgbLed.GREEN
        if self.__redpin is not None:
            GPIO.output(self.__redpin, GPIO.HIGH)
        if self.__greenpin is not None:
            GPIO.output(self.__greenpin, GPIO.LOW)
        if self.__bluepin is not None:
            GPIO.output(self.__bluepin, GPIO.HIGH)

    def blue(self):
        self.state = RgbLed.BLUE
        if self.__redpin is not None:
            GPIO.output(self.__redpin, GPIO.HIGH)
        if self.__greenpin is not None:
            GPIO.output(self.__greenpin, GPIO.HIGH)
        if self.__bluepin is not None:
            GPIO.output(self.__bluepin, GPIO.LOW)

    def off(self):
        self.state = RgbLed.BLUE
        if self.__redpin is not None:
            GPIO.output(self.__redpin, GPIO.HIGH)
        if self.__greenpin is not None:
            GPIO.output(self.__greenpin, GPIO.HIGH)
        if self.__bluepin is not None:
            GPIO.output(self.__bluepin, GPIO.HIGH)

if __name__ == "__main__":
    i = 0
    try:
        led = RgbLed(16, 18, 22)
        
        while True:
            i += 1
            led.red()
            time.sleep(0.2)
            led.off()

            led.green()
            time.sleep(0.2)
            led.off()
            
            led.blue()
            time.sleep(0.2)
            led.off()
            if i == 100:
                break
    except KeyboardInterrupt:
        print()
    finally:
        led.off()
        print('program exit')
    

