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


	def checkForWorldCollisions(self, data):
		"""Checks whether 6 collision points collide with the world geometry, and if so move the entity's rect"""
		rect = self.master.rect
		collisionPoints = {'top': (rect.midtop), 'bottom': (rect.midbottom),
						   'topleft': (rect.left, rect.top + 5), 'bottomleft': (rect.left, rect.bottom - 5),
						   'topright': (rect.right, rect.top + 5), 'bottomright': (rect.right, rect.bottom - 5)} # points to check collision

		# collidedPoints will be a dict with format {collisionPointName: platformCollided}
		collidedPoints = self.checkCollisionPoints(data, collisionPoints)
		self.master.isOnGround = False # assume not on ground

		for key in collidedPoints:
			if key == 'bottom': # do bottom first because entities will most likely be falling fast
				rect.bottom = collidedPoints[key].rect.top
				self.master.isOnGround = True
				self.master.yVel = 0
			elif key == 'top':
				rect.top = collidedPoints[key].rect.bottom
				self.master.yVel = 0 # hit head of ceiling
			elif key in ['topleft', 'bottomleft']:
				rect.left = collidedPoints[key].rect.right
			elif key in ['topright', 'bottomright']:
				rect.right = collidedPoints[key].rect.left


	def checkCollisionPoints(self, data, pointsDict):
		"""Checks whether each of the 6 collision points collides with any platform"""
		collidedPoints = {}
		for platform in data.platforms:
			for key in pointsDict:
				if platform.rect.collidepoint(pointsDict[key]):
					collidedPoints[key] = platform
		return collidedPoints



class GravityComponent:
	"""A component which will update its master's y velocity and rect's y coordinates"""
	gravity = 600
	terminalVelocity = 400
	def __init__(self, master):
		self.master = master


	def update(self, data):
		if not self.master.isOnGround:
			self.master.yVel += GravityComponent.gravity * data.dt
			if self.master.yVel > GravityComponent.terminalVelocity:
				self.master.yVel = GravityComponent.terminalVelocity

			self.master.rect.y += math.ceil(self.master.yVel * data.dt)
		if self.master.yVel < 0:
			self.master.rect.y += self.master.yVel * data.dt