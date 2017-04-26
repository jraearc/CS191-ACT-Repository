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
	def __init__(self):
		self.facing = '^'
		self.x = 0
		self.y = 0
		self.orient_vector = (0, 1, 0)
		self.up_vector = (0, 0, 1)
		self.listenerObject = pyglet.media.get_audio_driver().get_listener()
		self.listenerObject.position = (self.x, self.y, 0)
		self.listenerObject.forward_orientation = (0, 1, 0)
		self.listenerObject.up_orientation = (0, 0, 1)

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
	def __init__(self,cols,rows,player):
		self.start = False
		self.player = player
		self.forward = False
		self.backward = False
		self.move = 0
		self.mapElements = []
		
		self.cols = cols
		self.rows = rows
		
		for x in range(self.cols):
			self.mapElements.append([])
			for y in range(self.rows):
				self.mapElements[x].append(Space())
		# self.mapElements[0][20].event = Battle1(self.player,'tone5.wav',10,0,20)
		# self.mapElements[0][20].flag = True

		self.footstep = pyglet.media.load('footstep.wav', streaming=False)

	# playAudio()
	# Creation Date: 2/2/2017
	# Plays the audio associated with the element
	# Return type: None
	def playFootstep(self):
		self.footstep.play()

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
				self.playFootstep()
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
				self.playFootstep()
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
						print "Bump" # every bump should be a sound instead
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
				self.playFootstep()
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
				self.playFootstep()
				print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
				if self.mapElements[self.player.x][self.player.y].event != None and self.mapElements[self.player.x][self.player.y].flag:
					states.append(self.mapElements[self.player.x][self.player.y].event)
					self.mapElements[self.player.x][self.player.y].flag = False
				self.move = 30
			else:
				self.move -= 1


class Scene1:
	def __init__(self):
		self.t = 0
		self.start = False
		self.text = ["*ship horn*", "This is your stop.", "Aye.", "*marching*", "The king requests your presence at the castle.", "Let's not keep him waiting."]
		self.soundfiles = ["shiphorn.mp3", "dialog1_1.mp3", "dialog1_2.mp3", "dialog1_3.mp3", "dialog1_4.mp3", "dialog1_5.mp3", "castleentry.mp3"]
		self.positions = [(1, 15, 2), (2, 1, 2), (0, 0, 2), (3, 2, 2)]
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.dialogOddPlayer = pyglet.media.Player()
		self.dialogEvenPlayer = pyglet.media.Player()
		self.audioChannels = [self.backgroundSoundPlayer, self.dialogOddPlayer, self.dialogEvenPlayer, self.backgroundSoundPlayer2]
		for i in range(len(self.audioChannels)):
			self.audioChannels[i].position = self.positions[i]
		self.backgroundSoundFile = pyglet.media.load(self.soundfiles[0])
		self.dialogSoundFile = pyglet.media.load(self.soundfiles[1])
	def update(self,dt):
		if not self.start:
			self.start = True
			print self.text[self.t]
			self.audioChannels[0].queue(self.backgroundSoundFile)
			self.audioChannels[0].play()
			self.t += 1
		@window.event
		def on_key_press(symbol, modifiers):
			if self.t < len(self.text):
				print self.text[self.t]
				self.dialogSoundFile = pyglet.media.load(self.soundfiles[self.t])
				if (self.t % 2 == 0 and self.t < 3) or (self.t % 2 == 1 and self.t > 3):
					self.audioChannels[2].queue(self.dialogSoundFile)
					self.audioChannels[2].play()
				elif self.t == 3:
					self.audioChannels[3].queue(self.dialogSoundFile)
					self.audioChannels[0].pause()
					self.audioChannels[3].play()
					self.dialogSoundFile = pyglet.media.load(self.soundfiles[6])
					self.audioChannels[0].queue(self.dialogSoundFile)
					self.audioChannels[0].next()
					self.audioChannels[0].play()
				else:
					self.audioChannels[1].queue(self.dialogSoundFile)
					self.audioChannels[1].play()
						
				self.t += 1
			else:
				states.remove(self)
				states.append(map1)

class Transition1:
	def update(self,dt):
		states.remove(map1)
		states.remove(self)
		states.append(Scene2())

