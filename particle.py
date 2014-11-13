# Magus Operandi
# a game by Adam Binks

import pygame, time, random
from components import Entity, GravityComponent

class Particle(Entity):
	"""A simple particle"""
	gravity = 1.5
	weight = 0.5
	def __init__(self, data, image, center, avgLifeSpan, velocity, obeysGravity):
		"""obeysGravity: 0 is no gravity, 1 is falling particle, -1 is upward floating particle"""
		Entity.__init__(self, data)
		self.add(data.particles)

		self.image = image
		self.rect = image.get_rect(center=center)
		self.coords = list(center)

		self.velocity = list(velocity)
		self.obeysGravity = obeysGravity
		if obeysGravity:
			self.gravity = GravityComponent(self)
			self.weight = Particle.weight

		self.birthTime = time.time()
		self.lifeTime = random.uniform(avgLifeSpan - 0.3, avgLifeSpan + 0.3)
		if self.lifeTime < 0: self.lifeTime = 0.05


	def update(self, data):
		if self.gravity != 0:
			self.gravity.update(data) # allow gravity to act upon the particle
		self.coords[0] += self.velocity[0] * data.dt
		self.coords[1] += self.velocity[1] * data.dt

		self.rect.center = self.coords

		data.gameSurf.blit(self.image, self.rect)
		if time.time() - self.birthTime > self.lifeTime:
			self.kill()