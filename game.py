#
# a game by Adam Binks

import pygame, mob
from object import Platform, Crate

class GameHandler:
	def __init__(self, data):
		self.genWorld(data)

		#TEMP
		self.player = mob.Player(data)


	def update(self, data):
		data.gameSurf.fill((50, 50, 50))

		self.player.update(data)

		for object in data.dynamicObjects:
			object.update(data)

		data.entities.draw(data.gameSurf)
		data.screen.blit(data.gameSurf, (0, 0))


	def genWorld(self, data):
		# MOSTLY TEMPORARY
		platformSurf = pygame.Surface((32, 32))
		platformSurf.fill((50, 200, 60))

		x = y = 0
		level = [
		"PPPPPPPPPPPPPPPPPPPPPPPPP",
		"P  P                    P",
		"P  PPPPPP     C         P",
		"P  P     P    P         P",
		"P  P      P   P         P",
		"P  P       P  P         P",
		"P  P         PP    PPPPPP",
		"P  P        P P         P",
		"P  P       P  P         P",
		"P  P      P   PPPPPP    P",
		"P  P     P    PP        P",
		"P  P PP       PPP      PP",
		"P  PPPPP      PPPP    PPP",
		"P       P     PPPPP  PPPP",
		"P        PP   P CCCCCCC P",
		"P       C    PP CCCCCCC P",
		"P          PP P CCCCCCC P",
		"P       PP    P CCCCCCC P",
		"P      PPPP   P CCCCCCC P",
		"PPPPPPPPPPPPPPPPPPPPPPPPP",]
		# build the level
		for row in level:
			for col in row:
				if col == "P":
					Platform((x, y), platformSurf, data)
				if col == 'C':
					Crate((x, y), data)
				x += 32
			y += 32
			x = 0