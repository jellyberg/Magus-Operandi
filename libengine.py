# MAGUS OPERANDI
# a game by Adam Binks

import pygame, input, game
from pygame.locals import *

WINDOWEDMODE = True

def run():
	stateHandler = StateHandler()
	while True:
		stateHandler.update()


class StateHandler:
	"""handles menu and game state, runs boilerplate update code"""
	def __init__(self):
		self.data = Data()
		self.data.screen.fill((135, 206, 250))
		pygame.display.set_caption('Magus Operandi')

		# START GAME
		self.data.newLevel()
		self.gameHandler = game.GameHandler(self.data)
		self.data.gameHandler = self.gameHandler


	def update(self):
		self.data.input.get()
		self.data.dt = self.data.FPSClock.tick(self.data.FPS) / 1000.0

		# update game/menu objs
		self.gameHandler.update(self.data)

		pygame.display.update()
		pygame.display.set_caption('Magus Operandi   FPS: %s' %(int(self.data.FPSClock.get_fps())))



class Data:
	"""stores variables to be accessed in many parts of the game"""
	def __init__(self):
		if not WINDOWEDMODE:
			screenInfo = pygame.display.Info()
			self.WINDOWWIDTH, self.WINDOWHEIGHT = (screenInfo.current_w, screenInfo.current_h)
			self.screen = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT), FULLSCREEN)
		if WINDOWEDMODE:
			self.WINDOWWIDTH, self.WINDOWHEIGHT = (1450, 1050)
			self.screen = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
		self.gameSurf = pygame.Surface(self.screen.get_size())
		self.gameSurf.convert()

		self.FPS = 60
		self.FPSClock = pygame.time.Clock()
		self.FPSClock.tick(self.FPS) # so the first dt value isnt really weird

		self.input = input.Input()
		self.currentLevel = 0 # TEMP FOR TESTING should normally be = 0

		self.CELLSIZE = 64

		self.keybinds = {'left': [K_LEFT, K_a], 'right': [K_RIGHT, K_d],
						 'jump': [K_SPACE, K_UP, K_w]}

		self.WHITE     = (255, 255, 255)
		self.BLACK     = (  0,   0,   0)
		self.RED       = (220,  20,  20)
		self.SKYBLUE   = (135, 206, 250)
		self.DARKBLUE  = (  0,  35, 102)
		self.YELLOW    = (255, 255, 102)
		self.DARKYELLOW= (204, 204,   0)
		self.GREEN     = (110, 255, 100)
		self.ORANGE    = (255, 165,   0)
		self.DARKGREY  = ( 60,  60,  60)
		self.LIGHTGREY = (180, 180, 180)
		self.CREAM     = (255, 255, 204)


	def newLevel(self):
		"""Called just before a new level is loaded to reset everything"""
		self.entities = pygame.sprite.Group()
		self.staticObjects = pygame.sprite.Group()
		self.dynamicObjects = pygame.sprite.Group()
		self.worldGeometry = pygame.sprite.Group()

		self.platforms = pygame.sprite.Group()
		self.exits = pygame.sprite.Group()
		
		self.crates = pygame.sprite.Group()
		self.keys = pygame.sprite.Group()
		self.locks = pygame.sprite.Group()
		self.unlockableWithKeys = pygame.sprite.Group()
		self.balloons = pygame.sprite.Group()

		self.mobs = pygame.sprite.Group()
		self.playerGroup = pygame.sprite.Group()

		self.spellTargeter = pygame.sprite.GroupSingle()


	def saveGame(self):
		pass


	def loadGame(self):
		pass


if __name__ == '__main__':
	run()