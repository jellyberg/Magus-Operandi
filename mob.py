# 
# a game by Adam Binks

import pygame
from components import Entity, GravityComponent, CollisionComponent

class Player(Entity):
	image = pygame.image.load('assets/mobs/player.png')
	moveSpeed = 50
	jumpVelocity = 20
	def __init__(self, data):
		Entity.__init__(self, data)
		self.image = Player.image
		self.rect = self.image.get_rect()
		self.rect.topleft = (35, 35)

		self.collisions = CollisionComponent(self)
		self.gravity = GravityComponent(self)

		self.xVel = self.yVel = 0
		self.isOnGround = False


	def update(self, data):
		self.gravity.update(data)
		self.move(data)
		self.collisions.checkForWorldCollisions((self.xVel, self.yVel), data)


	def move(self, data):
		"""Update velocity based on keyboard input"""
		if pygame.locals.K_RIGHT in data.input.pressedKeys:
			self.xVel += Player.moveSpeed * data.dt
		if pygame.locals.K_LEFT in data.input.pressedKeys:
			self.xVel += Player.moveSpeed * data.dt
		if pygame.locals.K_UP in data.input.pressedKeys and self.isOnGround:
			self.yVel += Player.jumpVelocity