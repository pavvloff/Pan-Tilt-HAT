import argparse
from pth.camera import runCameraView, platform
from pth.updater import runUpdaterView
from pth.custombottle import StoppableServer
from bottle import Bottle
import threading
import time

def main():
  parser = argparse.ArgumentParser(description='Run the camera software.')
  parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
  args = parser.parse_args()

  app = Bottle()
  server = StoppableServer(host='0.0.0.0', port=8001)

  runCameraView(app, args.static)
  runUpdaterView(app, server)

  app.run(server=server)

  print(server.command)
  try:
    # Trying to peacefully 
    platform.command = 'exit'
    time.sleep(0.2)
  except AttributeError as er:
    pass

  if server.command == "refresh":
    exit(255)
  else:
    exit(0)


if __name__ == '__main__':
  main()
