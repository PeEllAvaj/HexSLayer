#
# HexSLayer
# copyright (C) Stephen Fluin 2009
#

# Pawns Classfiles
# provides objects representing different pawns that can be placed on the game board.
#

import pygame, random
from pygame.locals import *
from hexmath import *

class Pawn(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y,level):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.startTile = None
		self.moved = False
		self.level = level
		
	def setPos(self,x,y):
		self.x,self.y = convertGridPosition(self.gameMap,x,y)
		self.startTile.pawn = None
		self.gameMap.getTile((x,y)).pawn = self
		self.gameMap.getTile((x,y)).draw()
		
	# Returns true if attack was successful (movement taken, or false if nothing happened)
	# Should handle moving of sprites, reallocation of space, destruction of victims.
	def attack(self,x,y):
		
		#print "Testing if we can attack this tile"
		#print "Returning the pawn to " , self.startTile.xloc,"X",self.startTile.yloc
		dest = self.gameMap.getTile((x,y))
		#print "Attacking tile at %sx%s, which belongs to player %s" % (x,y,dest.player)
		tiles = self.gameMap.getTileSet((self.startTile.xloc,self.startTile.yloc))
		for tile in tiles:
			if(tile.isAdjacent((x,y))):
				#The attacked tile is adjacent to a tile in our starting set
				
				
				
				#Newly organized version of attack code
				# Step 1. Check if just moving within my realm and allow
				if dest.player != self.startTile.player:
					self.moved = True
				else:
					if dest.pawn and dest.pawn != self: 
						if self.level == 1 and dest.pawn.level <= 4:
							
							while self.level <= dest.pawn.level and self != dest.pawn:
								print "Upgrading because self level is %s and dest pawn level is %s." % (self.level, dest.pawn.level)
								self.upgrade()
							if dest.pawn not in self.gameMap.renders:
								print "Found a weird fringe case where the unit we are upgrading isn't being rendered!!!!"
							self.gameMap.renders.remove(dest.pawn)
							
							return True
						return False
						
						
					return True
					
				
				# Step 2. Block movement by more powerful units
				fail = False
				if dest.pawn and dest.pawn.level >= self.level:
					fail = True
				for i in range(0,6):
					if dest.getAdjacentTile(i) and dest.getAdjacentTile(i).player == dest.player and  dest.getAdjacentTile(i).pawn and dest.getAdjacentTile(i).pawn.level >= self.level:
						fail = True
				
				# Step 3. Block movement by villages
				if self.level < 2:
					if dest.village:
						fail = True
					for i in range(0,6):
						if dest.getAdjacentTile(i) and dest.getAdjacentTile(i).player == dest.player and  dest.getAdjacentTile(i).village:
							fail = True
						
				if fail:
					self.moved = False
					return False
					
				# Step 4. Kill whatever is left with your movement.
				if dest.pawn:
					self.gameMap.renders.remove(dest.pawn)
					dest.pawn = None
				if dest.village:
					self.gameMap.renders.remove(dest.village)
					dest.village = None
				
				

			
				dest.setPlayer(self.startTile.player)
				self.gameMap.cleanUpGame()
				
				return True
				
		return False
		
	def upgrade(self):
		print "Upgrading this pawn from level ",self.level
		self.level += 1
		if self.level == 2:
			self.image = pygame.image.load("wizard.png")
			self.upkeep = 6
		elif self.level == 3:
			self.image = pygame.image.load("swordsman.png")
			self.upkeep = 18
		elif self.level == 4:
			self.image = pygame.image.load("knight.png")
			self.upkeep = 50
	def kill(tile):
		
		self.gameMap.renders.remove(self)
		tile.pawn = None
		tile.grave = Grave(self.gameMap,tile.x,tile.y)
		self.gameMap.renders.append(tile.grave)
		#print "Removed a pawn and added a grave."
			
# Takes in tile coordinates, not x/y coordinates
class Villager(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,1)
		self.image = pygame.image.load("villager.png")
		self.upkeep = 2
		
	

class Grave(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("dead.png")
		self.upkeep = 2
		self.x = x
		self.y = y
		print "Grave is created at %sx%s." % (x,y)
