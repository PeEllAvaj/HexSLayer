#
# HexSLayer
# copyright (C) Stephen Fluin 2011
#
import pygame, random
from pygame.locals import *
from hexmath import *
from hexconfig import *

class VillageData(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		self.gameMap = gameMap
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = x,y

		self.draw()
	def draw(self):
		self.image = pygame.Surface((500,30))
		self.image.fill(bgColor)
		if(self.gameMap.selectedSetIncome > 0):
			msg = "Village Income:+"+str(self.gameMap.selectedSetIncome)+",-"+str(self.gameMap.selectedSetUpkeep)+"="+str(self.gameMap.selectedSetIncome-self.gameMap.selectedSetUpkeep)
			if(self.gameMap.selectedVillage.balance > 0):
				msg += "  Balance:%s" % (self.gameMap.selectedVillage.balance)
				
			font = pygame.font.Font("freesansbold.ttf", 22)
			text = font.render(msg,1,fontColor)
			self.image.blit(text,(0,0))
			
class PurchaseUnits(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.gameMap = gameMap
		self.x,self.y = x,y
		self.income = 0
		self.draw()
	def draw(self):
		self.image = pygame.Surface((60,30))
		self.image.fill(bgColor)
		if self.gameMap.selectedVillage and self.gameMap.selectedVillage.player == 0:
			if self.gameMap.selectedVillage.balance >= 10:
				# TODO: Make sure this doesn't load on each call of draw
				self.image.blit(pygame.image.load("villager.png"),(0,0))
			if self.gameMap.selectedVillage.balance >= 20:
				self.image.blit(pygame.image.load("castle.png"),(30,0))
			
		
		#if(self.gameMap.balance() > 8):
				# TODO: Castles
		
class GameOver(pygame.sprite.Sprite):
	def __init__(self,gameMap,x,y,winner):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = x,y
		self.gameMap = gameMap
		self.winner = winner
		print "Winner of game is %s." % (self.winner)
		self.draw()
	def draw(self):
		self.image = pygame.Surface((560,100))
		self.image.fill(bgColor)
		font = pygame.font.Font("freesansbold.ttf",28)
		text = font.render("Player %s (%s) won! Congratulations!" % (self.winner,self.gameMap.players[self.winner].getName()),True,fontColor)
		self.image.blit(text,(0,0))

class NewGame(pygame.sprite.Sprite):
	def __init__(self,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.x,self.y = x,y
		self.draw()
	def draw(self):
		self.image = pygame.Surface((300,40))
		self.image.fill(bgColor)
		font = pygame.font.Font("freesansbold.ttf",20)
		text = font.render("Start Another Game",True,fontColor)
		self.rect = pygame.draw.rect(self.image,(0,0,0),(0,0,300,40),1)
		self.image.blit(text,(30,5))
		
class ScoreCard(pygame.sprite.Sprite):
	def __init__(self,gameMap,location):
		pygame.sprite.Sprite.__init__(self)
		(self.x,self.y) = location
		
		self.gameMap = gameMap
		self.draw()
	def draw(self):
		self.image = pygame.Surface((200,400))
		self.image.fill(bgColor)
		size = 18
		font = pygame.font.Font("freesansbold.ttf",size)
		tileCounts = self.gameMap.countTiles()
		for i in range(0,6):
			
			text = font.render("%s - %s" % (self.gameMap.players[i].getName(),tileCounts[i]),True,fontColor)
			self.image.blit(text,(30,10+(size+10)*i))
			pygame.draw.rect(self.image,pygame.Color(playerColors[i]),pygame.Rect(0,(size+10)*i+10,15,15))
		self.image.blit(font.render("Turn %s" % (self.gameMap.turn),True,fontColor),(30,(size+10)*6+10))
		
		