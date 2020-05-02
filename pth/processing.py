import multiprocessing as mp
import multiprocessing.sharedctypes as st
import random

STREAM_END='end'
ACK='ack'

def isEnd(obj):
  return isinstance(obj, str) and obj == STREAM_END

def isAck(obj):
  return isinstance(obj, str) and obj == ACK

class Sender(mp.Process):
  def __init__(self, **kwargs):
    parentPipe = kwargs.get('parentPipe')
    finishEvent = kwargs.get('finishEvent')
    assert parentPipe is not None
    assert finishEvent is not None
    super(Sender, self).__init__()
    self.parentPipe = parentPipe
    self.finishEvent = finishEvent
    self.daemon = True
  def isFinished(self):
    return self.finishEvent.is_set()

  def init(self):
    pass
  def getItem(self):
    return "item"

  def run(self):
    self.init()
    while not self.isFinished():
      item = self.getItem()
      ack = self.parentPipe.recv()
      self.parentPipe.send(item)
    ack = self.parentPipe.recv()
    self.parentPipe.send(STREAM_END)

class Processor(mp.Process):

  def __init__(self, **kwargs):
    childPipe = kwargs.get('childPipe')
    sharedValue = kwargs.get('sharedValue')
    assert childPipe is not None
    assert sharedValue is not None
    super(Processor, self).__init__()
    self.childPipe = childPipe
    self.sharedValue = sharedValue
    self.daemon = True
  def setSharedValue(self, val):
    self.sharedValue.value = val

  def init(self):
    """Perform resource intensive initialization"""
    pass
  def processItem(self, item):
    """Process item and return result"""
    return random.randrange(100)

  def run(self):
    self.init()
    self.childPipe.send(ACK)
    while True:
      item = self.childPipe.recv()
      if isEnd(item):
        break
      self.setSharedValue(self.processItem(item))
      self.childPipe.send(ACK)

class Processing:
  """Parallel processing in 2 separate threads
  The Sender thread is responsible for producing items that would be processed.
  The Processor thread is responsible for processing and writing the result to the shared value
  """
  def __init__(self, senderClass = Sender, processorClass = Processor, sharedValueClass = lambda: mp.Value('i', 0), **kwargs):
    self.sharedValue = sharedValueClass()
    self.parentPipe, self.childPipe = mp.Pipe()
    self.finishEvent = mp.Event()

    self.sender = senderClass(
      parentPipe = self.parentPipe,
      finishEvent = self.finishEvent,
      **kwargs)
    self.processor = processorClass(
      childPipe = self.childPipe,
      sharedValue = self.sharedValue,
      **kwargs)

  def start(self):
    self.sender.start()
    self.processor.start()

  def stop(self):
    self.finishEvent.set()
    self.sender.join()
    self.processor.join()

  def getValue(self):
    return self.sharedValue
