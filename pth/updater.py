import bottle

callback = None

def runUpdaterView(app, cb, root = '.'):
  global callback
  callback = cb

  @app.post('/srvcmd')
  def cmd():
    global callback
    command = bottle.request.body.read().decode()
    print(command)
    if command == "shutdown" or command == "refresh":
      callback(command)
    return 'OK'
