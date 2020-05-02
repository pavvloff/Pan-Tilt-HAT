import argparse
from pth.camera import runCameraView, platform
from pth.updater import runUpdaterView
from pth.custombottle import StoppableServer
from pth.processing import Processing
from pth.imgclassifier import imageClassification
from bottle import Bottle
import threading
import time

stopcommand = 'exit'

def main():
  parser = argparse.ArgumentParser(description='Run the camera software.')
  parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
  args = parser.parse_args()

  app = Bottle()
  server = StoppableServer(host='0.0.0.0', port=8001)
  
  proc = imageClassification(app)
  proc.start()

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
