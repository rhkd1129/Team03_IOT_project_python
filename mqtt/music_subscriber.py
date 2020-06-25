import paho.mqtt.client as mqtt
import threading
from gpio.Mbuzzer import MusicBuzzer

# Motor와 관련된 메시지를 구독하기 위한 클래스
class MusicMqttSubscriber:
    def __init__(self, brokerIp=None, brokerPort=1883, topic=None):
        self.__brokerIp = brokerIp
        self.__brokerPort = brokerPort
        self.__topic = topic
        self.__client = mqtt.Client()
        self.__client.on_connect = self.__on_connect
        self.__client.on_disconnect = self.__on_disconnect
        self.__client.on_message = self.__on_message
        self.ms = MusicBuzzer(32)

    # 연결 되었을 때 자동으로 호출되는 콜백함수
    def __on_connect(self, client, userdata, flags, rc):
        print('** connection **')
        self.__client.subscribe(self.__topic, qos=0)

    # 연결이 끊겼을 때 자동으로 호출되는 콜백함수
    def __on_disconnect(self, client, userdata, rc):
        print('** disconnection **')

    # 메시지가 도착했을 때 자동으로 호출되는 콜백함수
    def __on_message(self, client, userdata, message):
        if message.topic == '/Controller/Music':
            self.ms.on()

            # if str(message.payload, encoding='UTF-8') == 'stop':
            #     print('실행1')
            #     self.ms.status = False
            #     print('실행2')

        if message.topic == '/Controller/Music/Stop':
            self.ms.off()


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

