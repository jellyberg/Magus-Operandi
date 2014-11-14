# 
# a game by Adam Binks

import pygame, math, time


class Entity(pygame.sprite.Sprite):
	"""Base class for all in game objects"""
	def __init__(self, data):
		pygame.sprite.Sprite.__init__(self)
		self.add(data.entities)



class CollisionComponent:
	"""A component which will check if its master entity has collided with a static entity and correct its rect's position.
	This component should only be used on the dynamic/movable entities"""
	slowdownWhilePushing = -500 # slow the mob pushing this entity by x
	def __init__(self, master, collisionRect=None, useRectsForCollision=False):
		"""
		collisionRect can be a different sized rect to the rendering rect for more accurate collision detection.
		useRectsForCollision uses rect based collision rather than point based so collision detection is more reliable."""
		self.master = master
		self.master.isOnGround = False
		self.wasStandingOn = None
		self.collisionRect = collisionRect
		self.useRectsForCollision = useRectsForCollision


	def checkForWorldCollisions(self, data, useExtraAccuracy=False):
		"""
		Checks whether 9 collision points collide with the world geometry, and if so move the entity's rect"""
		if self.collisionRect:
			rect = self.collisionRect
			self.collisionRect.center = self.master.rect.center
		else:
			rect = self.master.rect

		if self.useRectsForCollision:
			collidedPoints = self.checkCollisionRects(data, rect, data.worldGeometry)

		else:  # use points
			collisionPoints = {'top': (rect.midtop), 'bottomC': (rect.midbottom), # points to check collision
							   'bottomL': (rect.left + 20, rect.bottom), 'bottomR': (rect.right - 20, rect.bottom),
							   'topleft': (rect.left, rect.top + 10), 'bottomleft': (rect.left, rect.bottom - 10),
							   'topright': (rect.right, rect.top + 10), 'bottomright': (rect.right, rect.bottom - 10)}
			# collidedPoints will be a dict with format {collisionPointName: platformCollided}
			collidedPoints = self.checkCollisionPoints(data, collisionPoints, data.worldGeometry)

		self.master.isOnGround = False # assume not on ground
		self.doCollision(collidedPoints, data)


	def checkCollisionPoints(self, data, pointsDict, groupToCollide):
		"""Checks whether each of the up to 6 passed collision points collides with a rect of any of the passed group"""
		collidedPoints = {}
		for obstacle in groupToCollide:
			for key in pointsDict:
				try:  # use collision rect if obstacle has one
					if obstacle.collisions.collisionRect.collidepoint(pointsDict[key]):
						collidedPoints[key] = obstacle
				except AttributeError:
					if obstacle.rect.collidepoint(pointsDict[key]):
						collidedPoints[key] = obstacle
		return collidedPoints


	def checkCollisionRects(self, data, rect, groupToCollide):
		"""Checks whether 4 areas of the passed rect collides with a rect of any of the passed group"""
		margin = rect.height / 5

		quadrants      = {'top': pygame.Rect((rect.left + margin, rect.top),
											 (rect.width - margin*2, rect.height / 4)),
						  'bottom': pygame.Rect((rect.left + margin, rect.bottom - rect.height / 4),
						  					    (rect.width - margin*2, rect.height / 4)),
						  'left': pygame.Rect((rect.left, rect.top + margin), 
						  					 (rect.width / 4, rect.height - margin*2)),
						  'right': pygame.Rect((rect.right - rect.width / 4, rect.top + margin), 
						  					   (rect.width / 4, rect.height - margin*2))}

		collidedRects = {}
		for obstacle in groupToCollide:
			for key in quadrants:
				try:  # use collision rect if obstacle has one
					if obstacle.collisions.collisionRect.colliderect(quadrants[key]):
						collidedRects[key] = obstacle
				except AttributeError:
					if obstacle.rect.colliderect(quadrants[key]):
						collidedRects[key] = obstacle

		return collidedRects


	def doCollision(self, collidedPoints, data):
		"""Moves the master's rect according to which points have been collided with. Returns True if rect has moved"""
		if self.collisionRect:
			rect = self.collisionRect
			self.collisionRect.center = self.master.rect.center
		else:
			rect = self.master.rect

		for key in collidedPoints:

			try: # use collision rect if entity has one
				if collidedPoints[key].collisions.collisionRect:
					collidedRect = collidedPoints[key].collisions.collisionRect
				else:
					collidedRect = collidedPoints[key].rect
			except AttributeError:
				collidedRect = collidedPoints[key].rect

			if key in ['bottomC', 'bottomL', 'bottomR', 'bottom']:
				rect.bottom = collidedRect.top
				self.master.isOnGround = True
				self.master.yVel = 0
			elif key == 'top':
				rect.top = collidedRect.bottom
				self.master.yVel = 0 # hit head against the ceiling
			elif key in ['topleft', 'bottomleft', 'left']:
				rect.left = collidedRect.right
			elif key in ['topright', 'bottomright', 'right']:
				rect.right = collidedRect.left

		self.master.rect.center = rect.center


	def checkIfBeingPushed(self, entitiesToBePushedBy, data):
		"""Checks whether 4 collision points collide with the entities to be pushed by, and if so move the entity's rect."""
		if self.collisionRect:
			rect = self.collisionRect
			self.collisionRect.center = self.master.rect.center
		else:
			rect = self.master.rect

		collisionPoints = {'topleft': (rect.left, rect.top + 10), 'bottomleft': (rect.left, rect.bottom - 10),
						   'topright': (rect.right, rect.top + 10), 'bottomright': (rect.right, rect.bottom - 10)} # points to check collision

		# collidedPoints will be a dict with format {collisionPointName: platformCollided}
		collidedPoints = self.checkCollisionPoints(data, collisionPoints, entitiesToBePushedBy)
		self.doCollision(collidedPoints, data)

		# if applicable, slow the pusher's movespeed by slowdownWhilePushing while pushing
		for key in collidedPoints:
			self.master.movedThisFrame = True
			pusher = collidedPoints[key]

			if hasattr(pusher, 'moveSpeedModifier'):
				if key in ['topright', 'bottomright']:
					pusher.moveSpeedModifier['left'] = CollisionComponent.slowdownWhilePushing
				if key in ['topleft', 'bottomleft']:
					pusher.moveSpeedModifier['right'] = CollisionComponent.slowdownWhilePushing

			
			if hasattr(pusher, 'animation'):
				if pusher.movedThisFrame:
					pusher.animation.play('push' + pusher.facing)


	def checkIfStandingOn(self, entitiesToStandOn, data):
		if self.collisionRect:
			rect = self.collisionRect
			self.collisionRect.center = self.master.rect.center
		else:
			rect = self.master.rect
		collisionPoints = {'bottomC': (rect.midbottom),
						   'bottomL': (rect.left + 30, rect.bottom), 'bottomR': (rect.right - 30, rect.bottom)}
		# collidedPoints will be a dict with format {collisionPointName: entityCollided}
		collidedPoints = self.checkCollisionPoints(data, collisionPoints, entitiesToStandOn)
		self.doCollision(collidedPoints, data)
		for point in collidedPoints:
			if point:
				self.wasStandingOn = point



