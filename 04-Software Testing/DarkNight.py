# Dark Night
# Version 1.0 Beta
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
#
# Other development versions omitted in this file
#
# Version 1.0 Beta
# - Added main menu (Rae, 4/2017)
# - Added sound channel test feature at app start (Rae, 4/2017)
# - Created plot (Ethan, 4/2017)
# - Improved 3D audio channel configurations on Scene 3 (Rae, 4/2017)

#define
import time
import random
import pyglet
from pyglet.gl import *

pyglet.options['audio'] = ('openal', 'silent')

from pyglet.media import *

EnableDialogs = False

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
		global EnableDialogs
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

		self.footstep = pyglet.media.load('soundfiles/footstep.wav', streaming=False)
		self.bump = pyglet.media.load('soundfiles/hit.wav', streaming=False)

	# playAudio()
	# Creation Date: 2/2/2017
	# Plays the audio associated with the element
	# Return type: None
	def playFootstep(self):
		self.footstep.play()

	def playBump(self):
		self.bump.play()

	# update(dt)
	# REQUIRED PYGLET METHOD
	# Updates the frame of the Pyglet window
	def update(self, dt):
		global EnableDialogs
		if not self.start:
			self.start = True
			if EnableDialogs:
				print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
		@window.event
		def on_key_press(symbol, modifiers):
			global EnableDialogs
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
				if EnableDialogs:
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
				if EnableDialogs:
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
						if EnableDialogs:
							print "Bump" # every bump should be a sound instead
						self.playBump()
				elif self.player.facing == 'v':
					if self.player.y-1>=0 and self.mapElements[self.player.x][self.player.y-1].obstacle == False:
						self.player.y -= 1
					else:
						if EnableDialogs:
							print "Bump"
						self.playBump()
				elif self.player.facing == '<':
					if self.player.x-1>=0 and self.mapElements[self.player.x-1][self.player.y].obstacle == False:
						self.player.x -= 1
					else:
						if EnableDialogs:
							print "Bump"
						self.playBump()
				elif self.player.facing == '>':
					if self.player.x+1<self.cols and self.mapElements[self.player.x+1][self.player.y].obstacle == False:
						self.player.x += 1
					else:
						if EnableDialogs:
							print "Bump"
						self.playBump()
				self.player.updateListener()
				self.playFootstep()
				if EnableDialogs:
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
						if EnableDialogs:
							print "Bump"
						self.playBump()
				elif self.player.facing == 'v':
					if self.player.y+1<self.rows and self.mapElements[self.player.x][self.player.y+1].obstacle == False:
						self.player.y += 1
					else:
						if EnableDialogs:
							print "Bump"
						self.playBump()
				elif self.player.facing == '<':
					if self.player.x+1<self.cols and self.mapElements[self.player.x+1][self.player.y].obstacle == False:
						self.player.x += 1
					else:
						if EnableDialogs:
							print "Bump"
						self.playBump()
				elif self.player.facing == '>':
					if self.player.x-1>=0 and self.mapElements[self.player.x-1][self.player.y].obstacle == False:
						self.player.x -= 1
					else:
						if EnableDialogs:
							print "Bump"
						self.playBump()
				self.player.updateListener()
				self.playFootstep()
				if EnableDialogs:
					print self.player.facing + " (" + str(self.player.x) + ", " + str(self.player.y) + ")"
				if self.mapElements[self.player.x][self.player.y].event != None and self.mapElements[self.player.x][self.player.y].flag:
					states.append(self.mapElements[self.player.x][self.player.y].event)
					self.mapElements[self.player.x][self.player.y].flag = False
				self.move = 30
			else:
				self.move -= 1


