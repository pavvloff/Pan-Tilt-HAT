import argparse
from pth.camera import runCameraView
from pth.updater import runUpdaterView, command
from pth.custombottle import StoppableServer
from bottle import Bottle
import threading

def main():
  parser = argparse.ArgumentParser(description='Run the camera software.')
  parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
  args = parser.parse_args()

  app = Bottle()
  server = StoppableServer(host='0.0.0.0', port=8001)

  runCameraView(app, args.static)
  runUpdaterView(app, server)

  app.run(server=server)

  if command == "refresh":
    exit(-1)
  else:
    exit(0)


if __name__ == '__main__':
  main()
