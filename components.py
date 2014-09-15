import pygame


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
		self.isOnGround = False
		self.collide(velocityTuple[0], 0, data.platforms) # check for x collisions
		self.collide(0, velocityTuple[1], data.platforms) # check for y collisions


	def collide(self, xVel, yVel, obstacles):
		"""
		Checks for collisions with the obstacles passed, then corrects
		self.rect's position so it no longer collides with them.
		"""
		collidedObstacles = pygame.sprite.spritecollide(self.master, obstacles, False)
		for o in collidedObstacles:
			if xVel > 0: # right
				self.master.rect.right = o.rect.left
			if xVel < 0: # left
				self.master.rect.left = o.rect.right
			if yVel > 0: # falling
				self.master.rect.bottom = o.rect.top
				self.master.onGround = True
				self.master.yVel = 0
			if yVel < 0: # jumping
				self.master.rect.top = o.rect.bottom
				self.master.yVel = 0



class GravityComponent:
	"""A component which will update its master's y velocity and rect's y coordinates"""
	gravity = 1000
	terminalVelocity = 400
	def __init__(self, master):
		self.master = master


	def update(self, data):
		if not self.master.isOnGround:
			self.master.yVel += GravityComponent.gravity * data.dt
			if self.master.yVel > GravityComponent.terminalVelocity:
				self.master.yVel = GravityComponent.terminalVelocity
			self.master.rect.y += self.master.yVel * data.dt