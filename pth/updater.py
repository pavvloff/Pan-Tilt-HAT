import bottle

server = None
command = ""

def runUpdaterView(app, srv, root = '.'):
  global server
  server = srv

  @app.post('/srvcmd')
  def cmd():
    global server
    global command
    command = bottle.request.body.read().decode()
    print(command)
    if command == "shutdown" or command == "refresh":
      server.stop()
    return 'OK'
