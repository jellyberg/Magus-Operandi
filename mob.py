# 
# a game by Adam Binks

import pygame
from components import Entity, GravityComponent, CollisionComponent

class Player(Entity):
	image = pygame.image.load('assets/mobs/player.png')
	moveSpeed = 300
	jumpVelocity = 400
	drag = 120
	def __init__(self, data):
		Entity.__init__(self, data)
		self.image = Player.image
		self.rect = self.image.get_rect()
		self.rect.topleft = (50, 60) # TEMP

		self.collisions = CollisionComponent(self)
		self.gravity = GravityComponent(self)
		self.obeysGravity = True

		self.xVel = self.yVel = 0
		self.isOnGround = False


	def update(self, data):
		self.move(data)
		self.gravity.update(data)
		self.collisions.checkForWorldCollisions(data)


	def move(self, data):
		"""Update velocity based on keyboard input"""
		self.xVel = 0
		if pygame.locals.K_RIGHT in data.input.pressedKeys:
			self.xVel += Player.moveSpeed * data.dt
		if pygame.locals.K_LEFT in data.input.pressedKeys:
			self.xVel -= Player.moveSpeed * data.dt

		if self.xVel > 0:
			self.xVel -= Player.drag * data.dt
		if self.xVel < 0:
			self.xVel += Player.drag * data.dt

		if pygame.locals.K_UP in data.input.justPressedKeys and self.isOnGround:
			self.yVel = -Player.jumpVelocity

		self.rect.move_ip(self.xVel, 0)