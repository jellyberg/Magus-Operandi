#
# a game by Adam Binks

import pygame, mob
from components import Entity

class GameHandler:
	def __init__(self, data):
		self.genWorld(data)

		#TEMP
		self.player = mob.Player(data)


	def update(self, data):
		data.gameSurf.fill((50, 50, 50))

		self.player.update(data)

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
		"P  PPPPPP               P",
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
		"P        PP   P         P",
		"P            PP         P",
		"P          PP P         P",
		"P       PP    P         P",
		"P      PPPP   P         P",
		"PPPPPPPPPPPPPPPPPPPPPPPPP",]
		# build the level
		for row in level:
			for col in row:
				if col == "P":
					Platform((x, y), platformSurf, data)
				x += 32
			y += 32
			x = 0



class Platform(Entity):
	"""A simple static platform"""
	def __init__(self, topleft, image, data):
		Entity.__init__(self, data)
		self.add(data.platforms)

		self.image = image
		self.rect = image.get_rect()
		self.rect.topleft = topleft