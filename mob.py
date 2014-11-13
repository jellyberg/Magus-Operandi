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

		self.animation = AnimationComponent(self, { 'run': {'spritesheet': pygame.image.load('assets/mobs/player/run.png'),
														   'imageWidth': 128, 'timePerFrame': 0.06, 'flip': True},
													'jump': {'spritesheet': pygame.image.load('assets/mobs/player/jump.png'),
														   'imageWidth': 128, 'timePerFrame': 0.1, 'flip': True},
													'idle': {'spritesheet': pygame.image.load('assets/mobs/player/idle.png'),
														   'imageWidth': 128, 'timePerFrame': 0.1, 'flip': True},
													'push': {'spritesheet': pygame.image.load('assets/mobs/player/push.png'),
														   'imageWidth': 128, 'timePerFrame': 0.1, 'flip': True}})

		collisionRect = pygame.Rect((0, 0), (83, 128))
		collisionRect.midbottom = midbottom
		self.collisions = CollisionComponent(self, collisionRect)
		self.gravity = GravityComponent(self)
		self.obeysGravity = True
		self.weight = 1
		self.movedThisFrame = False

		self.moveSpeedModifier = {'left': 0, 'right': 0} # a number added on to the player's moveSpeed every frame eg when pushing a crate

		self.xVel = self.yVel = 0
		self.facing = 'R'
		self.isOnGround = False
		self.lastTimeOnGround = 0
		self.releasedJumpButton = True

		self.animation.play('idleR')
		self.animation.update()

		self.rect = self.image.get_rect(midbottom = midbottom)


	def update(self, data):
		for exit in data.exits:
			if self.rect.colliderect(exit.rect):
				data.gameHandler.nextLevel(data)
				return

		self.move(data)
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

		if not self.movedThisFrame and ('run' in self.animation.animName or 'push' in self.animation.animName):
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