import argparse
from pth.camera import runCameraView, platform
from pth.updater import runUpdaterView
from pth.custombottle import StoppableServer
from pth.processing import Processing
from pth.imgclassifier import ImageExtractor, ImageSaver
from bottle import Bottle
import threading
import time

def main():
  parser = argparse.ArgumentParser(description='Run the camera software.')
  parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
  args = parser.parse_args()

  proc = Processing(
    senderClass = ImageExtractor,
    processorClass = ImageSaver,
    resolution = (640, 480),
    outresolution = (160, 160),
    outframes = (5, 3),
    output = './static/frame')
  proc.start()

  app = Bottle()
  server = StoppableServer(host='0.0.0.0', port=8001)

  stopcommand = 'exit'

  def stopcallback(command):
    global stopcommand 
    proc.stop()
    server.stop()
    platform.command = 'exit'
    time.sleep(1.5)
    stopcommand = command

  runCameraView(app, args.static)
  runUpdaterView(app, stopcallback)
  app.run(server=server)

  if stopcommand == 'refresh':
    exit(255)
  else:
    exit(0)


if __name__ == '__main__':
  main()