class Scene1:
	def __init__(self):
		global EnableDialogs
		global player
		global map1
		player = Player()
		player.x = 1
		map1 = Map(3,10,player) # character starts in the middle of a market street, can place market sounds to the sides, set obstacle to true
		map1.mapElements[1][9].event = Transition1()
		map1.mapElements[1][9].flag = True
		self.t = 0
		self.start = False
		self.text = ["*ship horn*", "This is your stop.", "Aye.", "*marching*", "The king requests your presence at the castle.", "Let's not keep him waiting.", "Press and hold the Up arrow key or W to walk straight up to your destination."]
		self.soundfiles = ["shiphorn.mp3", "dialog1_1.mp3", "dialog1_2.mp3", "dialog1_3.mp3", "dialog1_4.mp3", "dialog1_5.mp3", "dialog1_6.mp3", "castleentry.mp3"]
		self.lengths = [3, 2, 1, 3, 3, 2, 5]
		self.positions = [(1, 15, 2), (2, 1, 2), (0, 0, 2), (3, 2, 2)]
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.dialogOddPlayer = pyglet.media.Player()
		self.dialogEvenPlayer = pyglet.media.Player()
		self.audioChannels = [self.backgroundSoundPlayer, self.dialogOddPlayer, self.dialogEvenPlayer, self.backgroundSoundPlayer2]
		for i in range(len(self.audioChannels)):
			self.audioChannels[i].position = self.positions[i]
		self.backgroundSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[0])
		self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[1])
	def update(self,dt):
		global EnableDialogs
		if not self.start:
			self.start = True
			if EnableDialogs:
				print self.text[self.t]
			self.audioChannels[0].queue(self.backgroundSoundFile)
			self.audioChannels[0].play()
			time.sleep(3)
			self.t += 1
		if self.t > 0 and self.t < len(self.text):
			if EnableDialogs:
				print self.text[self.t]
			self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[self.t])
			if (self.t % 2 == 0 and self.t < 3) or (self.t % 2 == 1 and self.t > 3):
				self.audioChannels[2].queue(self.dialogSoundFile)
				self.audioChannels[2].play()
			elif self.t == 3:
				self.audioChannels[3].queue(self.dialogSoundFile)
				self.audioChannels[0].pause()
				self.audioChannels[3].play()
				self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[7])
				self.audioChannels[0].queue(self.dialogSoundFile)
				self.audioChannels[0].next()
				self.audioChannels[0].play()
			else:
				self.audioChannels[1].queue(self.dialogSoundFile)
				self.audioChannels[1].play()
			time.sleep(self.lengths[self.t])		
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
		global EnableDialogs
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
		"Very well! This duel shall be a fine accompaniment to today's celebration!",
		"I know you can easily press the Space bar to use your sword. Your shield also works well with the Up arrow key. Let's see how you can do it.",
		"Fight with courage and honor!", "Commence!"]
		self.soundfiles = ["trumpet.wav", "dialog2_1.mp3", "dialog2_2.mp3", "dialog2_3.mp3", "dialog2_4.mp3", "dialog2_5.mp3", "dialog2_6.mp3", "dialog2_7.mp3", 
		"dialog2_8.mp3", "cheering.mp3", "dialog2_9.mp3", "dialog2_10.mp3", "dialog2_11.mp3", "dialog2_12.mp3", "dialog2_13.mp3", "dialog2_14.mp3",
		"dialog2_15.mp3", "dialog2_16.mp3", "dialog2_17.mp3", "dialog2_18.mp3", "dialog2_19.mp3", "dialog2_20.mp3", "dialog2_21.mp3", "dialog2_22.mp3",
		"dialog2_23.mp3", "dialog2_24.mp3", "dialog2_25.mp3", "dialog2_26.mp3", "battleinst.mp3", "dialog2_27.mp3", "dialog2_28.mp3"]
		self.channels = [0, 2, 1, 2, 1, 2, 1, 2, 1, 3, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1]
		self.lengths = [9, 3, 4, 3, 7, 5, 5, 4, 5, 4, 4, 6, 5, 5, 6, 4, 5, 4, 6, 5, 4, 7, 4, 6, 4, 1, 3, 5, 9, 2, 2]
		self.positions = [(2, 35, 2), (3, 10, 2), (1, 9, 2), (4, 11, 2), (2, 12, 2)]
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.backgroundSoundPlayer3 = pyglet.media.Player()
		self.dialogOddPlayer = pyglet.media.Player()
		self.dialogEvenPlayer = pyglet.media.Player()
		self.audioChannels = [self.backgroundSoundPlayer, self.dialogOddPlayer, self.dialogEvenPlayer, self.backgroundSoundPlayer2]
		for i in range(len(self.audioChannels)):
			self.audioChannels[i].position = self.positions[i]
		self.backgroundSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[0])
		self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[1])
	def update(self,dt):
		global EnableDialogs
		if not self.start:
			self.start = True
			if EnableDialogs:
				print self.text[self.t]
			self.audioChannels[0].queue(self.backgroundSoundFile)
			self.audioChannels[0].play()
			time.sleep(self.lengths[self.t])
			self.t += 1
		if self.t > 0 and self.t < len(self.text):
			if EnableDialogs:
				print self.text[self.t]
			self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[self.t])
			self.audioChannels[self.channels[self.t]].queue(self.dialogSoundFile)
			self.audioChannels[self.channels[self.t]].play()
			time.sleep(self.lengths[self.t])
			self.t += 1
		else:
			states.remove(self)
			states.append(Battle1(player))

