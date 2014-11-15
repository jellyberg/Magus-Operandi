#
# a game by Adam Binks

import pygame, pickle
from object import Platform, Exit, Crate, Balloon, Key, Lock
from mob import Player

class GameHandler:
	levelFileNames = ['basic platforming', 'basic crates', 'lock and key', 'introducing keys', 'test level']
	startLevel = 'introducing keys' # temp
	def __init__(self, data):
		data.currentLevel = GameHandler.levelFileNames.index(GameHandler.startLevel) # temp
		self.loadLevelFile(GameHandler.levelFileNames[data.currentLevel], data)


	def update(self, data):
		data.gameMousePos = (data.input.mousePos[0] - data.gameRect.left, data.input.mousePos[1] - data.gameRect.top)

		if pygame.locals.K_r in data.input.unpressedKeys:
			data.currentLevel -= 1
			self.nextLevel(data)

		data.gameSurf.fill((170, 192, 171))

		for player in data.playerGroup:
			player.update(data)

		for dynObject in data.dynamicObjects:
			dynObject.update(data)

		data.staticObjects.draw(data.gameSurf)
		data.dynamicObjects.draw(data.gameSurf)
		data.playerGroup.draw(data.gameSurf)

		if data.spellTargeter:
			for targeter in data.spellTargeter: # there is only one but this a workaround to get the return value
				result = targeter.update(data)

			if result is not None:
				spellCast, spellRoot, spellTarget = result
				if spellCast == 'soulbind':
					spellRoot.enchantments.bindSoulTo(spellTarget)

		data.screen.blit(data.gameSurf, data.gameRect)


	def nextLevel(self, data):
		"""Load and start the next level"""
		data.currentLevel += 1 # starts at 0
		if data.currentLevel >= len(GameHandler.levelFileNames):
			data.input.terminate()
		data.newLevel()
		self.loadLevelFile(GameHandler.levelFileNames[data.currentLevel], data)


	def loadLevelFile(self, filename, data):
		"""Load a level from a .pickle file in the folder assets/levels"""
		data.screen.fill((20, 20, 20))
		# TEMP
		platformSurf = pygame.image.load('assets/objects/platform.png')
		platformSurf.convert_alpha()

		Exit.image = pygame.image.load('assets/objects/exit.png')

		with open('assets/levels/%s.pickle' %(filename), 'rb') as handle:
			level = pickle.load(handle)
		x = y = 0

		# build the level
		for row in level:
			for tile in row:
				if 'platform' in tile:
					Platform((x, y), platformSurf, data)
				if tile == 'exit':
					Exit((x + data.CELLSIZE / 2, y + data.CELLSIZE - 1), data)   # place objects at the midbottom of the cell
				if tile == 'crate':
					Crate((x + data.CELLSIZE / 2, y + data.CELLSIZE - 1), data)
				if tile == 'balloon':
					Balloon((x + data.CELLSIZE / 2, y + data.CELLSIZE - 1), data)
				if tile == 'key':
					Key((x + data.CELLSIZE / 2, y + data.CELLSIZE - 1), data)
				if tile == 'lock':
					Lock((x + data.CELLSIZE / 2, y + data.CELLSIZE - 1), data)
				if tile == 'playerSpawn':
					Player((x + data.CELLSIZE / 2, y + data.CELLSIZE - 1), data)
				y += data.CELLSIZE
			x += data.CELLSIZE
			y = 0

		data.levelWidth = len(level) * data.CELLSIZE
		data.levelHeight = len(level[0]) * data.CELLSIZE

		data.gameSurf = pygame.Surface((data.levelWidth, data.levelHeight))
		data.gameSurf.convert()

		data.gameRect = data.gameSurf.get_rect()
		data.gameRect.center = (data.WINDOWWIDTH / 2, data.WINDOWHEIGHT / 2)