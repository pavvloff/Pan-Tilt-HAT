import argparse
from pth.camera import runCameraView

def main():
	parser = argparse.ArgumentParser(description='Run the camera software.')
	parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
        parser.add_argument('-f', '--freq', type=int, help='Motor update frequency', default = 50)
	args = parser.parse_args()

	runCameraView(root = args.static, freq = args.freq)

if __name__ == '__main__':
	main()