class Battle1:
	def __init__(self,player):
		global EnableDialogs
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.backgroundSoundPlayer3 = pyglet.media.Player()
		self.backgroundSoundPlayer4 = pyglet.media.Player()
		self.backgroundSoundPlayer5 = pyglet.media.Player()
		self.backgroundSoundPlayer.position = (player.x-1, player.y, 0)
		self.backgroundSoundPlayer.queue(pyglet.media.load("soundfiles/battlemode.mp3"))
		self.backgroundSoundPlayer2.queue(pyglet.media.load("soundfiles/sword.wav", streaming=False))
		self.backgroundSoundPlayer2.position = (player.x-1, player.y, 0)
		self.backgroundSoundPlayer3.queue(pyglet.media.load("soundfiles/hit.wav", streaming=False))
		self.backgroundSoundPlayer3.position = (player.x-1, player.y, 0)
		self.text = ["(You are fighting the captain of the guards!)"]
		self.backgroundSoundPlayer4.queue(pyglet.media.load("soundfiles/battlebg.mp3"))
		self.backgroundSoundPlayer4.play()
		self.t = 0
		self.start = False
		self.str = 5
		self.EnemyHealth = 20
		self.player = player
		self.block = False
		self.willExit = False
	def update(self,dt):
		global EnableDialogs
		if not self.start:
			if EnableDialogs:
				print self.text[self.t]
			self.backgroundSoundPlayer.play()
			self.t += 1
			self.start = True
		if(self.player.health > 0):
			if random.randint(1,50) == 1:
				if self.block:
					if EnableDialogs:
						print "*block*"
				else:
					self.backgroundSoundPlayer3.play()
					self.backgroundSoundPlayer3.queue(pyglet.media.load("soundfiles/hit.wav", streaming=False))
					self.player.health = float(self.player.health) - float(self.str)
					self.player.health = int(self.player.health)
					if EnableDialogs:
						print "Health: " + str(self.player.health) + "/100"
			@window.event
			def on_key_press(symbol, modifiers):
				global EnableDialogs
				if symbol == pyglet.window.key.SPACE:
					self.backgroundSoundPlayer2.play()
					self.backgroundSoundPlayer2.queue(pyglet.media.load("soundfiles/sword.wav", streaming=False))
				if symbol == pyglet.window.key.SPACE and not self.block:
					self.EnemyHealth = float(self.EnemyHealth) - float(self.player.str)
					self.EnemyHealth = int(self.EnemyHealth)
					if EnableDialogs:
						print "Enemy Health: " + str(self.EnemyHealth)
				if symbol == pyglet.window.key.UP:
					self.block = True
			@window.event
			def on_key_release(symbol, modifiers):
				if symbol == pyglet.window.key.UP:
					self.block = False
			if self.EnemyHealth <= 0:
				if EnableDialogs:
					print "Victory!"
				self.backgroundSoundPlayer4.pause()
				self.backgroundSoundPlayer5.queue(pyglet.media.load("soundfiles/win.mp3"))
				self.backgroundSoundPlayer5.play()
				states.remove(self)
				states.append(Scene3())
			if self.player.health <= 0:
				self.backgroundSoundPlayer4.pause()
				self.backgroundSoundPlayer5.queue(pyglet.media.load("soundfiles/lose.wav"))
				self.backgroundSoundPlayer5.play()
		else:
			if EnableDialogs:
				print "Defeat..."
			states.append(MainMenu())
			states.remove(self)

