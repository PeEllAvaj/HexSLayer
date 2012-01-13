#
# HexSLayer
# copyright (C) Stephen Fluin 2010
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
		self.x,self.y = convertGridPawnPosition(self.gameMap,x,y)
		self.startTile = None
		self.moved = False
		self.level = level
		self.spin = 0
		self.player = -1
		self.justPurchased = False
		self.indicator = None
		
	def getHasMoved(self):
		return self.moved
		
		
	def setPos(self,x,y):
		self.x,self.y = convertGridPawnPosition(self.gameMap,x,y)
		if not self.justPurchased:
			self.startTile.pawn = None
		self.gameMap.getTile((x,y)).pawn = self
		self.gameMap.getTile((x,y)).draw()
		
		# Is this good enough to set the player for all pawns?
		if(self.gameMap.getTile((x,y))):
			self.player = self.gameMap.getTile((x,y)).player
		
	# Returns true if attack was successful (movement taken, or false if nothing happened)
	# Should handle moving of sprites, reallocation of space, destruction of victims.
	def attack(self,x,y):
		
		#print "Testing if we can attack this tile"
		#print "Returning the pawn to " , self.startTile.xloc,"X",self.startTile.yloc
		dest = self.gameMap.getTile((x,y))
		#print "Attacking tile at %sx%s, which belongs to player %s" % (x,y,dest.player)
		tiles = self.gameMap.getTileSet((self.startTile.xloc,self.startTile.yloc))
		#Why am I attacking a tileset? This means you can take 2 squares at once
		# IMPORTANT TODO
		for tile in tiles:
			if(tile.isAdjacent((x,y))):
				#The attacked tile is adjacent to a tile in our starting set
				
				
				#Newly organized version of attack code
				# Step 1. Check if just moving within my realm and allow
				if dest.player != self.startTile.player:
					self.moved = True
				else:
					if dest.village:
						return False
					if dest.pawn and dest.pawn != self: 
						if self.level == 1 and dest.pawn.level <= 4:
							
							while self.level <= dest.pawn.level and self != dest.pawn:
								#print "Upgrading because self level is %s and dest pawn level is %s." % (self.level, dest.pawn.level)
								if not isinstance(dest.pawn,Castle) and self.upgrade():
									pass
								else:
									return False
							if dest.pawn not in self.gameMap.renders:
								print "Found a weird fringe case where the unit we are upgrading isn't being rendered!!!!"
							self.gameMap.renders.remove(dest.pawn)
							
							return True
						return False
						
						
					return True
					
				
				#Step 2 & # Block movement by protection
				if self.level <= dest.getProtection():
					
					self.moved = False
					return False

				#Weird edge case experienced on 20100109
				if dest.pawn and dest.pawn not in self.gameMap.renders:
					print "WEIRD EDGE CASE WITH %s and %s." % (dest.pawn, self.gamemap.renders)
					
					
				# Step 4. Kill whatever is left with your movement.
				#@TODO this should only be dest.pawn
				if dest.pawn:
					dest.pawn.kill(dest)
				if dest.village:
					dest.village.kill(dest)
				
				

			
				dest.setPlayer(self.startTile.player)
				self.gameMap.cleanUpGame()
				
				return True
			else:
				self.gameMap.message("Destination must be adjacent to current region.")
			
		return False
		
	def upgrade(self):
		#print "Upgrading this pawn from level ",self.level
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
		return True
		
	# Kill removes pawn from renders, deletes it from the listed tile, adds a gravesite
	def kill(self,tile):
		if(self in self.gameMap.renders):
			self.gameMap.renders.remove(self)
			tile.pawn = None
			# why do we add graves in case of hunger death? :(
			
			#print "Removed a pawn and added a grave."
	
	def starve(self,tile):
		tile.grave = Grave(self.gameMap,tile.xloc,tile.yloc)
		self.gameMap.renders.insert(0,tile.grave)
		self.kill(tile)
			
# Takes in tile coordinates, not x/y coordinates
class Villager(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,1)
		self.image = pygame.image.load("villager.png")
		self.upkeep = 2
		
class Castle(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,2)
		self.image = pygame.image.load("castle.png")
		self.upkeep = 0
	def getHasMoved(self):
		return True
	def kill(self,tile):
		print "About to kill a legendary castle, my protection is:%s" % (tile.getProtection())
		Pawn.kill(self,tile)
		
class Village(Pawn):
	def __init__(self,gameMap,xloc,yloc):
		Pawn.__init__(self,gameMap,xloc,yloc,1)
		self.upkeep = 0
		self.balance = 5
		self.image = pygame.image.load("village.png")
		self.player = gameMap.getTile((xloc,yloc)).player
		self.xloc = xloc
		self.yloc = yloc
	def getHasMoved(self):
		return True
	def kill(self,tile):
		print "Killing a village"
		tile.village = None
		Pawn.kill(self,tile)
		


class Grave(pygame.sprite.Sprite):
	def __init__(self,gameMap,xloc,yloc):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("dead.png")
		(self.x,self.y) = convertGridPawnPosition(gameMap,xloc,yloc)
		#print "Grave is created at %sx%s." % (x,y)
		
class AvailableMove(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image =pygame.image.load("sparks.png")
		self.image = pygame.transform.smoothscale(self.image,(tilesize,tilesize))
		
		self.original = self.image
		self.rect = self.image.get_rect()
		screen = pygame.display.get_surface()
		self.area = screen.get_rect()
		self.rotation = 0
		self.rect.topleft = x-4,y-4
		
	def spin(self):
		center = self.rect.center
		self.rotation += 4
				
		self.image = pygame.transform.rotate(self.original,self.rotation)
		self.rect = self.image.get_rect(center=center)
		
	def render(self, screen):
		screen.blit(self.image,self.rect)
		
		
		
