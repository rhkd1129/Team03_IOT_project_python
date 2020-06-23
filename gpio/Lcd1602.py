import time
import smbus

class Lcd1602:
	def __init__(self, addr):
		self.__bus = smbus.SMBus(1)
		self.__addr = addr
		self.init()

	def init(self):
		try:
			self.send_command(0x33) # Must initialize to 8-line mode at first
			time.sleep(0.005)
			self.send_command(0x32) # Then initialize to 4-line mode
			time.sleep(0.005)
			self.send_command(0x28) # 2 Lines & 5*7 dots
			time.sleep(0.005)
			self.send_command(0x0C) # Enable display without cursor
			time.sleep(0.005)
			self.send_command(0x01) # Clear Screen
			self.__bus.write_byte(self.__addr, 0x08)
		except:
			return False
		else:
			return True

	def write_word(self, data):
		temp = data | 0x08
		self.__bus.write_byte(self.__addr ,temp)

	def send_command(self, comm):
		# 장치에게 지시
		# Send bit7-4 firstly
		buf = comm & 0xF0
		buf |= 0x04               # RS = 0, RW = 0, EN = 1
		self.write_word(buf)
		time.sleep(0.002)
		buf &= 0xFB               # Make EN = 0
		self.write_word(buf)

		# Send bit3-0 secondly
		buf = (comm & 0x0F) << 4
		buf |= 0x04               # RS = 0, RW = 0, EN = 1
		self.write_word(buf)
		time.sleep(0.002)
		buf &= 0xFB               # Make EN = 0
		self.write_word(buf)

	def send_data(self, data):
		# 디스플레이되는 데이터
		# Send bit7-4 firstly
		buf = data & 0xF0
		buf |= 0x05               # RS = 1, RW = 0, EN = 1
		self.write_word(buf)
		time.sleep(0.002)
		buf &= 0xFB               # Make EN = 0
		self.write_word(buf)

		# Send bit3-0 secondly
		buf = (data & 0x0F) << 4
		buf |= 0x05               # RS = 1, RW = 0, EN = 1
		self.write_word(buf)
		time.sleep(0.002)
		buf &= 0xFB               # Make EN = 0
		self.write_word(buf)

	def clear(self):
		self.send_command(0x01) # Clear Screen

	def openlight(self):  # Enable the backlight
		self.__bus.write_byte(0x27,0x08)
		self.__bus.close()

	def write(self, x, y, str):
		if x < 0:
			x = 0
		if x > 15:
			x = 15
		if y <0:
			y = 0
		if y > 1:
			y = 1

		# Move cursor
		addr = 0x80 + 0x40 * y + x
		self.send_command(addr)

		for chr in str:
			self.send_data(ord(chr))

if __name__ == '__main__':
	lcd = Lcd1602(0x27)
	lcd.write(1, 0, 'Hello Python')
	lcd.write(0, 1, 'AIOT class!')
