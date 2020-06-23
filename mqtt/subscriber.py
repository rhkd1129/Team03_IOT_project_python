import paho.mqtt.client as mqtt
import threading
from gpio.RgbLed import RgbLed
from gpio.Pca9685 import Pca9685
from gpio.Buzzer import ActiveBuzzer
from gpio.Sg90 import Sg90
from gpio.Laser import Laser
from gpio.Lcd1602 import Lcd1602

# 각종 센서와 관련된 메시지를 구독하기 위해 만든 클래스
class MqttSubscriber:
    def __init__(self, brokerIp=None, brokerPort=1883, topic=None):
        self.__brokerIp = brokerIp
        self.__brokerPort = brokerPort
        self.__topic = topic
        # mqtt의 Client 객체 생성
        self.__client = mqtt.Client()
        # 콜백 함수 설정
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        # 메시지를 받았을때 자동을 호출되는 콜백함수
        self.__client.on_message = self.__on_message
        # 센서 객체 생성
        self.rgbLed = RgbLed(redpin=16, greenpin=18, bluepin=22)
        self.pca9685 = Pca9685()
        self.buzzer = ActiveBuzzer(35)
        self.laser = Laser(37)
        self.laser2 = Laser(29)
        self.sg90direction = Sg90(self.pca9685, channel=15)
        self.sg90sensor = Sg90(self.pca9685, channel=14)
        self.sg90camera_vertical = Sg90(self.pca9685, channel=13)
        self.sg90camera_horizontal = Sg90(self.pca9685, channel= 8) #12번인데 지금 개박살나서 8번으로 비활성화 해놨어요
        self.lcd1602 = Lcd1602(0x27)
        # 서보모터 각도 고정값
        self.camera_angle_vertical =10
        self.camera_angle_horizontal = 70
        self.direction_angle = 90
        self.sensor_angle = 70

    # mqtt 연결에 성공했을 경우 자동적으로 호출되는 콜백함수
    def __on_connect(self, client, userdata, flags, rc):
        print('** connection **')
        self.__client.subscribe(self.__topic, qos=0)

    # mqtt 연결이 끊어졌을 경우 자동적으로 호출되는 콜백함수
    def __on_disconnect(self, client, userdata, rc):
        print('** disconnection **')

    # message가 도착했을 때 자동으로 호출되는 콜백함수
    def __on_message(self, client, userdata, message):
        # self.status = str(message.payload, encoding='UTF-8')
        # 각각의 토픽에 따라 메시지 내용 처리방식
        if message.topic == '/Control/RgbLed':
            if str(message.payload, encoding='UTF-8') == 'ledOn':
                self.rgbLed.red()
            elif str(message.payload, encoding='UTF-8') == 'ledOff':
                self.rgbLed.off()

        if message.topic == '/Control/Direction/Camera':
            if str(message.payload, encoding='UTF-8') == 'down':
                self.camera_angle_vertical -= 4
                if self.camera_angle_vertical < 0:
                    self.camera_angle_vertical = 0
                self.sg90camera_vertical.angle(self.camera_angle_vertical)

            elif str(message.payload, encoding='UTF-8') == 'up':
                self.camera_angle_vertical += 4
                if self.camera_angle_vertical>120:
                    self.camera_angle_vertical = 120
                self.sg90camera_vertical.angle(self.camera_angle_vertical)

            elif str(message.payload, encoding='UTF-8') == 'right':
                self.camera_angle_horizontal -= 4
                if self.camera_angle_horizontal< 10:
                    self.camera_angle_horizontal = 10
                self.sg90camera_horizontal.angle(self.camera_angle_horizontal)
            elif str(message.payload, encoding='UTF-8') == 'left':
                self.camera_angle_horizontal += 4
                if self.camera_angle_horizontal > 170:
                    self.camera_angle_horizontal = 170
                self.sg90camera_horizontal.angle(self.camera_angle_horizontal)

            elif str(message.payload, encoding='UTF-8') == 'stop':
                self.sg90camera_vertical.angle(self.camera_angle_vertical)

            elif str(message.payload, encoding='UTF-8') == 'horizonstop':
                self.sg90camera_horizontal.angle(self.camera_angle_horizontal)

        if message.topic == '/Control/Laser':
            if str(message.payload, encoding='UTF-8') == 'on':
                self.laser.on()
                self.laser2.on()

            elif str(message.payload, encoding='UTF-8') == 'off':
                self.laser.off()
                self.laser2.off()


        if message.topic == '/Control/Direction/FrontWheel':
            if str(message.payload, encoding='UTF-8') == 'left':
                self.direction_angle -= 3
                self.sensor_angle += 3
                if self.direction_angle < 60:
                    self.direction_angle = 60
                if self.sensor_angle > 100:
                    self.sensor_angle = 100

                self.sg90direction.angle(self.direction_angle)
                self.sg90sensor.angle(self.sensor_angle)

            elif str(message.payload, encoding='UTF-8') == 'right':
                self.direction_angle += 3
                self.sensor_angle -= 3
                if self.direction_angle > 120:
                    self.direction_angle = 120
                if self.sensor_angle < 40:
                    self.sensor_angle = 40

                self.sg90direction.angle(self.direction_angle)
                self.sg90sensor.angle(self.sensor_angle)

            elif str(message.payload, encoding='UTF-8') == 'stop':
                self.sg90direction.angle(self.direction_angle)
                self.sg90sensor.angle(self.sensor_angle)

        if message.topic == '/Control/Buzzer':
            if str(message.payload, encoding='UTF-8') == 'buzzerOn':
                self.buzzer.on()

            elif str(message.payload, encoding='UTF-8') == 'buzzerOff':
                self.buzzer.off()

        if message.topic == '/Control/Lcd':
            received_message = str(message.payload, encoding='UTF-8')

            self.lcd1602.write(0, 0, 'Received Message')
            self.lcd1602.write(0, 1, '>'+received_message)

    # subscribe 메소드를 스레드방식으로 시작하는 메소드
    def start(self):
        thread = threading.Thread(target=self.__subscribe)
        thread.start()

    # mqtt client에 구독자로서 연결
    def __subscribe(self):
        self.__client.connect(self.__brokerIp, self.__brokerPort)
        self.__client.loop_forever()

    # 강제적으로 연결 종료
    def stop(self):
        self.__client.unsubscribe(self.__topic)
        self.__client.disconnect()
