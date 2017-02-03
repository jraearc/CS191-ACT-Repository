# Dark Night
# Version 0.1
# 
# Copyright (c) 2016 Legends
# Jahziel Rae Arceo, Ethan Fredric Tan, Hans Gustaf Capiral
#
# This is a course requirement for CS 192 Software Engineering II under the
# supervision of Asst. Prof. Ma. Rowena C. Solamo of the Department of
# Computer Science, College of Engineering, University of the Philippines,
# Diliman for the AY 2015-2016
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# CHANGELOG
#
# Development phase
#
# Version 0.1
# - Initial elements created, added navigation mechanism. (Ethan, 2/1/2017)
# - Initial setup of Pyglet/Python source file. (Ethan, 2/1/2017)
# - Updated Player class to include OpenAL listener (Rae, 2/1/2017)
# - Added MapElement and MapElementList class, and updated Map class to adhere with MapElementList. (Rae, 2/1/2017)
# - Updated navigation algorithm, frame now updates even when button is on hold. (Ethan, 2/2/2017)
# - Merged navigation mechanism to OpenAL listener (Rae, 2/2/2017)
# - Added 3D sound feature (finally) to navigation (Rae, 2/2/2017)
# - Added static walking sound for navigation (Rae, 2/2/2017)
# - Testing game (through Map class) and analyzing sound elements to check if 3D audio is working (Hans, 2/2/2017)


import pyglet
from pyglet.gl import *
from pyglet.media import *

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
# Remember to set z position to 2, for elements,
# so that audio gaps will not be heard on the headphones.

class Player():
    def __init__(self,facing,x,y):
        self.facing = facing
        self.x = x
        self.y = y
        self.listenerObject = pyglet.media.get_audio_driver().get_listener()
        self.listenerObject.position = (self.x, self.y, 0)
        self.soundFile = pyglet.media.load('footstep.wav', streaming=False)

    # setPlayerPosition(facing, x, y)
    # Creation Date: 2/1/2017
    # facing is a String, x and y are both integer values.
    # Sets the player position in the audio 3D space.
    # Listener must be always updated after this call.
    # Use updateListener() to update.
    # Return type: None
    def setPlayerPosition(self,facing,x,y):
        self.facing = facing
        self.x = x
        self.y = y

    # updateListener()
    # Creation Date: 2/2/2017
    # Sets the listener position to the current data in the object
    # Return type: None
    def updateListener(self):
        self.listenerObject.position = (self.x, self.y, 0)

    # playAudio()
    # Creation Date: 2/2/2017
    # Plays the audio associated with the element
    # Return type: None
    def playAudio(self):
        self.updateListener()
        self.soundFile.play()

class MapElementList:
    def __init__(self):
        self.MapObjects = []

    # addObjectToMap(newObject)
    # Creation Date: 2/1/2017
    # Adds objects to the map object list to load
    # it to the game.
    # Return type: None
    def addObjectToMap(newObject):
        self.MapObjects.append(newObject)

# NOTE FOR CLASS 'MapElement':
# Make sure that source audio file is not set to stereo.
# Use audio-editing software (Adobe Audition or Audacity)
# to change channel mode from stereo to mono.

class MapElement:
    def __init__(self,x,y,sourceAudio):
        self.elementAudio = pyglet.media.Player()
        self.soundFile = pyglet.media.load(sourceAudio)
        self.loopSound = pyglet.media.SourceGroup(self.soundFile.audio_format, None)
        self.loopSound.loop = True
        self.loopSound.queue(self.soundFile)
        self.x = x
        self.y = y
        self.elementAudio.position = (x, y, 2)
        self.elementAudio.queue(self.loopSound)

    # playAudio()
    # Creation Date: 2/2/2017
    # Plays the audio associated with the map element
    # Return type: None
    def playAudio(self):
        self.elementAudio.play()

    # setElementPosition(x, y)
    # Creation Date: 2/2/2017
    # Sets the x and y coordinates of the map element.
    # x and y must be an integer.
    # Return type: None
    def setElementPosition(self,x,y):
        self.x = x
        self.y = y
        self.elementAudio.position = (x, y, 2)

class Map:
    def __init__(self):
        self.player = Player('up',0,0)
        self.forward = False
        self.backward = False
        self.mapElements = MapElementList()
        self.samplesource = MapElement(0, 30, 'tone5.wav')
        self.samplesource.playAudio()

    # update(dt)
    # REQUIRED PYGLET METHOD
    # Updates the frame of the Pyglet window
    def update(self, dt):
        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.W:
                self.forward = True
            elif symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.S:
                self.backward = True
            elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.A:
                if self.player.facing == 'up':
                    self.player.facing = 'left'
                elif self.player.facing == 'down':
                    self.player.facing = 'right'
                elif self.player.facing == 'left':
                    self.player.facing = 'down'
                elif self.player.facing == 'right':
                    self.player.facing = 'up'
                self.player.playAudio()
                print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
            elif symbol == pyglet.window.key.RIGHT or symbol == pyglet.window.key.D:
                if self.player.facing == 'up':
                    self.player.facing = 'right'
                elif self.player.facing == 'down':
                    self.player.facing = 'left'
                elif self.player.facing == 'left':
                    self.player.facing = 'up'
                elif self.player.facing == 'right':
                    self.player.facing = 'down'
                self.player.playAudio()
                print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
        @window.event
        def on_key_release(symbol, modifiers):
            if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.W:
                self.forward = False
            elif symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.S:
                self.backward = False
        if self.forward:
            if self.player.facing == 'up':
                self.player.y += 1
            elif self.player.facing == 'down':
                self.player.y -= 1
            elif self.player.facing == 'left':
                self.player.x -= 1
            elif self.player.facing == 'right':
                self.player.x += 1
            self.player.updateListener()
            self.player.playAudio()
            print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
        if self.backward:
            if self.player.facing == 'up':
                self.player.y -= 1
            elif self.player.facing == 'down':
                self.player.y += 1
            elif self.player.facing == 'left':
                self.player.x += 1
            elif self.player.facing == 'right':
                self.player.x -= 1
            self.player.updateListener()
            self.player.playAudio()
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
        
pyglet.clock.schedule_interval(update, 1.0/4.0)
pyglet.app.run()