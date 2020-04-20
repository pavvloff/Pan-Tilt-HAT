#!/usr/bin/python
# -*- coding:utf-8 -*-
import bottle
import PCA9685
import threading
import time
import os.path as path

HORIZONTAL_MOTOR = 1
VERTICAL_MOTOR = 0
I2C_ADDRESS = 0x40

class Stepper:
  def __init__(self, min_val = 400, max_val = 1800, max_speed = 3, acceleration = 0.1):
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
  def update(self):
    self.value = min(self.max_val, max(self.min_val, self.value + self.speed))
    return self.value
  def more(self):
    self.moving = True
    self.speed = min(self.max_speed, max(-self.max_speed, self.speed + self.acceleration))
  def less(self):
    self.moving = True
    self.speed = min(self.max_speed, max(-self.max_speed, self.speed - self.acceleration))
  def slowDown(self):
    if self.speed > self.acceleration:
      self.speed -= self.acceleration
    elif self.speed > 0:
      self.speed = 0.0
      self.moving = False
    elif self.speed < -self.acceleration:
      self.speed += self.acceleration
    elif self.speed < 0:
      self.speed = 0.0
      self.moving = False
  def isMoving(self):
    return self.moving


class PlatformControl(threading.Thread):
  def __init__(self, freq = 50, min_v = 0, max_v = 2500, min_h = 0, max_h = 2500):
    super(PlatformControl, self).__init__()
    self.freq = freq
    self.sleep_interval = 1.0 / freq
    self.horizontal = Stepper(min_val = min_h, max_val = max_h)
    self.vertical = Stepper(min_val = min_v, max_val = max_v)
    self.pwm = PCA9685.PCA9685(I2C_ADDRESS)
    self.pwm.setPWMFreq(self.freq)
    self.moving = False

    self.daemon = True
    self.command = "stop"

  def processCommand(self):
    if self.command == 'up':
      self.vertical.less()
    elif self.command == 'down':
      self.vertical.more()
    else:
      self.vertical.slowDown()

    if self.command == 'left':
      self.horizontal.more()
    elif self.command == 'right':
      self.horizontal.less()
    else:
      self.horizontal.slowDown()

  def moveMotor(self):
    v_move = self.vertical.isMoving()
    h_move = self.horizontal.isMoving()

    self.vertical.update()
    self.horizontal.update()

    if (v_move or h_move):
      self.startMotor()

    self.pwm.setServoPulse(HORIZONTAL_MOTOR, int(round(self.horizontal.value)))
    self.pwm.setServoPulse(VERTICAL_MOTOR, int(round(self.vertical.value)))

  def stopMotor(self):
    if self.moving:
      self.pwm.exit_PCA9685()
      self.moving = False

  def startMotor(self):
    if not self.moving:
      self.pwm.start_PCA9685()
      self.moving = True

  def run(self):
    try:
      while self.command != 'exit':
        self.processCommand()
        self.moveMotor()
        time.sleep(self.sleep_interval)
    finally:
      self.stopMotor()

platform = None

def runCameraView(port = 8001, root = '.', freq = 50):

  global platform

  platform = PlatformControl(freq)
  platform.start()

  app = bottle.Bottle()

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
    global platform
    platform.command = bottle.request.body.read().decode()
    if platform.command not in frozenset(['stop', 'up', 'down', 'left', 'right', 'exit']):
      platform.command = 'stop'
    print(platform.command)
    return 'OK'

  app.run(host='0.0.0.0', port=port)

