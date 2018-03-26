from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *
import pickle



class ScreenObject:


	def __init__(self,path,pygame):
		self.path=path
		self.create_surface(pygame)
		self.pos_x
		self.pos_y

	def get_path(self):
		return self.path

	def create_surface(self,pygame):
		self.surface=pygame.image.load(self.path).convert_alpha()

	def create_msurface(self,pygame):
		self.surface=[pygame.image.load(path).convert_alpha() for path in self.path]

	def get_surface(self):
		return self.surface

	def update(self,Frame):
		Frame.blit(self.surface, (pos_x,pos_y))

	def update_movement(self,pygame):
		pass

	def getHitmask(self,image):
		mask = []
		for x in xrange(image.get_width()):
			mask.append([])
			for y in xrange(image.get_height()):
				mask[x].append(bool(image.get_at((x,y))[3]))
		return mask

class Pipe(ScreenObject):

	def __init__(self,path,pygame):
		self.path=path
		self.create_surface(pygame)
		self.pipeVelX = -4
		self._BASE_Y = 512*0.79
		self._PIPEGAPSIZE = 100
		self._WIDTH =288
		self.create_pipes()
	

	def create_pipes(self):
		newPipe1= self.random_pipe()
		newPipe2= self.random_pipe()
		self.upperPipes = [{'x': self._WIDTH + 200,
							'y': newPipe1[0]['y']},
						   {'x': self._WIDTH + 200 + (self._WIDTH / 2),
						    'y': newPipe2[0]['y']}]
		self.lowerPipes = [{'x': self._WIDTH + 200,
		                    'y': newPipe1[1]['y']},
		                   {'x': self._WIDTH + 200 + (self._WIDTH / 2),
		                    'y': newPipe2[1]['y']}]
    
	def get_pipe_list(self):
		return self.upperPipes,self.lowerPipes
    
	def get_x(self,pipe):
		return pipe['x']
    	
	def update_movement(self,pygame):
		for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
			uPipe['x'] += self.pipeVelX
			lPipe['x'] += self.pipeVelX
		
		if 0 < self.upperPipes[0]['x'] < 5:
			newPipe = self.random_pipe()
			self.upperPipes.append(newPipe[0])
			self.lowerPipes.append(newPipe[1])
		if self.upperPipes[0]['x'] < -self.get_surface()[0].get_width():
			self.upperPipes.pop(0)
			self.lowerPipes.pop(0)

	def update(self,Frame):
		for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
			Frame.blit(self.surface[0], (uPipe['x'], uPipe['y']))
			Frame.blit(self.surface[1], (lPipe['x'], lPipe['y']))

	def create_surface(self,pygame):
		self.surface=(pygame.transform.rotate(pygame.image.load(self.path).convert_alpha(),
											  180
											  ),
             		 pygame.image.load(self.path).convert_alpha()
             		 )


	def random_pipe(self):
		gap_Y = random.randrange(0,
								 int(self._BASE_Y * 0.6 - self._PIPEGAPSIZE)
								 )
		gap_Y += int(self._BASE_Y * 0.2)
		pipeHeight = self.get_surface()[0].get_height()
		pipe_X = 288 + 10
		return [
			{'x': pipe_X, 'y': gap_Y - pipeHeight},  # upper pipe
        	{'x': pipe_X, 'y': gap_Y + self._PIPEGAPSIZE}, # lower pipe
        	   ]


