import argparse
from pth.camera import runCameraView

def main():
	parser = argparse.ArgumentParser(description='Run the camera software.')
	parser.add_argument('-s', '--static', type=str, help='Path to static files folder', default='.')
	args = parser.parse_args()

	runCameraView(root = args.static)

if __name__ == '__main__':
	main()