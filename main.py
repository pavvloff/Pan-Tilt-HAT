import argparse
from pth.camera import runCameraView
from pth.updater import runUpdaterView
import threading

class CamControl(threading.Tread):
	"""docstring for camera"""
	def __init__(self, root, freq):
		super(CamControl, self).__init__()
		self.daemon = True
		self.root = root
		self.freq = freq
	def run(self):
		runCameraView(self.root, self.freq)
		

def main():
	parser = argparse.ArgumentParser(description='Run the camera software.')
	parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
        parser.add_argument('-f', '--freq', type=int, help='Motor update frequency', default = 100)
	args = parser.parse_args()

	camThread = CamControl(root = args.static, freq = args.freq)
	camThread.start()

	runUpdaterView()

if __name__ == '__main__':
	main()
