import pygame, input, math, pickle, os
from pygame.locals import *

pygame.init()

screenInfo = pygame.display.Info()
WINDOWWIDTH, WINDOWHEIGHT = (1450, 900)
screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
FPSClock = pygame.time.Clock()

input = input.Input()
BASICFONT  = pygame.font.Font('assets/fonts/roboto medium.ttf', 14)
MEDIUMFONT = pygame.font.Font('assets/fonts/roboto regular.ttf', 16)
BIGFONT    = pygame.font.Font('assets/fonts/roboto regular.ttf', 25)
pygame.display.set_caption('Magus Operandi Level Editor')

CELLSIZE = 64

TILETYPES = ['platform', 'exit', 'lock', 'key', 'crate', 'balloon', 'playerSpawn']
selectedTileType = 'platform'
tileImages = {}
tileImagesList = []  # ordered list for the tile picker to display
for tile in TILETYPES:
	img = pygame.image.load('assets/objects/%s.png' %(tile))
	tileImages[tile] = img
	tileImagesList.append(img)



def genText(text, topLeftPos, colour, font):
	surf = font.render(text, 1, colour)
	surf.set_colorkey((0,0,0))
	rect = surf.get_rect()
	rect.topleft = topLeftPos
	return (surf, rect)



class ModalInput:
	"""Lets the user enter a number or string"""
	def __init__(self, topleft, inputType, label):
		self.inputType = inputType
		self.labelSurf, self.labelRect = genText(label + ': ', topleft, (0, 0, 0), BIGFONT)
		self.output = ''

		if inputType == 'number':
			self.validInputs = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
		elif inputType == 'text':
			self.validInputs = [K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, K_l, K_m, K_n, K_o,
			K_p, K_q, K_r, K_s, K_t, K_u, K_v, K_w, K_x, K_y, K_z, K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, 
			K_8, K_9, K_SPACE]


	def update(self):
		for key in input.unpressedKeys:
			if key == K_RETURN and self.output:
				if self.inputType == 'number':
					return int(self.output)
				else:
					return self.output

			if key == K_BACKSPACE:
				self.output = self.output[:-1]  # remove last character inputted

			if key in self.validInputs:
				if pygame.key.name(key) == 'space':
					self.output += ' '
				else: 
					self.output += pygame.key.name(key)

		outputSurf, outputRect = genText(self.output, self.labelRect.topright, (0, 0, 0), BIGFONT)
		screen.blit(outputSurf, outputRect)
		screen.blit(self.labelSurf, self.labelRect)




class LevelData:
	"""Stores level so far and blits it to the screen when draw() is called"""
	def __init__(self, name, levelSize=None, dataDict=None):
		"""Either create a new level file by passing levelSize or load in a previously created one by passing dataDict"""
		self.name = name

		if levelSize:
			self.levelSize = levelSize
			self.data = []
			for x in range(levelSize[0]):
				column = []
				for y in range(levelSize[1]):
					column.append(' ')
				self.data.append(column)

		elif dataDict:
			self.data = dataDict
			levelSize = (len(self.data), len(self.data[0]))

		self.surf = pygame.Surface((levelSize[0] * CELLSIZE, levelSize[1] * CELLSIZE))
		self.rect = self.surf.get_rect()
		self.rect.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)


	def update(self):
		self.surf.fill((180, 180, 180)) # light grey
		
		if input.mousePressed and self.rect.collidepoint(input.mousePos):
			hoveredPixel = (input.mousePos[0] - self.rect.left, input.mousePos[1] - self.rect.top)
			hoveredCell = (int(math.floor(hoveredPixel[0] / CELLSIZE)), int(math.floor(hoveredPixel[1] / CELLSIZE)))

			if input.mousePressed == 1:
				self.data[hoveredCell[0]][hoveredCell[1]] = selectedTileType
			elif input.mousePressed == 3:
				self.data[hoveredCell[0]][hoveredCell[1]] = ' '

		if K_RETURN in input.unpressedKeys and (K_RCTRL in input.unpressedKeys or K_LCTRL in input.unpressedKeys):
			self.export()
			return 'finished'

		self.draw()



	def draw(self):
		for x in range(len(self.data)):
			for y in range(len(self.data[0])):
				if self.data[x][y] != ' ':
					img = tileImages[self.data[x][y]]
					rect = img.get_rect(midbottom = (x * CELLSIZE + CELLSIZE / 2, (y + 1) * CELLSIZE))
					self.surf.blit(img, rect)
		screen.blit(self.surf, self.rect)


	def export(self):
		with open('assets/levels/%s.pickle' %(self.name), 'wb') as handle:
			pickle.dump(self.data, handle)



