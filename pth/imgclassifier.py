import io
import picamera
import processing as proc
from PIL import Image
import time

class ImageExtractor(proc.Sender):
  """docstring for ImageExtractor"""
  def __init__(self, **kwargs):
    super(ImageExtractor, self).__init__(**kwargs)
    self.resolution = kwargs.get('resolution')

  def init(self):
    self.camera = picamera.PiCamera(resolution = self.resolution)
  def getItem(self):
    stream = io.BytesIO()
    self.camera.capture(stream, format='rgb')
    stream.seek(0)
    return stream.read()


class ImageSaver(proc.Processor):
  """docstring for ImageSaver"""
  def __init__(self, **kwargs):
    super(ImageSaver, self).__init__(**kwargs)
    self.filename = kwargs.get('output')
    self.resolution = kwargs.get('resolution')
    self.outresolution = kwargs.get('outresolution')
    self.outframes = kwargs.get('outframes')
    assert self.outframes[0] > 1
    assert self.outframes[1] > 1

  def init(self):
    pass
  def processItem(self, item):
    image = Image.frombytes("RGB", self.resolution, item)
    i = 0
    for row in range(self.outframes[1]):
      for column in range(self.outframes[0]):
        x = (self.resolution[0] - self.outresolution[0]) // (self.outframes[0] - 1) * column
        y = (self.resolution[1] - self.outresolution[1]) // (self.outframes[1] - 1) * row
        cropped = image.crop((x, y, x + self.outresolution[0], y + self.outresolution[1]))
        cropped.save(self.filename + str(i) + '.jpg')
        i += 1
    time.sleep(1.0)
    return 1