class GravityComponent:
	"""A component which will update its master's y velocity and rect's y coordinates"""
	gravity = 800
	terminalVelocity = 400
	def __init__(self, master):
		self.master = master
		self.master.yVel = 0
		self.master.isOnGround = False


	def update(self, data):
		if not self.master.isOnGround or (self.master.weight < 0 or self.master.yVel < 0): # on ground or floats
			self.master.yVel += GravityComponent.gravity * data.dt
			if self.master.yVel > GravityComponent.terminalVelocity:
				self.master.yVel = GravityComponent.terminalVelocity

			
			if self.master in data.dynamicObjects:
				self.master.movedThisFrame = True

		if self.master.yVel != 0:
			self.master.rect.y += math.ceil(self.master.yVel * data.dt) * self.master.weight



class EnchantmentComponent:
	"""This component allows an entity to be affected by targeted spells"""
	def __init__(self, master):
		self.master = master
		self.soulBound = None
		self.isSoulBinder = False


	def update(self, data):
		"""Update's all enchantments the master entity is under the effect of"""
		if self.soulBound:
			if not self.soulBound in data.entities:
				self.removeSoulBind()
				return
			
			if self.isSoulBinder: # only run this code for one of the two entities
				pygame.draw.line(data.gameSurf, data.RED, self.master.rect.center, self.soulBound.rect.center, 2)

			rectOffset = self.getRectOffset(self.master.rect, self.soulBound.rect)
			if rectOffset != self.soulBoundOffset: # need to update one of the rects
				if self.soulBound.movedThisFrame:
					xToMove = self.soulBoundOffset[0] - rectOffset[0]

					if xToMove:
						# MOVE BIT BY BIT UNTIL COLLIDES WITH A WALL OR REACHES THE CORRECT OFFSET
						rect = self.master.rect
						if xToMove > 0:
							step = data.CELLSIZE / 3
						else:
							step = -(data.CELLSIZE / 3)

						for x in range(0, xToMove, step):
							self.master.rect.move_ip(x, 0)
							collidedPoints = self.master.collisions.checkCollisionPoints(data,
								{'topleft': (rect.left, rect.top + 10), 'bottomleft': (rect.left, rect.bottom - 10),
							   'topright': (rect.right, rect.top + 10), 'bottomright': (rect.right, rect.bottom - 10)},
							   data.worldGeometry)
							if collidedPoints:
								self.soulBoundOffset = self.getRectOffset(self.master.rect, self.soulBound.rect)
								self.soulBound.enchantments.soulBoundOffset = self.getRectOffset(self.soulBound.rect, self.master.rect)
								self.master.rect.move_ip(-1, 0)
								break

					if self.soulBound.yVel != 0:
						self.master.yVel = self.soulBound.yVel * 100

		self.master.lastRectTopleft = self.master.rect.topleft
		self.master.movedThisFrame = False


	def bindSoulTo(self, target):
		"""When entity A's (master) soul is bound to entity B (target), entity A's movements also act upon entity B and vice versa"""
		target.enchantments.removeSoulBind() # entities may only be bound to one other entity
		self.soulBound = target
		self.isSoulBinder = True
		target.enchantments.isSoulBinder = False
		target.enchantments.soulBound = self.master
		self.soulBoundOffset = self.getRectOffset(self.master.rect, target.rect)
		target.enchantments.soulBoundOffset = self.getRectOffset(target.rect, self.master.rect)
		self.master.lastRectTopleft = self.master.rect.topleft
		target.lastRectTopleft = target.rect.topleft


	def getRectOffset(self, rect1, rect2):
		"""Returns a tuple of the x difference and y difference of the two rects"""
		return (rect1.left - rect2.left, rect1.top - rect2.top)


	def removeSoulBind(self, isInitial=True):
		"""Removes any remnants of soul binding"""
		if self.soulBound and isInitial:
			self.soulBound.enchantments.removeSoulBind(False)
		self.soulBound = None
		self.isSoulBinder = False



