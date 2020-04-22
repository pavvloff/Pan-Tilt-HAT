#!/usr/bin/python

import time
import math
import smbus

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:

  __MODE1              = 0x00
  __MODE2              = 0x01
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09

  def __init__(self, address=0x40, freq = 50):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.stop()
    self.setPWMFreq(freq)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    return self.bus.read_byte_data(self.address, reg)
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    prescale = int(math.floor(prescaleval + 0.5))

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, prescale)
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setBlockPWM(self, motor0, motor1):
    assert motor0 >= 0
    assert motor1 >= 0
    assert motor0 < 4096
    assert motor1 < 4096
    data = [0, 0,
            motor0 & 0xFF, (motor0 >> 8) & 0x0F,
            0, 0,
            motor1 & 0xFF, (motor1 >> 8) & 0x0F]
    self.bus.write_i2c_block_data(self.address, self.__LED0_ON_L, data)
    
  def start(self):
    self.write(self.__MODE2, 0x04)
    
  def stop(self):
    self.write(self.__MODE2, 0x00)
