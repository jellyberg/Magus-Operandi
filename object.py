# 
# a game by Adam Binks

import pygame
from components import Entity, GravityComponent, CollisionComponent

class StaticObject(Entity):
	"""An unmovable object that forms part of the world geometry"""
	def __init__(self, rect, image, data):
		Entity.__init__(self, data)
		self.add(data.staticObjects)
		self.add(data.worldGeometry)
		self.image = image
		self.rect = rect


class DynamicObject(Entity):
	"""An object that can be pushed by the player or other entities and obeys gravity"""
	def __init__(self, rect, image, data, pushable):
		Entity.__init__(self, data)
		self.add(data.dynamicObjects)
		self.rect = rect
		self.collisions = CollisionComponent(self)
		self.gravity = GravityComponent(self)
		self.isPushable = pushable

	def update(self, data):
		self.gravity.update(data)
		if self.isPushable:
			data.dynamicObjects.remove(self)
			self.collisions.checkIfBeingPushed(data.playerGroup.sprites() + data.dynamicObjects.sprites(), data)
			data.dynamicObjects.add(self)
		self.collisions.checkIfStandingOn(data.dynamicObjects, data)
		self.collisions.checkForWorldCollisions(data)


class Platform(StaticObject):
	"""A simple static platform"""
	def __init__(self, topleft, image, data):
		rect = image.get_rect()
		rect.topleft = topleft

		StaticObject.__init__(self, rect, image, data)
		self.add(data.platforms)


class Crate(DynamicObject):
	"""A simple pushable crate, obeys gravity"""
	image = pygame.image.load('assets/objects/crate.png')
	def __init__(self, topleft, data):
		rect = Crate.image.get_rect()
		rect.topleft = topleft
		Crate.image.convert()
		DynamicObject.__init__(self, rect, Crate.image, data, 'PUSHABLE')
		self.add(data.crates)