class Scene2:
	def __init__(self):
		self.t = 0
		self.start = False
		self.text = ["*trumpet*", "It seems quite lively around here.", "The king wanted to celebrate your return with a feast.", "As always, he has gone overboard.",
		"Ah! My loyal knight! You have finally arrived. The festivities have already started without you!", 
		"Milord, I am grateful, but I am hardly worthy of such honor.", "Nonsense! My greatest knight surely deserves at least this much!",
		"To continue serving my liege is the only reward I desire.", "Then I shall grant you that as well! But for now, we feast!", "*cheering*",
		"Prince! Prince! Now, where is that son of mine?", "He is feeling a bit under the weather and has retreated to his bedchambers your majesty.",
		"He did not wish to sully the festivities with his disagreeable pallor.", "Bah! He should have at least been here to receive the guest of honor!",
		"My knight would not be able to witness his complexion anyway, no matter how disagreeable it is!", "My liege, I am still able to perceive others' discomfort.",
		"And I could hardly ask the crown prince to trouble himself on my account.", "Well I shall simply have to trouble him on mine! Hah!",
		"Under the weather! The lad spends entirely too much time in the royal library!", "He needs exercise! Perhaps you would be willing to whip him into shape?",
		"My son could learn a thing or two from someone like you!", "With all due respect, sire, the prince would benefit from a more... conventional tutor.",
		"True, few easily master your unique swordsmanship.", "If I recall, my captain of the guards desired to measure his strength against yours.",
		"I would be most grateful to be granted this selfish request.", "What say you, Sir Knight?", "I am at your service, your grace.",
		"Very well! This duel shall be a fine accompaniment to today's celebration!", "Fight with courage and honor!", "Commence!"]
		self.soundfiles = ["trumpet.wav", "dialog2_1.mp3", "dialog2_2.mp3", "dialog2_3.mp3", "dialog2_4.mp3", "dialog2_5.mp3", "dialog2_6.mp3", "dialog2_7.mp3", 
		"dialog2_8.mp3", "cheering.mp3", "dialog2_9.mp3", "dialog2_10.mp3", "dialog2_11.mp3", "dialog2_12.mp3", "dialog2_13.mp3", "dialog2_14.mp3",
		"dialog2_15.mp3", "dialog2_16.mp3", "dialog2_17.mp3", "dialog2_18.mp3", "dialog2_19.mp3", "dialog2_20.mp3", "dialog2_21.mp3", "dialog2_22.mp3",
		"dialog2_23.mp3", "dialog2_24.mp3", "dialog2_25.mp3", "dialog2_26.mp3", "dialog2_27.mp3", "dialog2_28.mp3"]
		self.positions = [(2, 35, 2), (3, 10, 2), (1, 9, 2), (4, 11, 2), (2, 12, 2)]
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.backgroundSoundPlayer3 = pyglet.media.Player()
		self.dialogOddPlayer = pyglet.media.Player()
		self.dialogEvenPlayer = pyglet.media.Player()
		self.audioChannels = [self.backgroundSoundPlayer, self.dialogOddPlayer, self.dialogEvenPlayer, self.backgroundSoundPlayer2, self.backgroundSoundPlayer3]
		for i in range(len(self.audioChannels)):
			self.audioChannels[i].position = self.positions[i]
		self.backgroundSoundFile = pyglet.media.load(self.soundfiles[0])
		self.dialogSoundFile = pyglet.media.load(self.soundfiles[1])
	def update(self,dt):
		if not self.start:
			self.start = True
			print self.text[self.t]
			self.audioChannels[0].queue(self.backgroundSoundFile)
			self.audioChannels[0].play()
			self.t += 1
		@window.event
		def on_key_press(symbol, modifiers):
			if self.t < len(self.text):
				print self.text[self.t]
				self.dialogSoundFile = pyglet.media.load(self.soundfiles[self.t])
				if (self.t >= 10 and self.t <= 14) or (self.t >= 17 and self.t <= 25) or self.t > 26:
					self.audioChannels[1].queue(self.dialogSoundFile)
					self.audioChannels[1].play()
				elif (self.t % 2 == 1 and self.t < 9) or (self.t >= 15 and self.t <= 16) or (self.t == 26):
					self.audioChannels[2].queue(self.dialogSoundFile)
					self.audioChannels[2].play()
				elif self.t == 9:
					self.audioChannels[4].queue(self.dialogSoundFile)
					self.audioChannels[0].pause()
					self.audioChannels[4].play()
					self.dialogSoundFile = pyglet.media.load(self.soundfiles[9])
					self.audioChannels[0].queue(self.dialogSoundFile)
					self.audioChannels[0].next()
					self.audioChannels[0].play()
				else:
					self.audioChannels[1].queue(self.dialogSoundFile)
					self.audioChannels[1].play()
				self.t += 1
			else:
				states.remove(self)
				states.append(Battle1(player))

