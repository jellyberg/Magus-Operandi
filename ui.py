# 
# a game by Adam Binks

import pygame
pygame.init()

BASICFONT       = pygame.font.Font('assets/fonts/roboto medium.ttf', 14)
MEDIUMFONT      = pygame.font.Font('assets/fonts/roboto regular.ttf', 16)
BIGFONT         = pygame.font.Font('assets/fonts/roboto regular.ttf', 25)
EXTRABIGFONT    = pygame.font.Font('assets/fonts/roboto regular.ttf', 35)

def genText(text, topLeftPos, colour, font):
	surf = font.render(text, 1, colour)
	surf.set_colorkey((0,0,0))
	rect = surf.get_rect()
	rect.topleft = topLeftPos
	return (surf, rect)



class SpellTargeter(pygame.sprite.Sprite):
	"""An arrow/line that shows you what you are targeting the spell you are casting on"""
	def __init__(self, startEntity, colour, spellName, data):
		pygame.sprite.Sprite.__init__(self)
		self.add(data.spellTargeter)

		self.startEntity = startEntity
		self.colour = colour
		self.spellName = spellName

		self.outlineSurf = pygame.Surface((1, 1))
		self.outlineSurf.convert()
		self.outlineSurf.fill(colour)


	def update(self, data):
		hovered = self.getHovered(data)
		if hovered and hovered != self.startEntity:
			if data.input.mouseUnpressed == 1: # LEFT CLICK to cast spell
				self.kill()
				return (self.spellName, self.startEntity, hovered)
			self.drawOutline(hovered.maskOutline, hovered.rect.topleft, data.gameSurf)
			pygame.draw.line(data.gameSurf, self.colour, self.startEntity.rect.center, hovered.rect.center, 2)
		else:
			pygame.draw.line(data.gameSurf, self.colour, self.startEntity.rect.center, data.input.mousePos, 2)
		
		self.drawOutline(self.startEntity.maskOutline, self.startEntity.rect.topleft, data.gameSurf)

		if data.input.mouseUnpressed == 3: # RIGHT CLICK to cancel
			self.kill()
			return


	def getHovered(self, data):
		"""Get the hovered dynamic object"""
		for entity in data.dynamicObjects:
			if entity.rect.collidepoint(data.input.mousePos):
				return entity
		return None


	def drawOutline(self, pixels, offset, destSurf):
		"""Fills each of the pixels with self.colour"""
		offsetx, offsety = offset
		for pixel in pixels:
			x, y = pixel
			destSurf.blit(self.outlineSurf, (x + offsetx, y + offsety))