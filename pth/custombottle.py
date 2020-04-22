from bottle import ServerAdapter
from threading import Timer

def stopServer(server = None):
  print('stopping server now...')
  server.server_close()
  print('closed')

class StoppableServer(ServerAdapter):
  server = None

  def run(self, handler):
    from wsgiref.simple_server import make_server, WSGIRequestHandler
    if self.quiet:
      class QuietHandler(WSGIRequestHandler):
        def log_request(*args, **kw): pass
      self.options['handler_class'] = QuietHandler
    self.server = make_server(self.host, self.port, handler, **self.options)
    self.server.serve_forever()

  def stop(self):
    print('stopping server in 0.5...')
    t = Timer(0.5, stopServer, kwargs={'server':self.server})
    t.start()
    
