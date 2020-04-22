#!/usr/bin/python
# -*- coding:utf-8 -*-
import bottle
import PCA9685
import threading
import time
import os.path as path
import math

HORIZONTAL_MOTOR = 1
VERTICAL_MOTOR = 0
I2C_ADDRESS = 0x40

DEFAULT_FREQ = 50
MIN_VAL = int(math.floor(4096 * 0.02)) # 1.0 ms of 50 ms interval
MAX_VAL = int(math.floor(4096 * 0.06)) # 3.0 ms of 50 ms interval

class Stepper:
  def __init__(self, min_val = MIN_VAL, max_val = MAX_VAL, max_speed = (MAX_VAL - MIN_VAL)/3.0, acceleration = 20.0):
    assert min_val >= 0
    assert max_val > min_val
    assert max_speed > 0
    assert acceleration > 0
    self.speed = 0.0
    self.min_val = min_val
    self.max_val = max_val
    self.value = (self.max_val + self.min_val) / 2
    self.max_speed = max_speed
    self.acceleration = acceleration
    self.moving = False
  def update(self, dtime):
    spd = self.speed * dtime
    self.value += spd
    if self.value < self.min_val:
      self.value = self.min_val
      if self.speed < 0:
        self.speed = 0
    if self.value > self.max_val:
      self.value = self.max_val
      if self.speed > 0:
        self.speed = 0
    return self.value
  def more(self, dtime):
    if self.speed < 0:
      self.speed = 0.0
    acc = self.acceleration * dtime
    self.moving = True
    self.speed = min(self.max_speed, max(-self.max_speed, self.speed + acc))
  def less(self, dtime):
    if self.speed > 0:
      self.speed = 0.0
    acc = self.acceleration * dtime
    self.moving = True
    self.speed = min(self.max_speed, max(-self.max_speed, self.speed - acc))
  def slowDown(self, dtime):
    acc = self.acceleration * dtime
    if self.speed > acc:
      self.speed -= acc
    elif self.speed > 0:
      self.speed = 0.0
      self.moving = False
    elif self.speed < -acc:
      self.speed += acc
    elif self.speed < 0:
      self.speed = 0.0
      self.moving = False
    else:
      self.speed = 0.0
      self.moving = False
  def isMoving(self):
    return self.moving
  def recenter(self):
    self.value = (self.max_val + self.min_val) / 2
    self.speed = 0
    self.moving = True

class PlatformControl(threading.Thread):
  def __init__(self, freq = 50):
    super(PlatformControl, self).__init__()
    self.freq = freq
    self.sleep_interval = 1.0 / freq
    self.horizontal = Stepper()
    self.vertical = Stepper()
    self.moving = False
    self.daemon = True
    self.command = "stop"

  def startPlatform(self):
    self.pwm = PCA9685.PCA9685(address = I2C_ADDRESS, freq = self.freq)

  def processCommand(self, dtime):
    if self.command == 'up':
      self.vertical.less(dtime)
    elif self.command == 'down':
      self.vertical.more(dtime)
    elif self.command == 'recenter':
      self.vertical.recenter()
    else:
      self.vertical.slowDown(dtime)
    self.vertical.update(dtime)

    if self.command == 'left':
      self.horizontal.more(dtime)
    elif self.command == 'right':
      self.horizontal.less(dtime)
    elif self.command == 'recenter':
      self.horizontal.recenter()
    else:
      self.horizontal.slowDown(dtime)
    self.horizontal.update(dtime)

  def moveMotor(self):
    v_move = self.vertical.isMoving()
    h_move = self.horizontal.isMoving()

    if (v_move or h_move):
      self.pwm.setBlockPWM(int(round(self.vertical.value)), int(round(self.horizontal.value)))
      self.startMotor()
      
    else:
      self.stopMotor()

  def stopMotor(self):
    if self.moving:
      self.pwm.stop()
      self.moving = False

  def startMotor(self):
    if not self.moving:
      self.pwm.start()
      self.moving = True

  def run(self):
    self.startPlatform()
    start = time.time()
    try:
      while self.command != 'exit':
        cur = time.time()
        dtime = cur - start
        self.processCommand(dtime)
        self.moveMotor()
        start = cur
        time.sleep(min(self.sleep_interval, 0.1))
    finally:
      self.stopMotor()

platform = PlatformControl()

def runCameraView(app, root):
  platform.start()

  @app.get('/')
  def index():
    return bottle.static_file('/static/camera/index.html', root=root)
    
  @app.route('/static/<filepath:path>')
  def server_static(filepath):
    return bottle.static_file(path.join('/static/', filepath), root=root)

  @app.route('/fonts/<filepath:path>')
  def server_fonts(filepath):
    return bottle.static_file(path.join('/static/fonts/', filepath), root=root)
    
  @app.post('/cmd')
  def cmd():
    platform.command = bottle.request.body.read().decode()
    if platform.command not in frozenset(['stop', 'up', 'down', 'left', 'right', 'recenter', 'exit']):
      platform.command = 'stop'
    print(platform.command)
    return 'OK'

