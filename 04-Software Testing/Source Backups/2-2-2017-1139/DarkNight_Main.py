import pyglet

pyglet.options['audio'] = ('openal', 'silent')

window = pyglet.window.Window()

class Map:
	def __init__(self):
		self.GameObjects = []
	def addObjectToMap(newObject):
		self.GameObjects.append(newObject)
	

class MainGame:
	def __init__(self, currentMap):
		self.GameMap = currentMap

@window.event
def on_draw():
    window.clear()

pyglet.app.run()