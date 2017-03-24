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
#
# Version 0.2
# - Updated listener and navigation to recognize correct sound orientation (depends where player is facing at).
#   (Rae, 2/16/2017)
# - Updated navigation to respond to map limits. (Ethan, 2/16/2017)
# - Updated sound files. (Rae/Hans, 2/15/2017)
#
# Version 0.3
# - Added event triggers to game. (Ethan, 3/1/2017)
# - Updated sound files. (Rae, 3/2/2017)
# - Added BattleMode, to be incorporated in future versions. (Rae, 3/2/2017)
# - Formulating plot, to be incorporated in final release. (Hans/Rae/Ethan, 3/2/2017)
# - Improved BattleMode, allows game to randomly incur damages to player. (Rae, 3/2/2017)

#define
import random
import pyglet
from pyglet.gl import *

pyglet.options['audio'] = ('openal', 'silent')

from pyglet.media import *

window = pyglet.window.Window(200,100,caption = "Dark Night")
window.set_location(window.screen.width/2 - window.width/2, window.screen.height/2 - window.height/2)
batch = pyglet.graphics.Batch()
keys = pyglet.window.key.KeyStateHandler()
window.push_handlers(keys)

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
        self.event = None
        self.flag = False

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
        self.orient_vector = (0, 1, 0)
        self.up_vector = (0, 0, 1)
        self.listenerObject = pyglet.media.get_audio_driver().get_listener()
        self.listenerObject.position = (self.x, self.y, 0)
        self.listenerObject.forward_orientation = (0, 1, 0)
        self.listenerObject.up_orientation = (0, 0, 1)
        self.soundFile = pyglet.media.load('footstep.wav', streaming=False)

        self.health = 100
        self.str = 5

    # updateListener()
    # Creation Date: 2/2/2017
    # Sets the listener position to the current data in the object
    # Return type: None
    def updateListener(self):
        self.listenerObject.position = (self.x, self.y, 0)
        self.listenerObject.forward_orientation = self.orient_vector
        self.listenerObject.up_orientation = self.up_vector

    # playAudio()
    # Creation Date: 2/2/2017
    # Plays the audio associated with the element
    # Return type: None
    def playAudio(self):
        self.updateListener()
        self.soundFile.play()

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

    # pauseAudio()
    # Creation Date: 3/3/2017
    # Pauses the audio associated with the map element
    # Return type: None
    def pauseAudio(self):
        self.elementAudio.pause()

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
    	self.start = False
        self.player = Player('^',0,0)
        self.forward = False
        self.backward = False
        self.move = 0
        self.mapElements = []
        
        self.cols = 100
        self.rows = 100
        
        for x in range(self.cols):
            self.mapElements.append([])
            for y in range(self.rows):
                self.mapElements[x].append(Space())
        self.mapElements[0][20].event = BattleMode(self.player,'tone5.wav',10,0,20)
        self.mapElements[0][20].flag = True

    # update(dt)
    # REQUIRED PYGLET METHOD
    # Updates the frame of the Pyglet window
    def update(self, dt):
    	if not self.start:
    		self.start = True
    		print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.W:
                self.forward = True
            elif symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.S:
                self.backward = True
            elif symbol == pyglet.window.key.LEFT or symbol == pyglet.window.key.A:
                if self.player.facing == '^':
                    self.player.facing = '<'
                    self.player.orient_vector = (-1, 0, 0)
                elif self.player.facing == 'v':
                    self.player.facing = '>'
                    self.player.orient_vector = (1, 0, 0)
                elif self.player.facing == '<':
                    self.player.facing = 'v'
                    self.player.orient_vector = (0, -1, 0)
                elif self.player.facing == '>':
                    self.player.facing = '^'
                    self.player.orient_vector = (0, 1, 0)
                self.player.updateListener()
                self.player.playAudio()
                print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
            elif symbol == pyglet.window.key.RIGHT or symbol == pyglet.window.key.D:
                if self.player.facing == '^':
                    self.player.facing = '>'
                    self.player.orient_vector = (1, 0, 0)
                elif self.player.facing == 'v':
                    self.player.facing = '<'
                    self.player.orient_vector = (-1, 0, 0)
                elif self.player.facing == '<':
                    self.player.facing = '^'
                    self.player.orient_vector = (0, 1, 0)
                elif self.player.facing == '>':
                    self.player.facing = 'v'
                    self.player.orient_vector = (0, -1, 0)
                self.player.updateListener()
                self.player.playAudio()
                print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
        @window.event
        def on_key_release(symbol, modifiers):
            if symbol == pyglet.window.key.UP or symbol == pyglet.window.key.W:
                self.forward = False
                self.move = 0
            elif symbol == pyglet.window.key.DOWN or symbol == pyglet.window.key.S:
                self.backward = False
                self.move = 0
        if self.forward:
        	if self.move <= 0:
	            if self.player.facing == '^':
	                if self.player.y+1<self.rows and self.mapElements[self.player.x][self.player.y+1].obstacle == False:
	                    self.player.y += 1
	                else:
	                    print "Bump"
	            elif self.player.facing == 'v':
	                if self.player.y-1>=0 and self.mapElements[self.player.x][self.player.y-1].obstacle == False:
	                    self.player.y -= 1
	                else:
	                    print "Bump"
	            elif self.player.facing == '<':
	                if self.player.x-1>=0 and self.mapElements[self.player.x-1][self.player.y].obstacle == False:
	                    self.player.x -= 1
	                else:
	                    print "Bump"
	            elif self.player.facing == '>':
	                if self.player.x+1<self.cols and self.mapElements[self.player.x+1][self.player.y].obstacle == False:
	                    self.player.x += 1
	                else:
	                    print "Bump"
	            self.player.updateListener()
	            self.player.playAudio()
	            print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
	            if self.mapElements[self.player.x][self.player.y].event != None and self.mapElements[self.player.x][self.player.y].flag:
	                states.append(self.mapElements[self.player.x][self.player.y].event)
	                self.mapElements[self.player.x][self.player.y].flag = False
	            self.move = 30
	        else:
	        	self.move -= 1
        elif self.backward:
        	if self.move <= 0:
	            if self.player.facing == '^':
	                if self.player.y-1>=0 and self.mapElements[self.player.x][self.player.y-1].obstacle == False:
	                    self.player.y -= 1
	                else:
	                    print "Bump"
	            elif self.player.facing == 'v':
	                if self.player.y+1<self.rows and self.mapElements[self.player.x][self.player.y+1].obstacle == False:
	                    self.player.y += 1
	                else:
	                    print "Bump"
	            elif self.player.facing == '<':
	                if self.player.x+1<self.cols and self.mapElements[self.player.x+1][self.player.y].obstacle == False:
	                    self.player.x += 1
	                else:
	                    print "Bump"
	            elif self.player.facing == '>':
	                if self.player.x-1>=0 and self.mapElements[self.player.x-1][self.player.y].obstacle == False:
	                    self.player.x -= 1
	                else:
	                    print "Bump"
	            self.player.updateListener()
	            self.player.playAudio()
	            print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
	            if self.mapElements[self.player.x][self.player.y].event != None and self.mapElements[self.player.x][self.player.y].flag:
	                states.append(self.mapElements[self.player.x][self.player.y].event)
	                self.mapElements[self.player.x][self.player.y].flag = False
	            self.move = 30
	        else:
	        	self.move -= 1

