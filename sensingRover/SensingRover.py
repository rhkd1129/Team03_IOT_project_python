# 필요한 라이브러리 import
import time
import json
import paho.mqtt.client as mqtt
import threading

# 카메라 퍼블리셔를 실행하기 위한 클래스 import
from mqtt.camera_publisher import ImageMqttPublisher

# 발행(Publish)과 동시에 구독(Subscribe)을 하기위한 Subscriber 클래스 import
from mqtt.subscriber import MqttSubscriber
from mqtt.motor_subscriber import MotorMqttSubscriber
from mqtt.controller_subscriber import ControllerMqttSubscriber

# Sensor 값을 받아 오기 위한 클래스 import
from gpio.Gas import Gas
from gpio.HcSr04 import HcSr04
from gpio.Pca9685 import Pca9685
from gpio.Pcf8591 import Pcf8591
from gpio.Photoresister import Photoresister
from gpio.Thermistor import Thermistor
from gpio.Tracking import Tracking

# 속도 값을 저장하는 싱글톤 객체를 사용하기 위해 import
from mqtt.singleton import SingletonSpeed

class SensingRover:

    # SensingRover 객체 생성시에 필요한 요소 설정
    # brokerIp : Mqtt 통신의 Broker 역할을 하는 PC의 ip
    # brokerPort : brokerIp로 접속할때 필요한 port 번호
    # pubTopic : 발행할 메시지를 담을 Topic 설정, 디렉토리(혹은 자바에서 패키지)와 비슷한 개념이라고 생각하면 이해하기 쉬움
    def __init__(self, brokerIp, brokerPort, pubTopic):
        # 센서 값을 받아오기 위해 각각의 객체를 생성하고, Pin 번호도 동시에 설정

        self.pca9685 = Pca9685()
        self.pcf8591 = Pcf8591(0x48)
        self.gas = Gas(self.pcf8591, ain=2)
        self.hcsr04 = HcSr04(trigpin=38, echopin=40)
        self.thermistor = Thermistor(self.pcf8591, 1)
        self.photoresister = Photoresister(self.pcf8591, ain=0)
        self.tracking = Tracking(Tracking=36)

        # SensorRover 객체 생성 시 받아온 값을 클래스 내에서 사용하기 위한 선언
        self.brokerIp = brokerIp
        self.brokerPort = brokerPort
        self.pubTopic = pubTopic
        self.client = None

        # 속도 값을 받아 오기 위한 객체 생성
        self.singletonSpeed = SingletonSpeed()

    # Mqtt 통신에 연결을 시작하기 위한 메소드
    def connect(self):
        # 메인 스레드와 별도로 실행시키기 위해 스레드 처리(메인 스레드 종료 시 자동 종료하도록 daemon = True)
        thread = threading.Thread(target=self.__run, daemon=True)
        # 위에서 target으로 설정한 __run 메소드 실행
        thread.start()

    # thread.start() 호출 시에 시작되는 메소드
    def __run(self):
        # mqtt의 클라이언트(구독자, 발행자)로 작동할수있도록 client 객체 생성
        self.client = mqtt.Client()
        # 파이썬에서 함수는 객체이므로 아래와 같이 선언하면 개발자가 직접 작성한 함수를 client 객체가 본래 가지고 있는 함수에 선언됨
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.connect(self.brokerIp, self.brokerPort)
        # mqtt 연결을 지속할 수 있도록 loop_forever 호출
        self.client.loop_forever()


    # mqtt 연결에 성공했을 경우 자동적으로 호출되는 콜백함수
    def __on_connect(self, client, userdata, flags, rc):
        print('SensingRover mqtt broker connected')

    # mqtt 연결이 끊어졌을 경우 자동적으로 호출되는 콜백함수
    def __on_disconnect(self, client, userdata, rc):
        print('SensingRover mqtt broker disconnected')

    # 호출했을때 강제적으로 mqtt 연결이 끊기는 메소드
    def disconnect(self):
        self.client.disconnect()

    # 연결한 mqtt broker로 메시지 발행(Publish)
    def publish(self):

        # mqtt 연결이 정상적으로 이뤄지지 않아서 client 객체가 생성되지 않았을 경우 해당 메소드를 빠져나간다.
        if self.client is None:
            return

        # 연결이 되어있지 않을 경우에도 해당 메소드를 빠져나간다.
        if not self.client.is_connected():
            return

        # while문을 무한 루프돌리기 위해서 stop flag 선언
        self.__stop = False
        # 센서값을 계속 발행하기 위한 while문

        while not self.__stop:

            # 각 센서 객체가 가지고 있는 메소드를 통해 값을 받아온다.
            sonic_distance = self.hcsr04.distance()
            temperature = self.thermistor.read()
            illumination = self.photoresister.read()
            gas = self.gas.read()
            tracking = self.tracking.read()
            speed = self.singletonSpeed.get_speed()

            # 받아온 값을 딕셔너리 타입으로 만들어준다. JSON으로 변환하기 위해서.
            message = {'sonic_distance':sonic_distance,
                       'temperature':temperature,
                       'illumination':illumination,
                       'gas':gas,
                       'tracking':tracking,
                       'speed':speed}

            # 딕셔너리 타입의 메시지를 JSON으로 변환
            message = json.dumps(message)
            # client 객체가 가지고 있는 publish 메소드를 통해 최초에 받아온 topic으로 메시지를 보낸다.
            self.client.publish(self.pubTopic, message)
            #print('발행 내용:', self.pubTopic, message)
            # 메시지를 보내고자 하는 주기
            time.sleep(1)

if __name__ == "__main__":
    # SensingRover와 ImageMqttPublisher 객체 생성
    sr = SensingRover('192.168.3.163', 1883, '/sensor')
    imageMqttPublisher = ImageMqttPublisher('192.168.3.163', 1883, '/camerapub')

    # 각각의 connect 메소드 호출
    sr.connect()
    imageMqttPublisher.connect()

    # 스레드 처리를 하여 imageMqttPublisher 객체의 publish 메소드를 실행하기 위해 thread 객체 생성
    camera_thread = threading.Thread(target=imageMqttPublisher.publish, daemon=True)

    # thread 시작
    camera_thread.start()

    # 구독을 위한 객체 생성
    mqttSubscriber = MqttSubscriber('192.168.3.163', topic='/Control/#')
    mqttSubscriber.laser.off()
    mqttSubscriber.laser2.off()
    motorMqttSubscriber = MotorMqttSubscriber('192.168.3.163', topic='/Control/#')
    controllerMqttSubscriber = ControllerMqttSubscriber('192.168.3.163', topic='/Controller/#')

    # 구독 객체의 start 메소드 호출하여 구독 시작
    mqttSubscriber.start()
    motorMqttSubscriber.start()
    controllerMqttSubscriber.start()

    # publish 메소드 호출하여 메시지 발행
    sr.publish()