class Scene3:
	def __init__(self):
		global EnableDialogs
		self.t = 0
		self.start = False
		self.text = ["A fine display! Such is only to be expected from among the kingdoms' finest!", "I thank you for the match. I have learned much.", 
		"I too, am grateful for this chance to cross swords.", "By my lord's leave, I shall return to my post.", "Your dedication is to be recognized, captain.",
		"I am pleased to know that your safety has not suffered in my absence.", "With the both of you here, the kingdom has nothing to fear!", 
		"I only wish that my son was here to witness your strength.", "My king, has the prince not been at your side for some time now?", "What do you-",
		"*stab*", "Your majesty!", "*thud*", "(The king dies)", "*screaming*", "The knight has murdered the king!", "What vile treachery!", "He flees!", "Guards! Guards!", 
		"Was he only fooling us all this time?", "Throw him in the dungeon!", "Hang him!", "Off with his head!", "Give us back our king!"]
		self.soundfiles = ["dialog3_1.mp3", "dialog3_2.mp3", "dialog3_3.mp3", "dialog3_4.mp3", "dialog3_5.mp3", "dialog3_6.mp3", "dialog3_7.mp3", 
		"dialog3_8.mp3", "dialog3_9.mp3", "dialog3_10.mp3", "stab_king.wav", "dialog3_11.mp3", "thud_king.wav", "king_dead.mp3", "panic_scream.mp3", 
		"dialog3_12.mp3", "dialog3_13.mp3", "dialog3_14.mp3", "dialog3_15.mp3", "dialog3_16.mp3", "dialog3_17.mp3", "dialog3_18.mp3",
		"dialog3_19.mp3", "dialog3_20.mp3"]
		self.channels = [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 0, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1]
		self.lengths = [5, 3, 4, 3, 4, 5, 4, 4, 4, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 2, 3, 5]
		self.positions = [(2, 35, 2), (3, 10, 2), (1, 9, 2), (4, 11, 2)]
		#self.positions = [(1, 15, 2), (2, 1, 2), (0, 0, 2), (3, 2, 2)]
		self.backgroundSoundPlayer = pyglet.media.Player()
		self.backgroundSoundPlayer2 = pyglet.media.Player()
		self.dialogOddPlayer = pyglet.media.Player()
		self.dialogEvenPlayer = pyglet.media.Player()
		self.audioChannels = [self.backgroundSoundPlayer, self.dialogOddPlayer, self.dialogEvenPlayer, self.backgroundSoundPlayer2]
		for i in range(len(self.audioChannels)):
			self.audioChannels[i].position = self.positions[i]
		self.backgroundSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[0])
		self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[1])
	def update(self,dt):
		global EnableDialogs	
		if not self.start:
			self.start = True
			time.sleep(3)
			if EnableDialogs:
				print self.text[self.t]
			self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[0])
			self.audioChannels[1].queue(self.dialogSoundFile)
			self.audioChannels[1].play()
			time.sleep(self.lengths[self.t])
			self.t += 1
		#try:
		if self.t > 0 and self.t < len(self.text):
			if EnableDialogs:
				print self.text[self.t]
			self.dialogSoundFile = pyglet.media.load("soundfiles/"+self.soundfiles[self.t])
			self.audioChannels[self.channels[self.t]].queue(self.dialogSoundFile)
			self.audioChannels[self.channels[self.t]].play()
			time.sleep(self.lengths[self.t])
			self.t += 1
		else:
			self.audioChannels[0].pause()
			self.audioChannels[3].pause()
			states.append(MainMenu())
			states.remove(self)
		#except Exception:
		#	print "Incomplete code or game bug, please contact the developers!"
		#	states.remove(self)

