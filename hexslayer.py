#!/usr/bin/python

import pygame, random, time
from pygame.locals import *

from pawns import *
from hexmath import *
from controls import *


if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'
tilesize = 32

pygame.init()
screen = pygame.display.set_mode((640,480))
pygame.display.set_caption('HexSLayer')

playerColors = ("#66FF33","#003DF5","#FF3366","#33FFCC","#FFCC33","#FF6633")

background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill((250, 250, 250))

infobarLocation =(25,455)
storeLocation = (325,450)



selected = None




class Village(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPosition(gameMap,xloc,yloc)
		self.xloc = xloc
		self.yloc = yloc
		self.balance = 5
		self.image = pygame.image.load("village.png")
		gameMap.renders.append(self)
		
class Realm(list):
	def __init__(self):
		self.size = 0
		self.elements = []
	
	

class Tile(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		#self.image = pygame.Surface([tilesize, tilesize])
		self.x,self.y = convertGridPosition(gameMap,xloc,yloc)
		self.xloc = xloc
		self.yloc = yloc
		self.setPlayer(random.randint(0,5))
		self.rect = self.draw()
		self.selected = False
		self.pawn = None
		self.village = None
		self.gameMap = gameMap
		self.grave = None
		self.realm = None
		

	# Changes the owner of a tile, redraws, and fixes the realm.
	def setPlayer(self,player):
		self.player = player
		self.color = pygame.Color(playerColors[self.player])
		self.draw()
		
		
		self.realm.remove(self)
		
		realm = self.gameMap.getTileSet(self.getPoint())
		if len(realm) > 1:
			if realm[0] == self:
				self.realm = realm[1].realm
			else:
				self.realm = realm[0].realm
			self.realm.append(self)
			
		
		
	def draw(self):
		rect = pygame.draw.polygon(background,self.color,self.getHex(),0)
		pygame.draw.polygon(background,pygame.Color("#000000"),self.getHex(),1)
		#pygame.display.update()
		
		return rect
	
	def getHex(self):
		return getHexAt(self.x,self.y)
		
	def getPoint(self):
		return (self.xloc,self.yloc)
		
	def checkHexCollision(self,point):
		s = tilesize
		l = .25
		x = point[0] - self.x
		y = point[1] - self.y
		#print "Mouse Hit:",x,"X",y," is it less than ",s/2
		#print "1,2,3,4:",(2*x + y),",",(2*x + (s-y)),",",(2*(s-x)+y),",",(2*(s-x)+(s-y))
		
		if ((2*x + y) <  s/2) or ((2*x + (s-y)) < s/2) or ((2*(s-x)+y) < s/2) or ((2*(s-x)+(s-y)) < s/2):
			# Failed hitdetection on hex
			return 0
		else:
			return 1
	def getAdjacent(self,direction):
		return getAdjacent(self.xloc,self.yloc,direction)
	def getAdjacentTile(self,direction):
		return self.gameMap.getTile(self.getAdjacent(direction))
	def isAdjacent(self,point):
		#print "Checking for adjacency."
		for dir in range(6):
			target = self.getAdjacent(dir)
			if(target == point):
				#print "Target was adjacent to this square"
				return True
		return False
			
	def select(self):
		#print "Selecting tile."
		pygame.draw.polygon(background,pygame.Color("#FFFFFF"),self.getHex(),1)
		self.selected = True
	def deselect(self):
		#print "Deselecting tile"
		self.draw()
		self.selected = False
	def addPawn(self,pawn):
		self.pawn = pawn
		return pawn
	def buyVillager(self):
		gameMap.getTileSet
		if not self.village or self.village.balance < 10:
			return None
		else:
			self.village.balance -= 10
			return Villager(self.gameMap,0,0)
			

class Map():
	def __init__(self):
		self.width = 13
		self.height = 25
		self.x = 5
		self.y = 30
		
		self.turn = 0
		self.selectedSetIncome = 0
		self.selectedSetUpkeep = 0
		
		self.tiles = []
		self.alltiles = []
		self.renders = []
		self.selectedSet = []
		self.selectedVillage = None
		self.infoBar = None
		
		for y in range(self.height):
			
			row = [None]*self.width
			for x in range(self.width):
				row[x] = Tile(self,x,y)
				self.alltiles.append(row[x])
			self.tiles.append(row)
			
		# setup Realms for newly created tiles.
		for row in self.tiles:
			for tile in row:
				if not tile.realm:
					realm = self.getTileSet(tile.getPoint())
					if len(realm) > 1:
						
						kingdom = Realm()
						kingdom.size = len(realm)
						kingdom.elements = realm
						for spot in kingdom:
							spot.realm = kingdom
			
	def hexClicked(self,x,y):
		retval = None
		#print "Clicked tile: %sx%s" % (self.tiles[y][x].xloc,self.tiles[y][x].yloc)
		clickedTile = self.tiles[y][x]
		if(clickedTile.pawn != None and clickedTile.pawn.moved == False):
			retval = clickedTile.pawn
			
		
		
		if not retval:
			for tile in self.selectedSet:
				tile.deselect()
			self.selectSet((x,y))
					
					
		return retval
		
	def hexDropped(self,carry,x,y):
		clickedTile = self.tiles[y][x]
		carry.setPos(x,y)
		#print "Set the position of the carry to ",x,"X",y
		
	def getTile(self,point):
		#print "Looking for",point
		if point[1] < 0 or point[1] >= self.height or point[0] < 0 or point[0] >= self.width:
			return None
		return self.tiles[point[1]][point[0]]
		
	def selectSet(self,point):
		self.selectedSet = self.getTileSet(point)
		
		income = 0
		balance = 0
		upkeep = 0
		for tile in self.selectedSet:
			tile.select()
			income += 1
			if tile.pawn:
				upkeep += tile.pawn.upkeep
			if(tile.village):
				balance = tile.village.balance
				self.selectedVillage = tile.village
		if(income == 1):
			income = 0
		self.selectedSetUpkeep = upkeep
		self.changeIncome(income)

			
		
			
	
	#We are going to do a breadth first search to find all connected tiles of same color
	def getTileSet(self,point):
		tile = self.getTile(point)
		searched = []
		toSearch = [tile]
		found = [tile]
		while(len(toSearch) >0):
			searching = toSearch.pop()
			searched.append(searching)
		
			for i in range(6):
				considered = self.getTile(searching.getAdjacent(i))
				if considered and searching.player == considered.player:
					#print "Was same color"
					if considered not in searched and considered not in toSearch:
						toSearch.append(considered)
					if considered not in found:
						found.append(considered)
		#print "Our search found: ",found
		return found
		
	# Adds, splits villages
	# @TODO, clean up this method, it is super redudant (checks each set once for each tile in the set)
	def cleanUpGame(self):
		print "Cleaning up the game, all realms should be set properly still."
		for row in self.tiles:
			for tile in row:
				realm = self.getTileSet(tile.getPoint())
				villagecount = 0
				villages = []
				# Count villages
				for spot in realm:
					if(spot.village):
						villagecount += 1
						villages.append(spot)
						#print "found village at ",spot.getPoint()
						
				#print "Found ",villagecount,"villages in this realm of ",len(realm),", ",len(villages)," of which were villages"
				#Add a village if none found, this means the city has been split, reset the realm on tiles in the new realm.
				if villagecount == 0 and len(realm) > 1:
					dest =realm[random.randrange(len(realm))]
					dest.village = Village(dest.gameMap,dest.xloc,dest.yloc)
					for spot in realm:
						spot.realm = realm
				
				
				
				while len(villages) > 1 or ( len(villages) > 0 and len(realm) < 2):
					dest = villages.pop(random.randrange(len(villages)))
					self.renders.remove(dest.village)
					dest.village = None
		if(self.selectedSet and self.selectedVillage):
			self.selectSet((self.selectedVillage.xloc,self.selectedVillage.yloc))
		
					

	def changeIncome(self,income):
		self.selectedSetIncome = income
		self.infobar.draw()
		self.store.draw()
		
	def newTurn(self):
		#End turn case
		print "End of turn %s" % (self.turn)
		
		#Remove graven images
		for row in self.tiles:
			for tile in row:
				if tile.grave:
					self.renders.remove(tile.grave)
					tile.grave = None
					#print "Removed a grave."
		
		#For each set, add balance to village, and remove upkeeps
		for row in self.tiles:
			for tile in row:
				if tile.village:
					realm = self.getTileSet((tile.xloc,tile.yloc))
					#print "Village balance was %s " %(tile.village.balance),
					tile.village.balance += len(realm)
					for space in realm:
						if space.pawn:
							tile.village.balance -= space.pawn.upkeep
					if tile.selected:
						self.selectedSetBalance = tile.village.balance
					#print "Village balance became %s" % (tile.village.balance)
					
					# Kill all of the pawns in case of negative balance
					if tile.village.balance < 0:
						for space in realm:
							if space.pawn:
								self.renders.remove(space.pawn)
								space.pawn = None
								space.grave = Grave(self,space.x,space.y)
								self.renders.append(space.grave)
								#print "Removed a pawn and added a grave."
								tile.village.balance = 0
					
				if tile.pawn:
					tile.pawn.moved = False
		self.turn += 1
		pygame.display.set_caption("HexSLayer - Turn %s" % (str(self.turn)))
		self.infobar.draw()
		self.store.draw()
		
		self.runAI()
		
	# Process AI calls for each player. 
	# TODO Make this use a model of handing an AI class a gamemap and have the AI take a single turn.
	def runAI(self):
		#0-5 means you have an AI-only game, 1-5 means player 0 is human.
		#The game currently has no protections from cheating, but do we need them if all of the AI's have moved every turn?
		for player in range(0,5):
			print "Running ai for player %s" % (player)
			
			# buy units where appropriate
			for row in self.tiles:
				for tile in row:
					if tile.player == player:
						realm = self.getTileSet(tile.getPoint())
						# TODO: This is really really innefficient (n^2 rather than n)
						for t in realm:
							if t.village and t.village.balance >= 30 and not tile.pawn and not tile.grave and not tile.village:
								
								tile.pawn = tile.buyVillager()
								self.renders.append(tile.pawn)
								print "Bought a simple pawn and placed at %sx%s for the tile at %sx%s" % (tile.x,tile.y,tile.xloc,tile.yloc)
							else:
								if t.village:
									#print "didn't buy anything, because %s is the balance" % (t.village.balance)
									nothing = None
			# move units where appropriate
			for row in self.tiles:
				for tile in row:
					
					if tile.player == player and tile.pawn and not tile.pawn.moved:
						set = self.getTileSet(tile.getPoint())
						for candidate in set:
							direction = random.randint(0,5)
							for i in range(0,6):
								dest = candidate.getAdjacentTile((direction + i) % 6)
								if not(not dest or dest.player == tile.player or dest.xloc < 0 or dest.yloc < 0 or dest.xloc >= self.width or dest.yloc >= self.height):
									break
								if i == 5:
									dest = None
								
							
						if dest:
							tile.pawn.startTile = tile
							if tile.pawn.attack(dest.xloc,dest.yloc):
								tile.pawn.moved = True
								tile.pawn.setPos(dest.xloc,dest.yloc)
						else:
							print "No candidate for attack."
							
						

						
						
							
						

			
	

		
def main():
	

	gameMap = Map()
	mouseCarrying = None
	

	if pygame.font:
		font = pygame.font.Font(None, 36)
		text = font.render("Welcome to HexSLayer",1,(10,10,10))
		textpos = text.get_rect(centerx=background.get_width()/2)
		background.blit(text,textpos)

	clock = pygame.time.Clock()
	allsprites = pygame.sprite.RenderPlain(())
	
	background.blit(pygame.image.load("endturn.png"),(400,450))
	
	
	gameMap.infobar = VillageData(gameMap,infobarLocation[0],infobarLocation[1])
	gameMap.store = PurchaseUnits(gameMap,storeLocation[0],storeLocation[1])
	gameMap.renders.append(gameMap.infobar)
	gameMap.renders.append(gameMap.store)
	gameMap.cleanUpGame()
	
	gameMap.newTurn()

	while True:
		clock.tick(60)
		#Handle Input Events
		if True:
			for event in pygame.event.get():
				if event.type == QUIT:
					return
				elif event.type == KEYDOWN and event.key == K_ESCAPE:
					return
				elif event.type == MOUSEBUTTONDOWN:
					#print "Looking for collisions"
					for row in gameMap.tiles:
						for tile in row:
							if tile.rect.collidepoint(pygame.mouse.get_pos()):
								
								if tile.checkHexCollision(pygame.mouse.get_pos()):
									
									mouseCarrying = gameMap.hexClicked(tile.xloc,tile.yloc)
									if mouseCarrying:
										mouseCarrying.startTile = tile
										#print "I have set the startTile of the carry."
									break
					x,y =pygame.mouse.get_pos()
					if(x>400 and y > 450):
						gameMap.newTurn()
					if(x<400 and x > 250 and y > 450):
						print "Spawning a new villager, and deducting from bank."
						mouseCarrying = Villager(gameMap,350,450)
						gameMap.selectedVillage.balance -= 10
						mouseCarrying.startTile = gameMap.selectedSet[0]
						gameMap.renders.append(mouseCarrying)
				elif event.type == MOUSEBUTTONUP:
					if mouseCarrying:
						print "At mouse up, Mousecarrying is %s" % (mouseCarrying)
						for row in gameMap.tiles:
							for tile in row:
								if tile.rect.collidepoint(pygame.mouse.get_pos()):
									if tile.checkHexCollision(pygame.mouse.get_pos()):
										if(mouseCarrying.attack(tile.xloc,tile.yloc)):
											#print "Attack of this square was successful, dropping player there."
											gameMap.hexDropped(mouseCarrying,tile.xloc,tile.yloc)
										else:
											mouseCarrying.setPos( mouseCarrying.startTile.xloc,mouseCarrying.startTile.yloc)
						mouseCarrying = None
				elif event.type == MOUSEMOTION:
					if mouseCarrying != None:
						mouseCarrying.x,mouseCarrying.y = pygame.mouse.get_pos()
						mouseCarrying.x -= 15
						mouseCarrying.y -= 15
		allsprites.update()

		#Draw Everything
		screen.blit(background, (0, 0))
		for pawn in gameMap.renders:
			screen.blit(pawn.image,(pawn.x,pawn.y))
		allsprites.draw(screen)
		pygame.display.flip()
		gameMap.newTurn()




main()
