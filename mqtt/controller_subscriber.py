import paho.mqtt.client as mqtt
import threading
from gpio.DCMotor import DCMotor
from gpio.Pca9685 import Pca9685
from mqtt.singleton import SingletonSpeed
from gpio.Sg90 import Sg90

# Motor와 관련된 메시지를 구독하기 위한 클래스
class ControllerMqttSubscriber:
    def __init__(self, brokerIp=None, brokerPort=1883, topic=None):
        self.__brokerIp = brokerIp
        self.__brokerPort = brokerPort
        self.__topic = topic
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.pca9685 = Pca9685()
        self.dcMotorL = DCMotor(IN1=11, IN2=12, pca9685=self.pca9685, pwm=5)
        self.dcMotorR = DCMotor(IN1=13, IN2=15, pca9685=self.pca9685, pwm=4)
        self.sg90direction = Sg90(self.pca9685, channel=15)
        self.sg90sensor = Sg90(self.pca9685, channel=14)
        # 속도 정보가 저장되는 싱글톤 객체 생성
        self.singletonSpeed = SingletonSpeed()
        # 모터의 기본 속도 정의
        self.motorspeed = 0
        self.direction_angle = 90
        self.sensor_angle = 70

    # 연결 되었을 때 자동으로 호출되는 콜백함수
    def __on_connect(self, client, userdata, flags, rc):
        print('** connection **')
        self.__client.subscribe(self.__topic, qos=0)

    # 연결이 끊겼을 때 자동으로 호출되는 콜백함수
    def __on_disconnect(self, client, userdata, rc):
        print('** disconnection **')

    # 메시지가 도착했을 때 자동으로 호출되는 콜백함수
    def __on_message(self, client, userdata, message):

        # self.status = str(message.payload, encoding='UTF-8')
        if message.topic == '/Controller/Move/Forward':
            message = str(message.payload, encoding='UTF-8').split(':', -1)
            axesValue = abs(float(message[1]))

            self.motorspeed = int(4000 * axesValue**2)
            self.dcMotorR.setSpeed(self.motorspeed)
            self.dcMotorL.setSpeed(self.motorspeed)
            self.dcMotorR.forward()
            self.dcMotorL.forward()
            self.singletonSpeed.set_speed(self.motorspeed)

        if message.topic == '/Controller/Move/Backward':
            message = str(message.payload, encoding='UTF-8').split(':', -1)
            axesValue = abs(float(message[1]))

            self.motorspeed = int(4000 * axesValue**2)
            self.dcMotorR.setSpeed(self.motorspeed)
            self.dcMotorL.setSpeed(self.motorspeed)
            self.dcMotorR.backward()
            self.dcMotorL.backward()
            self.singletonSpeed.set_speed(self.motorspeed)

        if message.topic == '/Controller/Move/Direction':
            message = str(message.payload, encoding='UTF-8').split(':', -1)
            axesValue = float(message[1])
            direction_angle = int(30 * axesValue + 90)

            self.sg90direction.angle(direction_angle)
             #self.sg90sensor.angle(self.sensor_angle)

        if message.topic == '/Controller/Sensor/Direction':
            message = str(message.payload, encoding='UTF-8').split(':', -1)
            axesValue = float(message[1]) * (-1)
            sensor_angle = int(30 * axesValue + 70)

            self.sg90sensor.angle(sensor_angle)




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

