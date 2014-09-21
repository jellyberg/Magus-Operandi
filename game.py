#
# a game by Adam Binks

import pygame
from object import Platform, Exit, Crate, Balloon
from mob import Player

class GameHandler:
	levelFileNames = ['testLevel', 'testLevel2']
	def __init__(self, data):
		self.loadLevelFile('testLevel', data)


	def update(self, data):
		data.gameSurf.fill((50, 50, 50))

		for player in data.playerGroup:
			player.update(data)

		for object in data.dynamicObjects:
			object.update(data)

		data.entities.draw(data.gameSurf)

		if data.spellTargeter:
			for targeter in data.spellTargeter: # there is only one but this a workaround to get the return value
				result = targeter.update(data)

			if result is not None:
				spellCast, spellRoot, spellTarget = result
				if spellCast == 'soulbind':
					spellRoot.enchantments.bindSoulTo(spellTarget)

		data.screen.blit(data.gameSurf, (0, 0))


	def nextLevel(self, data):
		"""Load and start the next level"""
		data.currentLevel += 1 # starts at 0
		if data.currentLevel >= len(GameHandler.levelFileNames):
			data.input.terminate()
		data.newLevel()
		self.loadLevelFile(GameHandler.levelFileNames[data.currentLevel], data)


	def loadLevelFile(self, filename, data):
		"""Load a level from a .txt file in the folder assets/levels"""
		# TEMP
		platformSurf = pygame.Surface((data.CELLSIZE, data.CELLSIZE))
		platformSurf.fill((50, 200, 60))

		level = open('assets/levels/' + filename + '.txt', 'r')
		x = y = 0
		# build the level
		for row in level:
			for col in row:
				col = col.upper()
				if col == "P":
					Platform((x, y), platformSurf, data)
				if col == 'E':
					Exit((x, y), data)
				if col == 'C':
					Crate((x, y), data)
				if col == 'B':
					Balloon((x, y), data)
				if col == '*':
					Player((x, y), data)
				x += data.CELLSIZE
			y += data.CELLSIZE
			x = 0