class Battle1:
	def __init__(self,player):
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.backgroundSoundPlayer3 = pyglet.media.Player()
		self.backgroundSoundPlayer4 = pyglet.media.Player()
		self.backgroundSoundPlayer5 = pyglet.media.Player()
		self.backgroundSoundPlayer.position = (player.x-1, player.y, 0)
		self.backgroundSoundPlayer.queue(pyglet.media.load("battlemode.mp3"))
		self.backgroundSoundPlayer2.queue(pyglet.media.load("sword.wav"))
		self.backgroundSoundPlayer2.position = (player.x-1, player.y, 0)
		self.backgroundSoundPlayer3.queue(pyglet.media.load("hit.wav"))
		self.backgroundSoundPlayer3.position = (player.x-1, player.y, 0)
		self.text = ["(You are fighting the captain of the guards!)"]
		self.backgroundSoundPlayer4.queue(pyglet.media.load("battlebg.mp3"))
		self.backgroundSoundPlayer4.play()
		self.t = 0
		self.start = False
		self.str = 5
		self.EnemyHealth = 20
		self.player = player
		self.block = False
		self.willExit = False
	def update(self,dt):
		if not self.start:
			print self.text[self.t]
			self.backgroundSoundPlayer.play()
			self.t += 1
			self.start = True
		if(self.player.health > 0):
			if random.randint(1,50) == 1:
				if self.block:
					print "*block*"
				else:
					self.backgroundSoundPlayer3.play()
					self.backgroundSoundPlayer3.queue(pyglet.media.load("hit.wav"))
					self.player.health = float(self.player.health) - float(self.str)
					self.player.health = int(self.player.health)
					print "Health: " + str(self.player.health) + "/100"
			@window.event
			def on_key_press(symbol, modifiers):
				if symbol == pyglet.window.key.SPACE:
					self.backgroundSoundPlayer2.play()
					self.backgroundSoundPlayer2.queue(pyglet.media.load("sword.wav"))
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
			if self.EnemyHealth <= 0:
				print "Victory!"
				self.backgroundSoundPlayer4.pause()
				self.backgroundSoundPlayer5.queue(pyglet.media.load("win.mp3"))
				self.backgroundSoundPlayer5.play()
				states.remove(self)
				states.append(Scene3())
			if self.player.health <= 0:
				self.backgroundSoundPlayer4.pause()
				self.backgroundSoundPlayer5.queue(pyglet.media.load("lose.wav"))
				self.backgroundSoundPlayer5.play()
		else:
			print "Defeat..."
			states.remove(self)

class Scene3:
	def __init__(self):
		self.t = 0
		self.start = False
		self.text = ["A fine display! Such is only to be expected from among the kingdoms' finest!", "I thank you for the match. I have learned much.", 
		"I too, am grateful for this chance to cross swords.", "By my lord's leave, I shall return to my post.", "Your dedication is to be recognized, captain.",
		"I am pleased to know that your safety has not suffered in my absence.", "With the both of you here, the kingdom has nothing to fear!", 
		"I only wish that my son was here to witness your strength.", "My king, has the prince not been at your side for some time now?", "What do you-",
		"*stab*", "Your majesty!", "*thud*", "*screaming*", "The knight has murdered the king!", "What vile treachery!", "He flees!", "Guards! Guards!", 
		"Was he only fooling us all this time?", "Throw him in the dungeon!", "Hang him!", "Off with his head!", "Give us back our king!"]
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
	
player = Player()
player.x = 1
map1 = Map(3,10,player) # character starts in the middle of a market street, can place market sounds to the sides, set obstacle to true
map1.mapElements[1][9].event = Transition1()
map1.mapElements[1][9].flag = True
states = []
states.append(Scene1())

def update(dt):
	if len(states):
		states[-1].update(dt)
	else:
		pyglet.app.exit()
		
pyglet.clock.schedule_interval(update, 1.0/60.0)
pyglet.app.run()