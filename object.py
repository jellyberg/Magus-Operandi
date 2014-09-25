# 
# a game by Adam Binks

import pygame
from components import Entity, GravityComponent, CollisionComponent, EnchantmentComponent
from ui import SpellTargeter

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
		self.mask = pygame.mask.from_surface(image)
		self.maskOutline = self.mask.outline()
		self.isPushable = pushable
		self.movedThisFrame = False
		
		self.collisions = CollisionComponent(self)
		self.gravity = GravityComponent(self)
		self.enchantments = EnchantmentComponent(self)

	def update(self, data):
		self.enchantments.update(data)

		self.gravity.update(data)

		if self.isPushable:
			data.dynamicObjects.remove(self)
			self.collisions.checkIfBeingPushed(data.playerGroup.sprites() + data.dynamicObjects.sprites(), data)
			data.dynamicObjects.add(self)
		self.collisions.checkIfStandingOn(data.dynamicObjects, data)
		self.collisions.checkForWorldCollisions(data)

		if not data.spellTargeter and data.input.mousePressed == 1 and self.rect.collidepoint(data.gameMousePos):
			self.enchantments.removeSoulBind()
			SpellTargeter(self, data.RED, 'soulbind', data)



class Platform(StaticObject):
	"""A simple static platform"""
	def __init__(self, topleft, image, data):
		rect = image.get_rect()
		rect.topleft = topleft

		StaticObject.__init__(self, rect, image, data)
		self.add(data.platforms)



class Lock(StaticObject):
	"""A static platform that disappears when it collides with a key"""
	image = pygame.image.load('assets/objects/lock.png')
	def __init__(self, topleft, data):
		rect = Lock.image.get_rect()
		rect.topleft = topleft

		self.image = Lock.image.convert()
		StaticObject.__init__(self, rect, self.image, data)
		self.add(data.locks)
		self.add(data.unlockableWithKeys)


	def unlock(self, data):
		self.kill()



class Exit(Entity):
	"""When the player touches an exit the next level is loaded"""
	image = pygame.Surface((32, 32))
	image.fill((220, 180, 220))
	def __init__(self, topleft, data):
		Entity.__init__(self, data)
		self.add(data.exits)
		self.rect = Exit.image.get_rect()
		self.rect.topleft = topleft
		self.image = Exit.image



class Crate(DynamicObject):
	"""A simple pushable crate, obeys gravity"""
	image = pygame.image.load('assets/objects/crate.png')
	def __init__(self, topleft, data):
		rect = Crate.image.get_rect()
		rect.topleft = topleft
		Crate.image.convert()
		DynamicObject.__init__(self, rect, self.image, data, 'PUSHABLE')
		self.add(data.crates)
		self.weight = 2.0



class Balloon(DynamicObject):
	"""A non pushable balloon that floats upwards"""
	image = pygame.image.load('assets/objects/balloon.png')
	def __init__(self, topleft, data):
		rect = Balloon.image.get_rect()
		rect.topleft = topleft
		Balloon.image.convert()
		DynamicObject.__init__(self, rect, self.image, data, 1) # not pushable
		self.add(data.balloons)
		self.weight = -0.1


class Key(DynamicObject):
	"""A pushable key that opens doors (and is consumed in the process) when it is near them"""
	image = pygame.image.load('assets/objects/key.png')
	def __init__(self, topleft, data):
		rect = Key.image.get_rect()
		rect.topleft = topleft
		Key.image.convert()
		DynamicObject.__init__(self, rect, self.image, data, 'pushable')
		self.add(data.keys)
		self.weight = 1.5


	def update(self, data):
		"""Check if unlocking door (within 10 pixels of one)"""
		collidedPoints = self.collisions.checkCollisionPoints(data, 
				{'left': (self.rect.left - 10, self.rect.centery), 'right': (self.rect.right + 10, self.rect.centery),
				'top': (self.rect.centerx, self.rect.top - 10), 'bottom': (self.rect.centerx, self.rect.bottom + 10),
				'center': self.rect.center}, data.unlockableWithKeys)
		if len(collidedPoints) > 0:
			for key in collidedPoints:
				collidedPoints[key].unlock(data)
				self.kill()
				return

		DynamicObject.update(self, data)
