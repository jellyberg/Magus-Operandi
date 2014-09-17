#
# a game by Adam Binks

import pygame
from object import Platform, Exit, Crate
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
		data.screen.blit(data.gameSurf, (0, 0))


	def nextLevel(self, data):
		"""Load and start the next level"""
		data.currentLevel += 1 # starts at 0
		data.newLevel()
		self.loadLevelFile(GameHandler.levelFileNames[data.currentLevel], data)


	def loadLevelFile(self, filename, data):
		"""Load a level from a .txt file in the folder assets/levels"""
		# TEMP
		platformSurf = pygame.Surface((32, 32))
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
				if col == '*':
					Player((x, y), data)
				x += 32
			y += 32
			x = 0