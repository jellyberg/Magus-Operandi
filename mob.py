# 
# a game by Adam Binks

import pygame, time
from components import Entity, GravityComponent, CollisionComponent, AnimationComponent

class Player(Entity):
	moveSpeed = 400
	jumpVelocity = 400
	jumpHoldIncrease = 200
	timeToJumpAfterLeavingGround = 0.2 # number of seconds in which the player can jump after falling off a platform
	drag = 120 						 # to make platforming less frustrating
	def __init__(self, midbottom, data):
		Entity.__init__(self, data)
		self.add(data.playerGroup)
		self.add(data.mobs)

		colourDict = {(206, 209, 138): (206, 138, 138),  # robe
					  (170, 192, 171): (191, 170, 170), #shoes and hat
					  (206, 201, 175): (204, 184, 173), # skin
					  (233, 234, 232): (233, 234, 232)} # moustache

		animImages = {}
		for animName in ['run', 'jump', 'idle', 'cast', 'push', 'pull']:
			animImages[animName] = pygame.image.load('assets/mobs/player/%s.png' %(animName))
		animImages = self.setColours(colourDict, animImages)
		self.initAnimations(animImages)

		

		collisionRect = pygame.Rect((0, 0), (83, 120))
		collisionRect.midbottom = midbottom
		self.collisions = CollisionComponent(self, collisionRect, True)
		self.gravity = GravityComponent(self)
		self.obeysGravity = True
		self.weight = 1
		self.movedThisFrame = False

		self.moveSpeedModifier = {'left': 0, 'right': 0} # a number added on to the player's moveSpeed every frame
														 # eg when pushing a crate

		self.xVel = self.yVel = 0
		self.facing = 'R'
		self.isOnGround = False
		self.lastTimeOnGround = 0
		self.releasedJumpButton = True

		self.animation.play('idleR')
		self.animation.update()

		self.rect = self.image.get_rect(midbottom = midbottom)

		self.pullRect = pygame.Rect((0, 0), (40, self.rect.height))
		self.pullStartFacing = None
		self.isPulling = False


	def initAnimations(self, animImages, currentAnim=None):
		self.animation = AnimationComponent(self, { 'run': {'spritesheet': animImages['run'],
														   'imageWidth': 128, 'timePerFrame': 0.06, 'flip': True},
													'jump': {'spritesheet': animImages['jump'],
														   'imageWidth': 128, 'timePerFrame': 0.1, 'flip': True},
													'idle': {'spritesheet': animImages['idle'],
														   'imageWidth': 128, 'timePerFrame': 0.15, 'flip': True},
													'cast': {'spritesheet': animImages['cast'],
														   'imageWidth': 128, 'timePerFrame': 0.18, 'flip': True},
													'push': {'spritesheet': animImages['push'],
														   'imageWidth': 128, 'timePerFrame': 0.1, 'flip': True},
													'pull': {'spritesheet': animImages['pull'],
														   'imageWidth': 128, 'timePerFrame': 0.15, 'flip': True}})


	def update(self, data):
		for exit in data.exits:   # if touches an exit when on ground, load next level
			if self.isOnGround and self.collisions.collisionRect.colliderect(exit.collisionRect):
				data.gameHandler.nextLevel(data)
				return

		if not data.spellTargeter:
			self.move(data)
			self.isPulling = self.pull(data)

		# spellcasting animation
		if data.spellTargeter:
			self.animation.play('cast' + self.facing)
		if 'cast' in self.animation.animName:
			if data.gameMousePos[0] < self.rect.centerx:
				self.facing = 'L'
			else:
				self.facing  = 'R'
			self.animation.switchDirection(self.facing)

			if not data.spellTargeter:
				self.animation.play('idle' + self.facing)

		self.gravity.update(data)
		self.collisions.checkForWorldCollisions(data)
		self.collisions.checkIfStandingOn(data.dynamicObjects, data)
		self.animation.update()


	def move(self, data):
		"""Update velocity based on keyboard input"""
		if self.isOnGround:
			self.lastTimeOnGround = time.time()

		self.xVel = 0
		self.movedThisFrame = False
		for key in data.input.pressedKeys: # support for multiple keys bound to the same action
			if key in data.keybinds['right']:
				self.xVel += (Player.moveSpeed + self.moveSpeedModifier['right']) * data.dt
				self.facing = 'R'
				self.animation.switchDirection('R')
				if 'idle' in self.animation.animName:
					self.animation.play('runR')
				self.movedThisFrame = True
				break
			if key in data.keybinds['left']:
				self.xVel -= (Player.moveSpeed + self.moveSpeedModifier['left']) * data.dt
				self.facing = 'L'
				self.animation.switchDirection('L')
				if 'idle' in self.animation.animName:
					self.animation.play('runL')
				self.movedThisFrame = True
				break

		if self.isPulling and self.facing != self.pullStartFacing:
			self.animation.play('pull' + self.facing)

		if not self.movedThisFrame and ('run' in self.animation.animName or 'push' in self.animation.animName\
										or 'pull' in self.animation.animName):
			self.animation.play('idle' + self.facing)

		if self.xVel > 0:
			self.xVel -= Player.drag * data.dt
		if self.xVel < 0:
			self.xVel += Player.drag * data.dt

		for key in data.keybinds['jump']:
			if key in data.input.justPressedKeys:
				# JUMP if on ground or just fell off a platform
				if self.isOnGround or time.time() - self.lastTimeOnGround < Player.timeToJumpAfterLeavingGround:
					self.yVel = -Player.jumpVelocity
					self.lastTimeOnGround = 0
					self.releasedJumpButton = False
					self.animation.playOnce('jump' + self.facing)
					break
			# OR if jumping up and jump is still held, jump a bit higher
			elif key in data.input.pressedKeys and self.yVel < -1 and not self.releasedJumpButton:
				self.rect.move_ip(0, -Player.jumpHoldIncrease * data.dt)
			if key in data.input.unpressedKeys:
				self.releasedJumpButton = True

		self.rect.move_ip(round(self.xVel), 0)
		self.moveSpeedModifier['right'] = self.moveSpeedModifier['left'] = 0


	def pull(self, data):
		"""Pulls any pushable objects within range of the player"""
		keyIsPressed = False
		for key in data.keybinds['pull']:
			if key in data.input.pressedKeys:
				keyIsPressed = True
				if not self.pullStartFacing:
					self.pullStartFacing = self.facing
				break

		if keyIsPressed:
			if self.pullStartFacing == 'R':
				self.pullRect.topleft = self.collisions.collisionRect.topright
			elif self.pullStartFacing == 'L':
				self.pullRect.topright = self.collisions.collisionRect.topleft

			for obj in data.dynamicObjects:
				if obj.rect.colliderect(self.pullRect):
					if self.pullStartFacing == 'R':
						obj.rect.left = self.collisions.collisionRect.right
					if self.pullStartFacing == 'L':
						obj.rect.right = self.collisions.collisionRect.left
					return 'pulling'

		if not keyIsPressed:
			self.pullStartFacing = None


	def setColours(self, colourDict, imageDict):
		"""Set colours of the wizard's images"""
		modifiedImgs = {}
		for imgName in imageDict:
			newImage = imageDict[imgName].copy()
			pixArray = pygame.PixelArray(newImage)

			for oldColour in colourDict:
				newColour = colourDict[oldColour]
				pixArray.replace(oldColour, newColour)

			modifiedImgs[imgName] = newImage

		return modifiedImgs
