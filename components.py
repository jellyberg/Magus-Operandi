# 
# a game by Adam Binks

import pygame, math


class Entity(pygame.sprite.Sprite):
	"""Base class for all in game objects"""
	def __init__(self, data):
		pygame.sprite.Sprite.__init__(self)
		self.add(data.entities)



class CollisionComponent:
	"""A component which will check if its master entity has collided with a static entity and correct its rect's position.
	This component should only be used on the dynamic/movable entities"""
	slowdownWhilePushing = 5 # slow the mob pushing this entity by x
	def __init__(self, master):
		self.master = master
		self.master.isOnGround = False


	def checkForWorldCollisions(self, data):
		"""Checks whether 6 collision points collide with the world geometry, and if so move the entity's rect"""
		rect = self.master.rect
		collisionPoints = {'top': (rect.midtop), 'bottom': (rect.midbottom),
						   'topleft': (rect.left, rect.top + 10), 'bottomleft': (rect.left, rect.bottom - 10),
						   'topright': (rect.right, rect.top + 10), 'bottomright': (rect.right, rect.bottom - 10)} # points to check collision

		# collidedPoints will be a dict with format {collisionPointName: platformCollided}
		collidedPoints = self.checkCollisionPoints(data, collisionPoints, data.worldGeometry)
		self.master.isOnGround = False # assume not on ground
		self.doCollision(collidedPoints, data)


	def checkCollisionPoints(self, data, pointsDict, groupToCollide):
		"""Checks whether each of the up to 6 passed collision points collides with a rect of any of the passed group"""
		collidedPoints = {}
		for platform in groupToCollide:
			for key in pointsDict:
				if platform.rect.collidepoint(pointsDict[key]):
					collidedPoints[key] = platform
		return collidedPoints


	def doCollision(self, collidedPoints, data):
		"""Moves the master's rect according to which points have been collided with"""
		rect = self.master.rect
		for key in collidedPoints:
			if key == 'bottom':
				rect.bottom = collidedPoints[key].rect.top
				self.master.isOnGround = True
				self.master.yVel = 0
			elif key == 'top':
				rect.top = collidedPoints[key].rect.bottom
				self.master.yVel = 0 # hit head against the ceiling
			elif key in ['topleft', 'bottomleft']:
				rect.left = collidedPoints[key].rect.right
			elif key in ['topright', 'bottomright']:
				rect.right = collidedPoints[key].rect.left


	def checkIfBeingPushed(self, entitiesToBePushedBy, data):
		"""Checks whether 4 collision points collide with the entities to be pushed by, and if so move the entity's rect."""
		rect = self.master.rect
		collisionPoints = {'topleft': (rect.left, rect.top + 10), 'bottomleft': (rect.left, rect.bottom - 10),
						   'topright': (rect.right, rect.top + 10), 'bottomright': (rect.right, rect.bottom - 10)} # points to check collision

		# collidedPoints will be a dict with format {collisionPointName: platformCollided}
		collidedPoints = self.checkCollisionPoints(data, collisionPoints, entitiesToBePushedBy)
		self.doCollision(collidedPoints, data)

		# if applicable, slow the pusher's movespeed by slowdownWhilePushing while pushing
		for key in collidedPoints:
			if hasattr(collidedPoints[key], 'moveSpeedModifier'):
				if key in ['topleft', 'bottomleft']:
					collidedPoints[key].moveSpeedModifier['right'] = CollisionComponent.slowdownWhilePushing
				elif key in ['topright', 'bottomright']:
					collidedPoints[key].moveSpeedModifier['left'] = CollisionComponent.slowdownWhilePushing


	def checkIfStandingOn(self, entitiesToStandOn, data):
		rect = self.master.rect
		collisionPoints = {'bottom': rect.midbottom}
		# collidedPoints will be a dict with format {collisionPointName: platformCollided}
		collidedPoints = self.checkCollisionPoints(data, collisionPoints, entitiesToStandOn)
		self.doCollision(collidedPoints, data)




class GravityComponent:
	"""A component which will update its master's y velocity and rect's y coordinates"""
	gravity = 600
	terminalVelocity = 400
	def __init__(self, master):
		self.master = master
		self.master.yVel = 0


	def update(self, data):
		if not self.master.isOnGround:
			self.master.yVel += GravityComponent.gravity * data.dt
			if self.master.yVel > GravityComponent.terminalVelocity:
				self.master.yVel = GravityComponent.terminalVelocity

			self.master.rect.y += math.ceil(self.master.yVel * data.dt) * self.master.weight
		if self.master.yVel < 0:
			self.master.rect.y += self.master.yVel * data.dt * self.master.weight



class EnchantmentComponent:
	"""This component allows an entity to be affected by targeted spells"""
	def __init__(self, master):
		self.master = master
		self.soulBound = None


	def update(self, data):
		"""Update's all enchantments the master entity is under the effect of"""
		if self.soulBound:
			self.rect.move_ip(self.soulBound.rect.top - self.soulBinderLastPos[0], self.soulBound.rect.top - self.soulBinderLastPos[1])


	def bindSoulTo(self, target):
		"""When entity A's (master) soul is bound to entity B (target), entity B's movements also act upon entity A"""
		self.soulBound = target
		self.soulBinderLastPos = target.rect.topleft
