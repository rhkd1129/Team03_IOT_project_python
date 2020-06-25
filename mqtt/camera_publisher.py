import cv2
import paho.mqtt.client as mqtt
import threading
import base64
import numpy as np
from datetime import datetime
import time

class ImageMqttPublisher:

    # ImageMqttPublisher 객체 생성시에 필요한 요소 설정
    # brokerIp : Mqtt 통신의 Broker 역할을 하는 PC의 ip
    # brokerPort : brokerIp로 접속할때 필요한 port 번호
    # pubTopic : 발행할 메시지를 담을 Topic 설정, 디렉토리(혹은 자바에서 패키지)와 비슷한 개념이라고 생각하면 이해하기 쉬움
    def __init__(self, brokerIp, brokerPort, pubTopic):
        self.brokerIp = brokerIp
        self.brokerPort = brokerPort
        self.pubTopic = pubTopic
        self.client = None
        # 0번 카메라의 VideoCapture 객체 생성
        self.videoCapture = cv2.VideoCapture(0)
        # VideoCapture 객체 가로 세로 크기 설정
        self.videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 생성한 ImageMqttPublisher 객체를 스레드로 실행하기 위한 설정
    def connect(self):
        # 메인 스레드와 별도로 실행시키기 위해 스레드 처리(메인 스레드 종료 시 자동 종료하도록 daemon = True)
        thread = threading.Thread(target=self.__run, daemon=True)
        # 위에서 target으로 설정한 __run 메소드 실행
        thread.start()

    # thread.start() 호출 시 실행되는 메소드
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
        print('ImageMqttClient mqtt broker connected')

    # mqtt 연결이 끊어졌을 경우 자동적으로 호출되는 콜백함수
    def __on_disconnect(self, client, userdata, rc):
        print('ImageMqttClient mqtt broker disconnected')

    # 호출했을때 강제적으로 mqtt 연결이 끊기는 메소드
    def disconnect(self):
        self.client.disconnect()

    # 카메라가 받아온 정보를 전송하는 메소드
    def sendBase64(self, frame):

        # mqtt 연결이 정상적으로 이뤄지지 않아서 client 객체가 생성되지 않았을 경우 해당 메소드를 빠져나간다.
        if self.client is None:
            return
        # MQTT Broker가 연결되어 있지 않을 경우
        if not self.client.is_connected():
            return
        # JPEG 포맷으로 인코딩
        retval, bytes = cv2.imencode('.jpg', frame)
        # 인코딩이 실패한 경우
        if not retval:
            print('image encoding fail')
            return
        # Base64 문자열로 인코딩
        b64_bytes = base64.b64encode(bytes)
        self.client.publish(self.pubTopic, b64_bytes)

    # sendBase64() 지속적으로 호출하여 카메라 정보를 끊임없이 발행하는 메소드
    def publish(self):
        while True:
            if self.videoCapture.isOpened():
                # 제대로 프레임을 읽으면 retval값이 True, 실패하면 False가 나타난다. frame에 읽은 프레임이 반환됨.
                retval, frame = self.videoCapture.read()
                if not retval:
                    print('video capture fail')
                    break
                self.sendBase64(frame)

            else:
                break


if __name__ == '__main__':
    videoCapture = cv2.VideoCapture(0)
    videoCapture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    videoCapture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    imageMqttPublisher = ImageMqttPublisher('192.168.3.163', 1883, '/camerapub')
    imageMqttPublisher.connect()

    while True:
        if videoCapture.isOpened():
            retval, frame = videoCapture.read()
            if not retval:
                print('video capture fail')
                break
            imageMqttPublisher.sendBase64()

        else:
            break

    imageMqttPublisher.disconnect()
    videoCapture.release()