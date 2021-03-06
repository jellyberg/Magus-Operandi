# 
# a game by Adam Binks

import pygame
from components import Entity, GravityComponent, CollisionComponent, EnchantmentComponent
from ui import SpellTargeter
from Box2D.b2 import *

class StaticObject(Entity):
	"""An unmovable object that forms part of the world geometry"""
	def __init__(self, rect, image, data, isRectangle=True):
		Entity.__init__(self, data)
		self.add(data.staticObjects)
		self.add(data.worldGeometry)
		self.image = image
		self.rect = rect

		h = rect.height / 2.0
		w = rect.width / 2.0
		self.body = data.world.CreateStaticBody(position=(data.pixelsToMetreCoords(rect.topleft)),
												shape=polygonShape(box=(data.pixelsToMetresConvert((h, w)))))

		print str(self.body.position)
		print str(data.pixelsToMetresConvert((h, w)))



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
		
		#self.collisions = CollisionComponent(self, False, True)
		#self.gravity = GravityComponent(self)
		self.enchantments = EnchantmentComponent(self)
		self.isBeingStoodOn = False


		h = rect.height / 2.0
		w = rect.width / 2.0
		self.body = data.world.CreateDynamicBody(position=(data.pixelsToMetreCoords(self.rect.topleft)), angle=0)
		self.body.CreatePolygonFixture(box=(data.pixelsToMetresConvert((h, w))), density=1, friction=0.3)


	def update(self, data):
		self.enchantments.update(data)

		#if not data.balloons or not self.isBeingStoodOn:  # balloons don't float when something is on top of them
		#	self.gravity.update(data)

		#if self.isPushable:
		#	data.dynamicObjects.remove(self)
		#	self.collisions.checkIfBeingPushed(data.playerGroup.sprites() + data.dynamicObjects.sprites(), data)
		#	data.dynamicObjects.add(self)
		#self.collisions.checkIfStandingOn(data.dynamicObjects, data)
		#self.collisions.checkForWorldCollisions(data)

		if not data.spellTargeter and data.input.mousePressed == 1 and self.rect.collidepoint(data.gameMousePos):
			self.enchantments.removeSoulBind()
			SpellTargeter(self, data.RED, 'soulbind', data)

		self.isBeingStoodOn = False



class Platform(StaticObject):
	"""A simple static platform"""
	def __init__(self, topleft, image, data):
		rect = image.get_rect(topleft = topleft)

		StaticObject.__init__(self, rect, image, data)
		self.add(data.platforms)



class Lock(StaticObject):
	"""A static platform that disappears when it collides with a key"""
	image = pygame.image.load('assets/objects/lock.png')
	def __init__(self, midbottom, data):
		rect = Lock.image.get_rect(midbottom = midbottom)

		self.image = Lock.image.convert()
		StaticObject.__init__(self, rect, self.image, data)
		self.add(data.locks)
		self.add(data.unlockableWithKeys)


	def unlock(self, data):
		self.kill()



class Exit(StaticObject):
	"""When the player touches an exit the next level is loaded"""
	def __init__(self, midbottom, data):
		self.rect = Exit.image.get_rect(midbottom = midbottom)
		self.collisionRect = pygame.Rect((0, 0), (self.rect.width - 20, self.rect.height - 20))
		self.collisionRect.midbottom = midbottom
		StaticObject.__init__(self, self.rect, Exit.image, data)
		self.add(data.exits)
		self.remove(data.worldGeometry)



# class Button(StaticObject):
# 	"""A button that is activated while colliding with dynamic objects or the player"""
# 	def __init__(self, )
# 		image = pygame.image.load('assets/object/')


class Crate(DynamicObject):
	"""A simple pushable crate, obeys gravity"""
	image = pygame.image.load('assets/objects/crate.png')
	def __init__(self, midbottom, data):
		rect = Crate.image.get_rect(midbottom = midbottom)
		Crate.image.convert()
		DynamicObject.__init__(self, rect, self.image, data, 'PUSHABLE')
		self.add(data.crates)
		self.weight = 2.0



class Balloon(DynamicObject):
	"""A non pushable balloon that floats upwards"""
	image = pygame.image.load('assets/objects/balloon.png')
	def __init__(self, midbottom, data):
		rect = Balloon.image.get_rect(midbottom = midbottom)
		Balloon.image.convert()
		DynamicObject.__init__(self, rect, self.image, data, 1) # not pushable
		self.add(data.balloons)
		self.weight = -0.1


class Key(DynamicObject):
	"""A pushable key that opens doors (and is consumed in the process) when it is near them"""
	image = pygame.image.load('assets/objects/key.png')
	def __init__(self, midbottom, data):
		rect = Key.image.get_rect(midbottom = midbottom)
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