class Bird(ScreenObject):
    def __init__(self,path,pygame):
		self.path=path
		self.create_msurface(pygame)
		self.bird_x=int(288 * 0.2)
		self.bird_y= int((512 - self.get_surface()[0].get_height()) / 2)
		self.bird_VelY    =  -10   # bird_'s velocity along Y, default same as bird_Flapped
		self.bird_MaxVelY =  15   # max vel along Y, max descend speed
		self.bird_MinVelY =  -15   # min vel along Y, max ascend speed
		self.bird_AccY    =   1   # bird_s downward accleration
		self.bird_Rot     =  45   # bird_'s rotation
		self.bird_VelRot  =   3   # angular speed
		self.bird_RotThr  =  20   # rotation threshold
		self.bird_FlapAcc =  -9  # bird_s speed on flapping
		self.bird_Flapped = False # True when bird_ flaps
		self._BASE_Y = 512*0.79
		self.rotated_surface=self.get_surface()[0]		

    def update(self,Frame):
    	Frame.blit(self.rotated_surface,
    		      (self.bird_x,self.bird_y))

    def get_x(self):
  		return self.bird_x

    def get_y(self):
  		return self.bird_y

    def get_velY(self):
  		return self.bird_VelY

    def get_rot(self):
  		return self.bird_Rot

    def flap(self):
		if self.bird_y > -2 * self.get_surface()[0].get_height():
                    self.bird_VelY = self.bird_FlapAcc
                    self.bird_Flapped = True


    def update_movement(self,pygame):
		 # rotate the bird_
        if self.bird_Rot > -90:
            self.bird_Rot -= self.bird_VelRot

        # bird_'s movement
        if self.bird_VelY < self.bird_MaxVelY and not self.bird_Flapped:
            self.bird_VelY += self.bird_AccY
        if self.bird_Flapped:
            self.bird_Flapped = False
            # more rotation to cover the threshold (calculated in visible rotation)
            self.bird_Rot = 45

        self.bird_Height = self.get_surface()[0].get_height()
        self.bird_y += min(self.bird_VelY,
        				   self._BASE_Y - self.bird_y - self.bird_Height)

        self.visibleRot = self.bird_RotThr
        if self.bird_Rot <= self.bird_RotThr:
        	self.visibleRot = self.bird_Rot
        self.rotated_surface=(pygame.transform.rotate(self.get_surface()[0], self.visibleRot))
 
class Background(ScreenObject):
	def __init__(self,path,pygame):
		self.path=path
		self.create_surface(pygame)
		self.bg_x=0
		self.bg_y=0


	def update(self,Frame):
		Frame.blit(self.get_surface(), (self.bg_x,self.bg_y))

class Base(ScreenObject):
	def __init__(self,path,pygame,background_width):
		self.path=path
		self.create_surface(pygame)
		self.base_x =0
		self.base_y =512*0.79

		self.base_shift=self.get_surface().get_width() - background_width


	def get_x(self):
		return self.base_x

	def update(self,Frame):
		Frame.blit(self.get_surface(), (self.base_x,self.base_y))


	def update_movement(self,pygame):
		self.base_x = -((-self.base_x + 100) % self.base_shift)

class Number(ScreenObject):
	def __init__(self,path,pygame):
		self.path=path
		self.create_msurface(pygame)


class GameOverMessage(ScreenObject):
	def __init__(self,path,pygame):
		self.path=path
		self.create_surface(pygame)

	def update(self,Frame):
		Frame.blit(self.get_surface(), (50,100))

class Menu(ScreenObject):
	def __init__(self,path,pygame):
		self.path=path
		self.create_surface(pygame)


	def update(self,Frame):
		Frame.blit(self.get_surface(), (0,0))

class Button(ScreenObject):

	def __init__(self,pygame,path,text,size,center_x,center_y):
		self.path=path
		self.text=text
		self.size=size
		self.center_x=center_x
		self.center_y=center_y
		self.create_surface(pygame)

	def get_rect(self):
		return self.spRect

	def create_surface(self,pygame):
		self.font = pygame.font.Font(self.path,self.size)
		self.surface = self.font.render(self.text, True, (255,255,255))
		self.spRect = self.surface.get_rect()
		self.spRect.centerx = self.center_x
		self.spRect.centery = self.center_y
	
	def update(self,Frame):
		Frame.blit(self.get_surface(), self.spRect)

	def highlight_text(self):
		self.surface = self.font.render(self.text, True, (233,252,217))

	def unhighlight_text(self):
		self.surface = self.font.render(self.text, True, (255,255,255))


class Highscore(ScreenObject):
	def __init__(self,pygame,path,size,file_path,center_x,center_y):
		self.file_path=file_path
		self.size=size
		self.path=path
		self.text="Highscore: "
		self.score=self.retrieve_score().get('score')
		
		self.center_x=center_x
		self.center_y=center_y
		self.create_surface(pygame)

	def retrieve_score(self):
		return  pickle.load( open( self.file_path, "rb" ) )

	def update_score(self,score):
		self.score = score
		pickle.dump( {'score':self.score}, open( self.file_path, "wb" ) )

	def get_score(self):
		return self.score

	def create_surface(self,pygame):
		self.font = pygame.font.Font(self.path,self.size)
		print(self.score)
		self.surface = self.font.render(self.text+str(self.score), True, (255,255,255))
		self.spRect = self.surface.get_rect()
		self.spRect.centerx = self.center_x
		self.spRect.centery = self.center_y
	def update(self,Frame):
		Frame.blit(self.get_surface(), self.spRect)

 





	