class SoundCheck:

	def __init__(self):
		self.centervoice = pyglet.media.Player()
		self.leftvoice = pyglet.media.Player()
		self.rightvoice = pyglet.media.Player()
		self.leftvoice.position = (-2, 0, 0)
		self.rightvoice.position = (2, 0, 0)
		self.count = 1
		self.centervoice.queue(pyglet.media.load("soundfiles/start1.mp3"))
		#self.centervoice.queue(pyglet.media.load("soundfiles/pressany.mp3"))
		self.leftvoice.queue(pyglet.media.load("soundfiles/left.mp3"))
		self.rightvoice.queue(pyglet.media.load("soundfiles/right.mp3"))
		self.centervoice.play()
		time.sleep(4)
		self.menu = True
		self.entered = False

	def update(self,dt):
		if self.menu:
			self.menu = False
			self.leftvoice.play()
			time.sleep(3)
			self.rightvoice.play()
			time.sleep(3)
			self.centervoice.queue(pyglet.media.load("soundfiles/pressenter.mp3"))
			self.centervoice.play()
			self.entered = True
		@window.event
		def on_key_press(symbol, modifiers):
			if symbol == pyglet.window.key.ENTER and self.entered:
				states.append(MainMenu())
				states.remove(self)

class MainMenu:
	def __init__(self):
		global player
		player.x = 0
		player.y = 0
		player.listenerObject.forward_orientation = (0, 1, 0)
		player.listenerObject.up_orientation = (0, 0, 1)
		player.updateListener()
		global EnableDialogs
		self.welcome = pyglet.media.Player()
		self.mainmenu = pyglet.media.Player()
		self.instructions = pyglet.media.Player()
		self.special = pyglet.media.Player()
		self.notPlayed = True
		self.onSpecialMenu = False

	def update(self,dt):
		global EnableDialogs
		if self.notPlayed:
			self.notPlayed = False
			self.welcome.queue(pyglet.media.load("soundfiles/welcome.mp3"))
			self.mainmenu.queue(pyglet.media.load("soundfiles/mainmenu.mp3"))
			self.welcome.play()
			time.sleep(2)
			self.mainmenu.play()
			time.sleep(8)
		@window.event
		def on_key_press(symbol, modifiers):
			global EnableDialogs
			if not self.onSpecialMenu and symbol == pyglet.window.key.W:
				global player
				player.x = 1
				states.append(Scene1())
				states.remove(self)
			elif not self.onSpecialMenu and symbol == pyglet.window.key.A:
				self.instructions.queue(pyglet.media.load("soundfiles/instructions.mp3"))
				self.instructions.play()
				time.sleep(19)
				self.notPlayed = True
			elif not self.onSpecialMenu and symbol == pyglet.window.key.S:
				states.remove(self)
			elif not self.onSpecialMenu and symbol == pyglet.window.key.D:
				self.onSpecialMenu = True
				if EnableDialogs:
					self.special.queue(pyglet.media.load("soundfiles/disabledialog.mp3"))
				else:
					self.special.queue(pyglet.media.load("soundfiles/enabledialog.mp3"))
				self.special.play()
			if self.onSpecialMenu and symbol == pyglet.window.key.SPACE:
				EnableDialogs = not EnableDialogs
				self.onSpecialMenu = False
				self.notPlayed = True

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
states.append(SoundCheck())
#states.append(Scene3())

def update(dt):
	if len(states):
		states[-1].update(dt)
	else:
		pyglet.app.exit()
		
pyglet.clock.schedule_interval(update, 1.0/60.0)
pyglet.app.run()
