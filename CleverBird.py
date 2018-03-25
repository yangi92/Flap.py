from itertools import cycle
import random
import sys
import pygame
from pygame.locals import *
from ScreenObject import *



(_WIDTH,_HEIGHT)=(288,512)
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
base_y        = _HEIGHT * 0.79
FPS =30
_BIRD =(
	   'sprites/redbird-upflap.png',
	   'sprites/redbird-midflap.png',
	   'sprites/redbird-downflap.png'
	   )
_BACKGROUND ='sprites/background-day.png'
_PIPE='sprites/pipe-green.png'
_GAMEOVER='sprites/gameover.png'
_message= 'sprites/message.png'
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
_FONT ='fonts/FlappyBirdy.ttf' 

try:
    xrange
except NameError:
    xrange = range

def main():

	global FRAME, FPSCLOCK,OBJECTS
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	FRAME=pygame.display.set_mode((_WIDTH, _HEIGHT))
	pygame.display.set_caption('Flappy Bird')
	OBJECTS = load_objects()
	HITMASKS = create_hitmask()

	while True:

		menu_state()
		initial_state()
		gameStats=game_state()
		gameover_state(gameStats)
		load_objects()


def menu_state():
    FRAME.fill((0,0,0))
    while True:
    	mpos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            	pygame.quit()
            	sys.exit()
            if singlePlayer.get_rect().collidepoint(mpos):
            	selected=True
            	singlePlayer.highlight_text()
            	if event.type == pygame.MOUSEBUTTONDOWN:
            		return

            else:
            	singlePlayer.unhighlight_text()

        update_screen(FRAME=FRAME,
        			  score=0,
        			  menu_state=True,
        			  gameOver_state=False)
        


        FPSCLOCK.tick(FPS)





def initial_state():
    FRAME.fill((0,0,0))
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            	pygame.quit()
            	sys.exit()
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        update_screen(FRAME=FRAME,
        			  score=0,
        			  menu_state=False,
        			  gameOver_state=False)
        FPSCLOCK.tick(FPS)

def game_state():
    FRAME.fill((0,0,0))
    score = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                bird.flap()

        # # check for crash here
        crashTest = checkCrash()
        if crashTest[0]:
            return {
                'score': score,
            }

        playerMidPos = bird.get_x() + bird.get_surface()[0].get_width() / 2
        for p in pipe.get_pipe_list()[0]:
            pipeMidPos = p['x'] + pipe.get_surface()[0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
        
        update_movements(pygame)
        update_screen(FRAME=FRAME,
        			  score=score,
        			  menu_state=False,
        			  gameOver_state=False)

        FPSCLOCK.tick(FPS)


def gameover_state(game_stats):
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    return

        update_screen(FRAME=FRAME,
        			  score=game_stats['score'],
        			  menu_state=False,
        			  gameOver_state=True)
        FPSCLOCK.tick(FPS)
        pygame.display.update()

def load_objects():
	global menu,numbers,pipe,bird,base,background,objects,gameovermsg,singlePlayer,learning
	objects = []
	background= Background(path=_BACKGROUND,
		                   pygame=pygame
		                   )
	bird = Bird(path=_BIRD,
				pygame=pygame
				)
	base = Base(path=_BASE,
		        pygame=pygame,
		        background_width=background.get_surface().get_width()
		        )
	pipe = Pipe(path=_PIPE,
				pygame=pygame
				)
	numbers = Number(path=_NUMBER_LIST,
					 pygame=pygame
					 )
	menu = Menu(path=_MENU,
				pygame=pygame
				)
	gameovermsg = GameOverMessage(path=_GAMEOVER,
								  pygame=pygame)

	singlePlayer = Button(path=_FONT,
						  pygame=pygame,
						  text="Single Player",
						  size=50,
						  center_x=FRAME.get_rect().centerx,
						  center_y=_HEIGHT/2.4
						  )

	learning = Button(path=_FONT,
						  pygame=pygame,
						  text="Learning",
						  size=50,
						  center_x=FRAME.get_rect().centerx,
						  center_y=_HEIGHT/1.8
						  )
	
	objects.append([background,bird,base,pipe])


def update_movements(pygame):
	[obj.update_movement(pygame) for obj in objects[0]]

def update_screen(FRAME,score,menu_state,gameOver_state):
	if(menu_state):
		menu.update(FRAME)
		singlePlayer.update(FRAME)
		learning.update(FRAME)
	else:
		[obj.update(FRAME) for obj in objects[0]]
		"""displays score in center of screen"""
		scoreDigits = [int(x) for x in list(str(score))]
		totalWidth = 0 # total width of all numbers to be printed
		for digit in scoreDigits:
			totalWidth += numbers.get_surface()[digit].get_width()

		Xoffset = (_WIDTH - totalWidth) / 2
		for digit in scoreDigits:
			FRAME.blit(numbers.get_surface()[digit], 
					   (Xoffset, _HEIGHT * 0.1)
					   )
			Xoffset += numbers.get_surface()[digit].get_width()

	if(gameOver_state):
		gameovermsg.update(FRAME)

	pygame.display.update()


def create_hitmask():
	global HITMASKS
	HITMASKS = {}
	HITMASKS['pipe'] = (
            pipe.getHitmask(pipe.get_surface()[0]),
            pipe.getHitmask(pipe.get_surface()[1])
        )
	HITMASKS['bird'] = (
            bird.getHitmask(bird.get_surface()[0]),
            bird.getHitmask(bird.get_surface()[1]),
            bird.getHitmask(bird.get_surface()[2])
        )
	return HITMASKS


def checkCrash():
    """returns True if player collders with base or pipes."""
    bird_w = bird.get_surface()[0].get_width()
    bird_h = bird.get_surface()[0].get_height()
    bird_x = bird.get_x()
    bird_y = bird.get_y()

    # if player crashes into ground
    if bird_y + bird_h >= base_y - 1:
        return [True, True]
    else:

        playerRect = pygame.Rect(bird_x, bird_y,
                      bird_w, bird_h)
        pipeW = pipe.get_surface()[0].get_width()
        pipeH = pipe.get_surface()[0].get_height()
        upperPipes ,lowerPipes = pipe.get_pipe_list()

        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            # upper and lower pipe rects
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

            # player and upper/lower pipe hitmasks
            pHitMask = HITMASKS['bird'][0]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]

            # if bird collided with upipe or lpipe
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

            if uCollide or lCollide:
                return [True, False]

    return [False, False]



def pixelCollision(rect1, rect2, hitmask1, hitmask2):
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

main()