class AnimationComponent:
	"""A component which handles animations for an entity"""
	def __init__(self, master, animsDict):
		"""animsDict has format {'name': {'spritesheet': [Surface], 'imageWidth': [int], 'timePerFrame': [float], 'flip': [bool]}}"""
		self.master = master

		for key in animsDict:
			animsDict[key]['spritesheet'].convert_alpha()

		self.framesDict = {}
		self.secsPerFrameDict = {}

		for key in animsDict:
			if animsDict[key]['flip']:
				a, b = self.snipSpritesheet(animsDict[key]['spritesheet'], animsDict[key]['imageWidth'], animsDict[key]['flip'])
				self.framesDict[key + 'R'] = a
				self.framesDict[key + 'L'] = b

				self.secsPerFrameDict[key + 'R'] = self.secsPerFrameDict[key + 'L'] = animsDict[key]['timePerFrame']

			else: 	# do not flip
				a = self.snipSpritesheet(animsDict[key]['spritesheet'], animsDict[key]['imageWidth'], animsDict[key]['flip'])
				self.framesDict[key] = a

		self.animName = None
		self.lastAnimTime = time.time()
		self.frame = 0
		self.nextAnim = None


	def snipSpritesheet(self, sheet, imgWidth, flip):
		"""Returns a list of frames in the spritesheet. If flip=True it also returns a list of x-flipped frames"""
		frames = []
		flippedFrames = []

		for x in range(0, sheet.get_width(), imgWidth):
			if x + imgWidth > sheet.get_width():
				break
			frameRect = pygame.Rect((x, 0), (imgWidth, sheet.get_height()))
			frames.append(sheet.subsurface(frameRect))

			if flip:
				flippedFrames.append(pygame.transform.flip(sheet.subsurface(frameRect), 1, 0))

		return (frames, flippedFrames)


	def play(self, animName):
		"""Starts the selected animation playing"""
		if self.animName != animName: # self.animName and self.animName not in animName:  # only if animName is not previous animName L or R
			self.animName = animName
			self.lastAnimTime = 0
			self.frame = -1


	def playOnce(self, animName, playNext=None):
		"""Start the selected animation then reverts to playNext or previous anim when finished"""
		if not playNext: # play previous anim
			self.nextAnim = self.animName
		else:
			self.nextAnim = playNext

		self.animName = animName
		self.lastAnimTime = 0
		self.frame = -1


	def switchDirection(self, direction):
		"""Changes the direction of the current animation to direction. Must have same number of frames"""
		assert direction in ('R', 'L'), 'switchDirection direction must be R or L.'
		if self.animName[-1] in ('R', 'L'):
			self.animName = self.animName[:-1]
			self.animName += direction
		if self.nextAnim and self.nextAnim[-1] in ('R', 'L'):
			self.nextAnim = self.nextAnim[:-1]
			self.nextAnim += direction


	def update(self):
		"""Update master.image with the correct frame of the animation"""
		if time.time() - self.lastAnimTime > self.secsPerFrameDict[self.animName]:
			# UPDATE IMAGE AND FRAME
			self.frame += 1
			if self.frame >= len(self.framesDict[self.animName]):
				if self.nextAnim: # has played anim once, must revert to prev anim
					self.play(self.nextAnim)
					self.nextAnim = None
				
				self.frame = 0

			self.master.image = self.framesDict[self.animName][self.frame]

			self.lastAnimTime = time.time()
