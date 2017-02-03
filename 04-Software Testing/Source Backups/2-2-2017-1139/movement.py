import pyglet
from pyglet.gl import *

window = pyglet.window.Window(200,100,caption = "Dark Night")
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)
batch = pyglet.graphics.Batch()

@window.event
def on_resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, 800, 0, 600, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    return pyglet.event.EVENT_HANDLED

class Space:
    def __init__(self):
        self.obstacle = False

# NOTE FOR POSITIONAL AUDIO CONFIGURATIONS IN
# ALL GAME ELEMENT CLASSES:
# The 'position' attribute of pyglet.media.Player
# takes care of the 3D audio in-game.
# It is a 3-tuple attribute that has x, y and z values.
# Remember to set z position to 2 so that audio
# gaps will not be heard on the headphones.

class Player():
    def __init__(self,facing,x,y):
        self.facing = facing
        self.x = x
        self.y = y
        self.listenerObject = pyglet.media.get_audio_driver().get_listener()
        self.listenerObject.position = (0, 0, 2)
    def setPlayerPosition(self,facing,x,y):
        self.facing = facing
        self.x = x
        self.y = y
    def updateListener(self):
        self.listenerObject.position = (self.x, self.y, 2)

class MapElementList:
    def __init__(self):
        self.MapObjects = []
    def addObjectToMap(newObject):
        self.MapObjects.append(newObject)

# NOTE FOR CLASS 'MapElement':
# Make sure that source audio file is not set to stereo.
# Use audio-editing software (Adobe Audition or Audacity)
# to change channel mode from stereo to mono.

class MapElement:
    def __init__(self,x,y,sourceAudio):
        self.elementAudio = pyglet.media.Player()
        elementAudio.position = (x, y, 2)

class Map:
    def __init__(self):
        self.player = Player('up',0,0)
        self.mapElements = MapElementList()
    def update(self, dt):
        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.W:
                if self.player.facing == 'up':
                    self.player.y += 1
                elif self.player.facing == 'down':
                    self.player.y -= 1
                elif self.player.facing == 'left':
                    self.player.x -= 1
                elif self.player.facing == 'right':
                    self.player.x += 1
            elif symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.S:
                if self.player.facing == 'up':
                    self.player.y -= 1
                elif self.player.facing == 'down':
                    self.player.y += 1
                elif self.player.facing == 'left':
                    self.player.x += 1
                elif self.player.facing == 'right':
                    self.player.x -= 1
            elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.A:
                if self.player.facing == 'up':
                    self.player.facing = 'left'
                elif self.player.facing == 'down':
                    self.player.facing = 'right'
                elif self.player.facing == 'left':
                    self.player.facing = 'down'
                elif self.player.facing == 'right':
                    self.player.facing = 'up'
            elif symbol == pyglet.window.key.RIGHT or symbol == pyglet.window.key.D:
                if self.player.facing == 'up':
                    self.player.facing = 'right'
                elif self.player.facing == 'down':
                    self.player.facing = 'left'
                elif self.player.facing == 'left':
                    self.player.facing = 'up'
                elif self.player.facing == 'right':
                    self.player.facing = 'down'
            self.player.updateListener()
            print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"

@window.event
def on_draw():
    window.clear()
    batch.draw()
    
states = []
states.append(Map())

def update(dt):
    if len(states):
        states[-1].update(dt)
    else:
        pyglet.app.exit()
        
pyglet.clock.schedule_interval(update, 1.0/60.0)
pyglet.app.run()