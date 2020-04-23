import io
import picamera
import processing as proc
from PIL import Image


class ImageExtractor(proc.Sender):
  """docstring for ImageExtractor"""
  def __init__(self, **kwargs):
    super(ImageExtractor, self).__init__(**kwargs)
    self.resolution = kwargs.get('resolution')

  def init(self):
    self.camera = picamera.PiCamera()
  def getItem(self):
    stream = io.BytesIO()
    self.camera.capture(stream, format='rgb')
    stream.seek(0)
    return stream.readall()


class ImageSaver(proc.Processor):
  """docstring for ImageSaver"""
  def __init__(self, **kwargs):
    super(ImageSaver, self).__init__(**kwargs)
    self.filename = kwargs.get('output')
    self.resolution = kwargs.get('resolution')
    self.saved = False

  def init(self):
    pass
  def processItem(self, item):
    if not self.saved:
      image = Image.frombytes(Image.RGB, self.resolution, item)
      image.save(self.filename)
    return 1
