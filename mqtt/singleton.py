# 클래스를 싱글톤으로 관리하기 위한 설정을 해준 클래스
class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

# 속도 정보를 저장하기 위한 싱글톤 객체를 만드는 클래스
class SingletonSpeed(metaclass=SingletonType):
    def __init__(self):
        self.__speed = 0
        print("singletonSpeed 생성")

    # getter 역할
    def get_speed(self):  # getter
        if self.__speed < 0:
            return self.__speed * (-1)
        return self.__speed

    # setter 역할
    def set_speed(self, value):  # setter
        self.__speed = value