class BattleMode:
    def __init__(self,player,sound,strength,x,y):
        self.text = ["Wild Monster Appeared!"]
        self.t = 0
        self.start = False
        self.str = strength
        self.EnemyHealth = 20
        self.EnemyPosition = (x,y+1,2) #enemy is at up position by default, we must set sound to be at front of player
        self.sound = MapElement(x,y+1,sound)
        self.player = player
        self.block = False
        self.x = x
        self.y = y
    def update(self,dt):
        if not self.start:
            print self.text[self.t]
            self.t += 1
            self.sound.playAudio()
            self.start = True
        if random.randint(1,5) == 1:
            if self.block:
            	print "*block*"
            else:
                self.player.health = float(self.player.health) - float(self.str)
                self.player.health = int(self.player.health)
                print "Health: " + str(self.player.health) + "/100"
        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.SPACE and not self.block:
                self.EnemyHealth = float(self.EnemyHealth) - float(self.player.str)
                self.EnemyHealth = int(self.EnemyHealth)
                print "Enemy Health: " + str(self.EnemyHealth)
            if symbol == pyglet.window.key.UP:
            	self.block = True
    	@window.event
    	def on_key_release(symbol, modifiers):
    		if symbol == pyglet.window.key.UP:
    			self.block = False
        if self.EnemyHealth == 0:
        	print "Wild Monster Disappeared."
        	self.sound.pauseAudio()
        	print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
        	states.remove(self)

class Scene1:
	def __init__(self):
		self.text = ["This is your stop.", "Aye.", "The king requests your presence at the castle.","Let's not keep him waiting."]
		self.t = 0
		self.start = False
	def update(self,dt):
		if not self.start:
			self.start = True
			print self.text[self.t]
			self.t += 1
		@window.event
		def on_key_press(symbol, modifiers):
			if self.t < len(self.text):
				print self.text[self.t]
				self.t += 1
			else:
				states.remove(self)
            
@window.event
def on_draw():
    window.clear()
    batch.draw()
    
states = []
states.append(Map())
states.append(Scene1())

def update(dt):
    if len(states):
        states[-1].update(dt)
    else:
        pyglet.app.exit()
        
pyglet.clock.schedule_interval(update, 1.0/60.0)
pyglet.app.run()