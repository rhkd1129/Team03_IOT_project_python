import paho.mqtt.client as mqtt
import threading
from gpio.DCMotor import DCMotor
from gpio.Pca9685 import Pca9685
from mqtt.singleton import SingletonSpeed

# Motor와 관련된 메시지를 구독하기 위한 클래스
class MotorMqttSubscriber:
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
        # 속도 정보가 저장되는 싱글톤 객체 생성
        self.singletonSpeed = SingletonSpeed()
        # 모터의 기본 속도 정의
        self.motorspeed = 0

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

        if message.topic == '/Control/Motor':
            if str(message.payload, encoding='UTF-8') == 'accel':
                # 현재 후진 상태일 경우 점점 속도를 줄여 0에 가까워 짐
                if self.motorspeed < 0:
                    self.motorspeed += 100
                    # 후진 상태의 경우 속도가 음수이므로 절대값을 씌워서 setSpeed 메소드의 매개값으로 사용
                    self.dcMotorR.setSpeed(abs(self.motorspeed))
                    self.dcMotorL.setSpeed(abs(self.motorspeed))
                else:
                    self.motorspeed += 5
                    if self.motorspeed > 4000:
                        self.motorspeed = 4000
                    self.dcMotorR.setSpeed(self.motorspeed)
                    self.dcMotorL.setSpeed(self.motorspeed)
                    self.dcMotorR.forword()
                    self.dcMotorL.forword()
                
                # 싱글톤 객체에 속도 정보 저장
                self.singletonSpeed.set_speed(self.motorspeed)


            elif str(message.payload, encoding='UTF-8') == 'break' :
                self.motorspeed = 0
                self.dcMotorR.setSpeed(self.motorspeed)
                self.dcMotorL.setSpeed(self.motorspeed)
                self.singletonSpeed.set_speed(self.motorspeed)

            elif str(message.payload, encoding='UTF-8') == 'backword':
                # self.motorspeed -= 100
                # self.dcMotorR.setSpeed(self.motorspeed)
                # self.dcMotorL.setSpeed(self.motorspeed)

                if self.motorspeed < 0:
                    self.dcMotorR.backword()
                    self.dcMotorL.backword()
                    self.motorspeed -= 5
                    if self.motorspeed < -4000:
                        self.motorspeed = -4000


                    self.dcMotorR.setSpeed(abs(self.motorspeed))
                    self.dcMotorL.setSpeed(abs(self.motorspeed))
                else:
                    self.motorspeed -= 100
                    self.dcMotorR.setSpeed(self.motorspeed)
                    self.dcMotorL.setSpeed(self.motorspeed)

                self.singletonSpeed.set_speed(self.motorspeed)

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

