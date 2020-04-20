import bottle

def runUpdaterView(port = 8002, root = '.'):

  app = bottle.Bottle()

  @app.get('/')
  def index():
    return bottle.static_file('/static/updater/index.html', root=root)
    
  @app.route('/static/<filepath:path>')
  def server_static(filepath):
    return bottle.static_file(path.join('/static/', filepath), root=root)

  @app.route('/fonts/<filepath:path>')
  def server_fonts(filepath):
    return bottle.static_file(path.join('/static/fonts/', filepath), root=root)
    
  @app.post('/updatercmd')
  def cmd():
    command = bottle.request.body.read().decode()
    if command == 'refresh':
      exit(0)
    if command == 'exit':
      exit(1)
    return 'OK'

  app.run(host='0.0.0.0', port=port)
