import bottle

server = None

def runUpdaterView(app, srv, root = '.'):
  global server
  server = srv

  @app.post('/srvcmd')
  def cmd():
    global server
    command = bottle.request.body.read().decode()
    print(command)
    if command == "shutdown" or command == "refresh":
      server.stop(command)
    return 'OK'
