# 
# a game by Adam Binks

import pygame, time
from components import Entity, GravityComponent, CollisionComponent

class Player(Entity):
	image = pygame.image.load('assets/mobs/player.png')
	moveSpeed = 300
	jumpVelocity = 300
	timeToJumpAfterLeavingGround = 0.2 # number of seconds in which the player can jump after falling off a platform
	drag = 120 						 # to make platforming less frustrating
	def __init__(self, data):
		Entity.__init__(self, data)
		self.add(data.playerGroup)

		self.image = Player.image
		self.rect = self.image.get_rect()
		self.rect.topleft = (50, 60) # TEMP

		self.collisions = CollisionComponent(self)
		self.gravity = GravityComponent(self)
		self.obeysGravity = True

		self.xVel = self.yVel = 0
		self.isOnGround = False
		self.lastTimeOnGround = 0


	def update(self, data):
		self.move(data)
		self.gravity.update(data)
		self.collisions.checkForWorldCollisions(data)
		self.collisions.checkIfStandingOn(data.dynamicObjects, data)


	def move(self, data):
		"""Update velocity based on keyboard input"""
		if self.isOnGround:
			self.lastTimeOnGround = time.time()

		self.xVel = 0
		if pygame.locals.K_RIGHT in data.input.pressedKeys:
			self.xVel += Player.moveSpeed * data.dt
		if pygame.locals.K_LEFT in data.input.pressedKeys:
			self.xVel -= Player.moveSpeed * data.dt

		if self.xVel > 0:
			self.xVel -= Player.drag * data.dt
		if self.xVel < 0:
			self.xVel += Player.drag * data.dt

		if pygame.locals.K_UP in data.input.justPressedKeys and \
				(self.isOnGround or time.time() - self.lastTimeOnGround < Player.timeToJumpAfterLeavingGround):
			self.yVel = -Player.jumpVelocity
			self.lastTimeOnGround = 0

		self.rect.move_ip(self.xVel, 0)