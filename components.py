# 
# a game by Adam Binks

import pygame, math


class Entity(pygame.sprite.Sprite):
	"""Base class for all in game objects"""
	def __init__(self, data):
		pygame.sprite.Sprite.__init__(self)
		self.add(data.entities)



class CollisionComponent:
	"""A component which will check if its master entity has collided with a static entity and correct its rect's position"""
	def __init__(self, master):
		self.master = master


	def checkForWorldCollisions(self, velocityTuple, data):
		"""Checks if the master has collided with a static world entity and if so corrects its position"""
		self.collide(velocityTuple[0], 0, data.platforms) # check for x collisions
		if self.master.obeysGravity:
			self.master.gravity.update(data)
		self.master.isOnGround = False
		self.collide(0, velocityTuple[1], data.platforms) # check for y collisions


	def collide(self, xVel, yVel, obstacles):
		"""
		Checks for collisions with the obstacles passed, then corrects
		self.rect's position so it no longer collides with them.
		"""
		collidedObstacles = pygame.sprite.spritecollide(self.master, obstacles, False)
		for o in collidedObstacles:
			if xVel > 0: # right
				print 'collide right'
				self.master.rect.right = o.rect.left
			if xVel < 0: # left
				self.master.rect.left = o.rect.right
				print 'collide left'
			if yVel > 0: # collided with floor
				self.master.rect.bottom = o.rect.top
				self.master.isOnGround = True
				self.master.yVel = 0
				print 'collide bottom'
			if yVel < 0: # collided with ceiling
				self.master.rect.top = o.rect.bottom
				self.master.yVel = 0
				print 'collide top'



class GravityComponent:
	"""A component which will update its master's y velocity and rect's y coordinates"""
	gravity = 100
	terminalVelocity = 400
	def __init__(self, master):
		self.master = master


	def update(self, data):
		if not self.master.isOnGround:
			self.master.yVel += GravityComponent.gravity * data.dt
			if self.master.yVel > GravityComponent.terminalVelocity:
				self.master.yVel = GravityComponent.terminalVelocity
			if 0 < self.master.yVel <= 50:
				self.master.yVel = 50

			self.master.rect.y += math.ceil(self.master.yVel * data.dt)
			print 'FALL: ' + str(math.ceil(self.master.yVel * data.dt))