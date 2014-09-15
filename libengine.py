# MAGUS OPERANDI
# a game by Adam Binks

import pygame, input, game

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
		self.data.newGame()
		self.gameHandler = game.GameHandler(self.data)


	def update(self):
		self.data.input.get()
		self.data.dt = self.data.FPSClock.tick(self.data.FPS) / 1000.0

		# update game/menu objs
		self.gameHandler.update(self.data)

		pygame.display.update()



class Data:
	"""stores variables to be accessed in many parts of the game"""
	def __init__(self):
		self.WINDOWWIDTH, self.WINDOWHEIGHT = (1200, 800)
		self.screen = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
		self.gameSurf = pygame.Surface(self.screen.get_size())
		self.gameSurf.convert()

		self.FPS = 60
		self.FPSClock = pygame.time.Clock()
		self.FPSClock.tick(self.FPS) # so the first dt value isnt really wierd

		self.input = input.Input()


	def newGame(self):
		self.entities = pygame.sprite.Group()
		self.platforms = pygame.sprite.Group()


	def saveGame(self):
		pass


if __name__ == '__main__':
	run()