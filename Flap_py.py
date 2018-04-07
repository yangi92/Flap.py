from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *
from ScreenObject import *
import pickle



(_WIDTH,_HEIGHT)=(288,512)
FPS=30
_BIRD =(
	   'sprites/redbird-upflap.png',
	   'sprites/redbird-midflap.png',
	   'sprites/redbird-downflap.png'
	   )
_BACKGROUND ='sprites/background-day.png'
_PIPE='sprites/pipe-green.png'
_GAMEOVER='sprites/gameover.png'
_BASE = 'sprites/base.png'
_NUMBER_LIST =(
			   'sprites/0.png',
			   'sprites/1.png',
			   'sprites/2.png',
			   'sprites/3.png',
			   'sprites/4.png',
			   'sprites/5.png',
			   'sprites/6.png',
			   'sprites/7.png',
			   'sprites/8.png',
			   'sprites/9.png'
			  )
_MENU ='sprites/menu.png'
_FONT ='fonts/FlappyBird.ttf' 
_ICON ='sprites/icon.png'
_HIGHSCORE_PATH='output/score.p'

_MENU_STATE=0
_INITIAL_STATE=1
_GAME_STATE=2
_GAMEOVER_STATE=3

try:
	xrange
except NameError:
	xrange = range


class Flap_py():

	def __init__(self):
		"""
		Initialisation

		Creates
		-------
		pygame
		frame  
		icon

		Sets
		----
		score : int
			sets initial score to 0
		state : int
			sets initial state to 0
		"""
		pygame.init()
		self.FPS_clock = pygame.time.Clock()
		self.frame=pygame.display.set_mode((_WIDTH, _HEIGHT))
		pygame.display.set_caption('Flap.py Bird')
		icon = pygame.image.load(_ICON).convert_alpha()
		pygame.display.set_icon(icon)
		self.state= _MENU_STATE
		self.score=0
		self.load_objects(restore=False)
		self.hitmasks=self.create_hitmask()
		self.main()


	def main(self):
		"""Main menu 
		   
		   The main class loops among all game states
		   Every state has :
			-pygame.event  : checks if users quits game or makes an action
			-update_screen : updates the elements in the parameter dict
		"""
		
		while True:

			#CASE = MENU
			if self.state ==_MENU_STATE:
				
				mpos = pygame.mouse.get_pos()
				for event in pygame.event.get():
					if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
						pygame.quit()
						sys.exit()

					#just an unecessary font highlight feature
					if self.play_button.get_rect().collidepoint(mpos):
						selected=True
						self.play_button.highlight_text()
						if event.type == pygame.MOUSEBUTTONDOWN:
							self.state=_INITIAL_STATE
							self.game_choice = _INITIAL_STATE

					else:
						self.play_button.unhighlight_text()

				self.update_screen({'objects':[ self.menu,
										   self.play_button,
										   self.learning_button,
										   self.highscore]})
			
			#CASE = INITIAL STATE
			elif self.state ==_INITIAL_STATE:
				for event in pygame.event.get():
					if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
						pygame.quit()
						sys.exit()
					elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
						self.state=_GAME_STATE

				self.update_screen({'objects':[self.background,
										  self.bird,
										  self.base,
										  self.pipe],
								'score':0})

			#CASE = GAME STATE
			elif self.state == _GAME_STATE:
				for event in pygame.event.get():
					if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
						pygame.quit()
						sys.exit()
					if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
						self.bird.flap()

				# check if bird has crashed
				crashTest = self.checkCrash()
				if crashTest:
					self.state=_GAMEOVER_STATE

				#score update when pipes are passed
				playerMidPos = self.bird.get_x() + self.bird.get_surface()[0].get_width() / 2
				for p in self.pipe.get_pipe_list()[0]:
					pipeMidPos = p['x'] + self.pipe.get_surface()[0].get_width() / 2
					if pipeMidPos <= playerMidPos < pipeMidPos + 4:
						self.score += 1
			
				#Updates new position of moveable objects
				[obj.update_movement() for obj in self.moveable_objects]

				self.update_screen({'objects':[self.background,
										  self.bird,
										  self.base,
										  self.pipe],
								'score':self.score})

			#CASE = GAMEOVER
			elif self.state == _GAMEOVER_STATE:
				for event in pygame.event.get():
					if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
						pygame.quit()
						sys.exit()
					if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
							#restore game score,objects and state
							self.score=0 
							self.load_objects(restore=True) 
							self.state=self.game_choice

				#updates highscore if necessary
				if self.score > self.highscore.get_score():
					self.highscore.update_score(self.score) 

				self.update_screen({'objects':[self.gameovermsg]})
				
		

	def update_screen(self,objects_dict):
		
		for item in objects_dict['objects']:
			item.update(self.frame)

		if 'score' in objects_dict:
			score = objects_dict['score']
			#displays score in center of screen
			scoreDigits = [int(x) for x in list(str(score))]
			totalWidth = 0 # total width of all numbers to be printed
			for digit in scoreDigits:
				totalWidth += self.numbers.get_surface()[digit].get_width()

			Xoffset = (_WIDTH - totalWidth) / 2
			for digit in scoreDigits:
				self.frame.blit(self.numbers.get_surface()[digit], 
						   (Xoffset, _HEIGHT * 0.1)
						   )
				Xoffset += self.numbers.get_surface()[digit].get_width()

		pygame.display.update()
		self.FPS_clock.tick(FPS)


	def load_objects(self, restore):
		""" 
		Creates all the objects
		

		Parameters
		----------
		restore : boolean
			if true restores all moveable objects
		"""
		
		if(~restore):
			self.numbers = Number(path=_NUMBER_LIST)
			self.menu = Menu(path=_MENU)
			self.gameovermsg = GameOverMessage(path=_GAMEOVER)

			self.play_button = Button(path=_FONT,
								  text="Single Player",
								  size=50,
								  center_x=self.frame.get_rect().centerx,
								  center_y=_HEIGHT/2.4
								  )

			self.learning_button = Button(path=_FONT,
								  text="Learning",
								  size=50,
								  center_x=self.frame.get_rect().centerx,
								  center_y=_HEIGHT/1.8
								  )

			self.highscore = Highscore(path =_FONT,
								  size=50,
								  file_path =_HIGHSCORE_PATH,
								  center_x=self.frame.get_rect().centerx,
								  center_y=_HEIGHT/1.1)

		self.background= Background(path=_BACKGROUND)
		self.bird = Bird(path=_BIRD)
		self.base = Base(path=_BASE,
					background_width=self.background.get_surface().get_width()
					)
		self.pipe = Pipe(path=_PIPE)
		
		#object list of all moveable objects
		self.moveable_objects = [self.background,
								 self.bird,
								 self.base,
								 self.pipe]


	def create_hitmask(self):
		"""
		Creates hitmasks for pipe and bird


		Returns
		-------
		hitmasks : dict
			Contains two keys (bird,pipe) each with hitmaps correposponding
			to their sprites

		"""
		hitmasks = {}
		hitmasks['pipe'] = (
				self.pipe.getHitmask(self.pipe.get_surface()[0]),
				self.pipe.getHitmask(self.pipe.get_surface()[1])
			)
		hitmasks['bird'] = (
				self.bird.getHitmask(self.bird.get_surface()[0]),
				self.bird.getHitmask(self.bird.get_surface()[1]),
				self.bird.getHitmask(self.bird.get_surface()[2])
			)
		return hitmasks


	def checkCrash(self):
		"""
		Check if the bird crashes into the ground or pipes

		Returns
		-------
		val : boolean
			true if bird has touched pipe/base
			false otherwise
			
		"""

		#Get bird's height,width,x and y positions
		bird_w = self.bird.get_surface()[0].get_width()
		bird_h = self.bird.get_surface()[0].get_height()
		bird_x = self.bird.get_x()
		bird_y = self.bird.get_y()

		#Base y position
		base_y = _HEIGHT * 0.79

		# if player crashes into ground
		if bird_y + bird_h >= base_y - 1:
			return True
		else:

			playerRect = pygame.Rect(bird_x, bird_y,
						  bird_w, bird_h)
			pipeW = self.pipe.get_surface()[0].get_width() 
			pipeH = self.pipe.get_surface()[0].get_height() -2 
			upperPipes ,lowerPipes = self.pipe.get_pipe_list()

			for uPipe, lPipe in zip(upperPipes, lowerPipes):
				# upper and lower pipe rects
				uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
				lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

				# player and upper/lower pipe hitmasks
				pHitMask = self.hitmasks['bird'][0]
				uHitmask = self.hitmasks['pipe'][0]
				lHitmask = self.hitmasks['pipe'][1]

				# if bird collided with upipe or lpipe
				uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
				lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

				if uCollide or lCollide:
					return True

		return False



	def pixelCollision(self,rect1, rect2, hitmask1, hitmask2):
		rect = rect1.clip(rect2)

		if rect.width == 0 or rect.height == 0:
			return False

		x1, y1 = rect.x - rect1.x, rect.y - rect1.y
		x2, y2 = rect.x - rect2.x, rect.y - rect2.y

		for x in xrange(rect.width):
			for y in xrange(rect.height):
				if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
					return True
		return False

Flap_py()