class TilePicker:
	"""A bar across the bottom of the screen to select a tile to paint onto the level"""
	tilesInRow = 10
	def __init__(self):
		self.currentTab = 0
		self.selectedTileNum = 0
		self.numTabs = int(math.ceil(len(TILETYPES) / float(TilePicker.tilesInRow)))

		# make an overlay with a grid and numbers in the top left of each tile
		self.overlay = pygame.Surface((CELLSIZE * TilePicker.tilesInRow, CELLSIZE))
		self.overlay.fill((1, 2, 3))
		self.overlay.set_colorkey((1, 2, 3))

		self.rect = self.overlay.get_rect(midbottom=(WINDOWWIDTH / 2, WINDOWHEIGHT))

		for i in range(0, TilePicker.tilesInRow):
			if i == 0: text = '0' # TEMP, TODO '`'   # to correspond with keyboard layout
			else: text = str(i)

			numSurf, numRect = genText(text, (i * CELLSIZE, 0), (255, 255, 255), BASICFONT)
			self.overlay.blit(numSurf, numRect)

			pygame.draw.line(self.overlay, (50, 50, 50), 
				(i * CELLSIZE, 0), (i * CELLSIZE, self.rect.height))

		self.surf = pygame.Surface(self.overlay.get_size())
		self.surf.set_alpha(200)

		self.selectedImg = pygame.Surface((CELLSIZE, CELLSIZE))
		self.selectedImg.fill((100, 100, 255))
		self.selectedImg.set_alpha(150)


	def update(self):
		# scroll selectable tiles up and down with mousewheel
		if input.mouseUnpressed == 4:  # scroll up
			self.currentTab -= 1
		if input.mouseUnpressed == 5:  # scroll down
			self.currentTab += 1
		if self.currentTab < 0:
			self.currentTab = self.numTabs
		if self.currentTab > self.numTabs:
			self.currentTab = 0

		self.draw()

		numberKeys = [K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9]
		for i in range(len(numberKeys)):
			if numberKeys[i] in input.unpressedKeys or (i == 0 and K_BACKQUOTE in input.unpressedKeys):
				newSelectedTileNum = self.currentTab * TilePicker.tilesInRow + i
				if newSelectedTileNum < len(TILETYPES):
					self.selectedTileNum = newSelectedTileNum
					return TILETYPES[newSelectedTileNum]  # new selected tile type


	def draw(self):
		self.surf.fill((100, 100, 100))

		for i in range(TilePicker.tilesInRow):
			if i + self.currentTab * len(TILETYPES) < len(TILETYPES):
				img = tileImagesList[self.currentTab * TilePicker.tilesInRow + i]
				rect = img.get_rect(center=(i * CELLSIZE + CELLSIZE / 2, CELLSIZE / 2))
				self.surf.blit(img, rect)

				if i + self.currentTab * len(TILETYPES) == self.selectedTileNum:
					self.surf.blit(self.selectedImg, (i * CELLSIZE, 0))

		tabSurf, tabRect = genText(str(self.currentTab), (self.rect.left - 20, self.rect.top + 20), (50, 50, 50), BIGFONT)
		screen.blit(tabSurf, tabRect)

		screen.blit(self.surf, self.rect)
		screen.blit(self.overlay, self.rect)




mode = 'input title'
modalInput = ModalInput((200, WINDOWHEIGHT / 2), 'text', 'Level name')
while True:
	input.get()
	screen.fill((255, 255, 255))

	if mode == 'input title':
		output = modalInput.update()
		if output != None:
			levelName = output

			if os.path.exists('assets/levels/%s.pickle' %(levelName)):
				mode = 'edit level'
				with open('assets/levels/%s.pickle' %(levelName), 'rb') as handle:
					loadedLevelData = pickle.load(handle)
				levelData = LevelData(levelName, dataDict=loadedLevelData)
				tilePicker = TilePicker()

			else:
				modalInput = ModalInput((200, WINDOWHEIGHT / 2), 'number', 'Level x cells')
				mode = 'input x cells'
	if mode == 'input x cells':
		output = modalInput.update()
		if output != None:
			xCells = output
			modalInput = ModalInput((200, WINDOWHEIGHT / 2), 'number', 'Level y cells')
			mode = 'input y cells'
	if mode == 'input y cells':
		output = modalInput.update()
		if output != None:
			yCells = output
			mode = 'edit level'

			levelData = LevelData(levelName, levelSize=(xCells, yCells))
			tilePicker = TilePicker()
	if mode == 'edit level':
		isFinished = levelData.update()
		output = tilePicker.update()
		if output != None:
			selectedTileType = output

		if isFinished:
			mode = 'input title'
			modalInput = ModalInput((200, WINDOWHEIGHT / 2), 'text', 'Level saved!    New level name')

	pygame.display.update()
	FPSClock.tick(60)