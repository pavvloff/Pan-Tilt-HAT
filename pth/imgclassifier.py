import io
import picamera
import pth.processing as pc
from PIL import Image
import time
import tensorflow as tf
import numpy as np
import multiprocessing as mp
import ctypes

class ImageExtractor(pc.Sender):
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


class ImageClassifier(pc.Processor):
  """docstring for ImageSaver"""
  def __init__(self, **kwargs):
    super(ImageClassifier, self).__init__(**kwargs)
    self.filename = kwargs.get('output')
    self.resolution = kwargs.get('resolution')
    self.outresolution = kwargs.get('outresolution')
    self.outframes = kwargs.get('outframes')
    self.model_path = kwargs.get('model_path')
    assert self.outframes[0] > 1
    assert self.outframes[1] > 1

  def init(self):
    self.interpreter = tf.lite.Interpreter(self.model_path)
    self.interpreter.allocate_tensors()
    self.input_index = self.interpreter.get_input_details()[0]['index']
    self.output_index = self.interpreter.get_output_details()[0]['index']
  def processItem(self, item):
    image = Image.frombytes("RGB", self.resolution, item)
    i = 0
    for row in range(self.outframes[1]):
      for column in range(self.outframes[0]):
        x = (self.resolution[0] - self.outresolution[0]) // (self.outframes[0] - 1) * column
        y = (self.resolution[1] - self.outresolution[1]) // (self.outframes[1] - 1) * row
        # Save the image
        cropped = image.crop((x, y, x + self.outresolution[0], y + self.outresolution[1]))
        cropped.save(self.filename + str(i) + '.jpg')
        # Prepare the data
        arr = np.asarray(cropped).reshape((1, self.outresolution[0], self.outresolution[1], 3))
        arr = arr.astype(np.dtype(float)) / 127.5 - 1.0
        # Invoke the interpreter
        self.interpreter.set_tensor(self.input_index, arr)
        self.interpreter.invoke()
        val = interpreter.get_tensor(self.output_index)[0][0]
        # Store the results
        self.sharedValue[i] = val
        
        i += 1
    time.sleep(1.0)
    return 1

processor = None

def imageClassification(app):
  global processor
  processor = pc.Processing(
    senderClass = ImageExtractor,
    processorClass = ImageClassifier,
    resolution = (640, 480),
    outresolution = (160, 160),
    outframes = (5, 3),
    output = './static/frame',
    model_path = './models/ninamodel.20200413.e100.tflite',
    sharedValueClass = lambda: mp.Array(ctypes.c_float, 5 * 3))
  
  @app.get('/getvalues')
  def cmd():
    global processor
    return ','.join(map(str,processor.getValue()))

  return processor
