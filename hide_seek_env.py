import gym
from gym import spaces
import numpy as np
import cv2
import random
import time
from collections import deque
from turtle import shape
import pygame
import pygame.display as display
import math
import os



RENDER_GAME = True

if RENDER_GAME:
    pygame.init()
else:
    os.environ["SDL_VIDEODRIVER"] = "dummy"

running = True
display.set_caption("HIDE AND SEEK")


# might be the only way to turn off diplay of pygame
# need to control + c in terminal to stop game
# os.environ["SDL_VIDEODRIVER"] = "dummy"


# Global REWARDS -----------------------------------------------------------------------------
NEAR_WALL = -1
# hider's rewards
GOT_THE_FLAG = 50
HIDER_WINS_REWARD = 100
HIDER_LOSES_PENALTY = -200
# seeker's rewards
SEEKER_WINS_REWARD = 150
SEEKER_LOSES_PENALTY = -200

NOT_MOVING = -5
MOVING = 0

# Global CONSTANTS -----------------------------------------------------------------------------
# everything depends on the window width

# g=Game specifications
WINDOW_WIDTH = 800
WINDOW_HEIGHT = WINDOW_WIDTH # make sure the window is a square!
MAP_SIZE = int(WINDOW_WIDTH / (WINDOW_WIDTH/10)) # number of rows and cols
TILE_SIZE = int(WINDOW_WIDTH/MAP_SIZE)
NUM_TILES = MAP_SIZE ** 2

NUM_EPISODES = 10

PLAYER_DIAMETER = 10
HIDER_START_ANGLE = math.pi
SEEKER_START_ANGLE = 3 * (math.pi/2)

# Start Position of all objects 
SEEKER_START_POS = (120,120)
HIDER_START_POS = (680, 680)
flag_x = 680
flag_y = 120


# PLAYER SETTINGS
PLAYER_SPEED = 8
RENDER_FOV = False
FOV = math.pi /3 #60 deg
HALF_FOV = FOV/2
CASTED_RAYS = 120
STEP_ANGLE = FOV/CASTED_RAYS
MAX_DEPTH = 500 # depth of FOV


# End game conditions, IF EITHER IS TRUE GAME IS OVER
FLAG_CAPTURED = False
HIDER_WINS = False
SEEKER_WINS = False

# INITIAL MAP   
MAP = (
        '            '
    '  #     #   '
    '  ###   ### '
    '  ###   ### '
    '  ###   ##  '
    '            '
    '            '
    '   #        '
    '  ###   ### '
    '  ###   ##  '
    '    #   ##  '
    '            ')

# global vars -----------------------------------------------------------------------------

seeker_x, seeker_y = SEEKER_START_POS[0], SEEKER_START_POS[1]
hider_x, hider_y = HIDER_START_POS[0], HIDER_START_POS[1]

hider_angle, seeker_angle = HIDER_START_ANGLE, SEEKER_START_ANGLE

# total Scores 
seeker_points, hider_points = 0, 0

# Colors palate
BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
STEEL_TEAL = (91, 130, 142)
PEWTER_BLUE = (135, 159, 169)
SILVER_SAND = (171, 184, 191)
ANTIQUE_BRASS = (183, 151, 134)

# Game set up
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# Helper functions -----------------------------------------------------------------------------
def determine_square_color(square):
    if square == '#':
        return STEEL_TEAL
    elif square == ' ':
        return SILVER_SAND
    else:
        return BLACK

def draw_map():
    for row in range(MAP_SIZE):
        for col in range(MAP_SIZE):
            # calculate square index
            square = row * MAP_SIZE + col
            # draw rectangle for each tile
            pygame.draw.rect(
                screen,
                determine_square_color(MAP[square]),
                (col*TILE_SIZE, row*TILE_SIZE, TILE_SIZE-1, TILE_SIZE-1) # -1 for the gutters
            )

def update_map():
    return (
    '            '
    '  #     #   '
    '  ###   ### '
    '  ###   ### '
    '  ###   ##  '
    '            '
    '            '
    '   #        '
    '  ###   ### '
    '  ###   ##  '
    '    #   ##  '
    '            '   )













def draw_player(player_x, player_y, color):
    pygame.draw.circle(
        screen,
        color,
        (player_x, player_y),
        PLAYER_DIAMETER
    )

def draw_flag():
    if not FLAG_CAPTURED:
        pygame.draw.circle(
            screen,
            ANTIQUE_BRASS,
            (flag_x, flag_y),
            10
        )

def draw_FOV(player_x, player_y, angle):
    # draw direction
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (player_x, player_y), 
        (player_x - math.sin(angle) * 50,
         player_y + math.cos(angle) * 50,
        ),
        3
    )
    #draw FOV left boundary
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (player_x, player_y), 
        (player_x - math.sin(angle - HALF_FOV) * 50,
         player_y + math.cos(angle - HALF_FOV) * 50,
        ),
        3
    )
    #draw FOV right boundary
    pygame.draw.line(
        screen, 
        ANTIQUE_BRASS,
        (player_x, player_y), 
        (player_x - math.sin(angle + HALF_FOV) * 50,
         player_y + math.cos(angle + HALF_FOV) * 50,
        ),
        3
    )



# ray casting algorithm - for seeker
def cast_rays_seeker():
    global SEEKER_WINS, seeker_points
    start_angle = seeker_angle - HALF_FOV

    # for all casted rays 
    for ray in range (CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            # coordinates of the end of the ray, grows per frame rate
            target_x = seeker_x - math.sin(start_angle) * depth
            target_y = seeker_y + math.cos(start_angle) * depth

            # capture the hider if in range
            if target_y - 1 <= hider_y <= target_y + 1 and target_x - 1 <= hider_x <= target_x + 1:
                seeker_points += SEEKER_WINS_REWARD
                SEEKER_WINS = True
                # these loops are too fast for the reset() call. so we need to return and end it.
                return SEEKER_WINS
             
            # if the index bigger than 100 because of the exit
            if not is_valid(target_x, target_y):
                break
            
            #draw casted ray 
            if RENDER_FOV:
                pygame.draw.line(screen, ANTIQUE_BRASS, (seeker_x, seeker_y), (target_x, target_y))

        # increment casted ray angle
        start_angle += STEP_ANGLE

# ray casting algorithm - for hider
def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist
def cast_rays_hider():
    global hider_points, NUM_TILES
    start_angle = hider_angle - HALF_FOV
    dist_towall = math.inf
    dist_toseeker = math.inf
    dist_toflag = math.inf

    for depth in range(MAX_DEPTH):
        # the tip of the ray as it is expanding
        target_x = hider_x - math.sin(start_angle) * depth
        target_y = hider_y + math.cos(start_angle) * depth

        # find index of the tile
        col = int(target_x / TILE_SIZE)
        row = int(target_y / TILE_SIZE)
        index_square = row * (MAP_SIZE) + col
        
        if index_square >= NUM_TILES:
            break

        # if the ray hits a wall then calculate the disance to the wall and return it.
        elif MAP[index_square] == "#":
            dist_towall = int(calculateDistance(hider_x, hider_y, target_x, target_y))
            # if we are too close to the wall then neg rewards

    # for all casted rays 
    for ray in range (CASTED_RAYS):
        for depth in range(MAX_DEPTH):
            # coordinates of the end of the ray, grows per frame rate
            target_x = hider_x - math.sin(start_angle) * depth
            target_y = hider_y + math.cos(start_angle) * depth
                
            # if the index bigger than 100 because of the exit
            if not is_valid(target_x, target_y):
                break

            # give the hider the ability to see the seeker
            elif target_y - 1 <= seeker_x <= target_y + 1 and target_x - 1 <= seeker_y <= target_x + 1:
                dist_toseeker = int(calculateDistance(hider_x, hider_y, target_x, target_y))

            # give the hider the ability to see the flag
            elif target_y - 1 <= flag_x <= target_y + 1 and target_x - 1 <= flag_y <= target_x + 1:
                dist_toflag = int(calculateDistance(hider_x, hider_y, target_x, target_y))
            
                
            #draw casted ray
            if RENDER_FOV: 
                pygame.draw.line(screen, ANTIQUE_BRASS, (hider_x, hider_y), (target_x, target_y))

        # increment casted ray angle
        start_angle += STEP_ANGLE

    return dist_towall, dist_toseeker, dist_toflag

def is_valid(x,y):
    # position + and - 10px
        # find which col & row is the target in based on coordinates
    col = int(x / TILE_SIZE)
    row = int(y / TILE_SIZE)

    # find index of the tile
    index_square = row * (MAP_SIZE) + col

    # if the index bigger than 100 because of the exit
    if index_square >= NUM_TILES or MAP[index_square] == "#":
        return False
    return True

def flag_found():
    if flag_y - 10 <= hider_y <= flag_y + 10 and flag_x - 10 <= hider_x <= flag_x + 10:
        global FLAG_CAPTURED, hider_points
        FLAG_CAPTURED = True
        hider_points += 1 # reward the hider

    
        
# Main loop of the game -------------------------------------------------------------------------------
# this function is called as oppose to loop. we need to get deep neural network's decision for each move
# action (int) : between 0-4.
# 0 = left
# 1 = up
# 2 = right
# 3 = down
# 4 = don't move










class hasEnv(gym.Env):

	def __init__(self):
		super(hasEnv, self).__init__()
		# Define action and observation space
		# They must be gym.spaces objects
		# Example when using discrete actions:
		self.action_space = spaces.Discrete(5)
		# Example for using image as input (channel-first; channel-last also works):
		self.observation_space = spaces.Box(low= -500, high=500,
											shape=(5+MAX_DEPTH,), dtype=np.float32)

	def step(self, hider_action, seeker_action):
		self.prev_actions.append(hider_action, seeker_action)

		global SEEKER_START_POS, HIDER_START_POS, HIDER_WINS, SEEKER_WINS, seeker_x, seeker_y, hider_x, hider_y, MAP, seeker_angle, hider_angle, hider_points

		screen.fill(BLACK)
		self.hider_reward = 0

	    # these rewards are only for one execution of the step function
		self.seeker_reward = 0
		if RENDER_GAME:
			draw_map()
		# get player input
		keys = pygame.key.get_pressed()

        # ------------- seeker control -------------
		if keys[pygame.K_LEFT] : seeker_angle -= 0.1 # left
		if keys[pygame.K_RIGHT] : seeker_angle += 0.1 # right

		# up
		if keys[pygame.K_UP]:
			seeker_x += -math.sin(seeker_angle) * PLAYER_SPEED
			seeker_y += math.cos(seeker_angle) * PLAYER_SPEED
			if not is_valid(seeker_x, seeker_y):
				# check x and y and see if it is wall
				# if yes go back to privious x and y
				# if not move
				seeker_x -= -math.sin(seeker_angle) * PLAYER_SPEED
				seeker_y -= math.cos(seeker_angle) * PLAYER_SPEED

		# down
		if keys[pygame.K_DOWN]:
			seeker_x -= -math.sin(seeker_angle) * PLAYER_SPEED
			seeker_y -= math.cos(seeker_angle) * PLAYER_SPEED

			if not is_valid(seeker_x, seeker_y):
				seeker_x += -math.sin(seeker_angle) * PLAYER_SPEED
				seeker_y += math.cos(seeker_angle) * PLAYER_SPEED
		
		# don't move
		else: pass

		# ------------- hider control -------------
		if hider_action == 0: 
			hider_angle -= 0.1 # turn left
			self.hider_reward += MOVING # pointlessly moving
		if hider_action == 2: 
			hider_angle += 0.1 # turn right
			self.hider_reward += MOVING # pointlessly moving

		# go up
		if hider_action == 1:
			hider_x += -math.sin(hider_angle) * PLAYER_SPEED
			hider_y += math.cos(hider_angle) * PLAYER_SPEED
			if not is_valid(hider_x, hider_y):
				# check x and y and see if it is wall
				# if yes go back to privious x and y
				# if not move
				hider_x -= -math.sin(hider_angle) * PLAYER_SPEED
				hider_y -= math.cos(hider_angle) * PLAYER_SPEED
			
			self.hider_reward += MOVING # pointlessly moving

		# go down
		if hider_action == 3:
			hider_x -= -math.sin(hider_angle) * PLAYER_SPEED
			hider_y -= math.cos(hider_angle) * PLAYER_SPEED

			if not is_valid(hider_x, hider_y):
				hider_x += -math.sin(hider_angle) * PLAYER_SPEED
				hider_y += math.cos(hider_angle) * PLAYER_SPEED
			
			self.hider_reward += MOVING # pointlessly moving

		# don't move
		else:
			self.hider_reward += NOT_MOVING 
			pass

		# draw player on map
		if RENDER_GAME:
			draw_player(seeker_x, seeker_y, PEWTER_BLUE)
			draw_player(hider_x, hider_y, BLACK)
			draw_FOV(seeker_x, seeker_y, seeker_angle)
			draw_FOV(hider_x, hider_y, hider_angle)
		
		# player vision being drawn
		self.SEEKER_WINS = cast_rays_seeker()

		# if seeker wins then hider loses
		if self.SEEKER_WINS:
			self.seeker_reward += SEEKER_WINS_REWARD
			self.hider_reward += HIDER_LOSES_PENALTY

		self.dist_towall, self.dist_toseeker, self.dist_toflag = cast_rays_hider()
		if self.ist_towall <= 15:
			hider_points += NEAR_WALL
			self.hider_reward += NEAR_WALL



		# if the hider is within 10 px of the flag capture it and open exit
		if flag_y - 10 <= hider_y <= flag_y + 10 and flag_x - 10 <= hider_x <= flag_x + 10:
			FLAG_CAPTURED = True
			MAP = update_map()
			hider_points += GOT_THE_FLAG # total points thus far
			self.hider_reward += GOT_THE_FLAG # only for this execution
			
		else:    
			draw_flag()
		
		# hider makes it to exit without being captured
		if 750 <= hider_y <= 800 and 240 <= hider_x <= 320:
			self.HIDER_WINS = True
			hider_points += HIDER_WINS_REWARD
			self.hider_reward += HIDER_WINS_REWARD
			self.seeker_reward += SEEKER_LOSES_PENALTY
		info = {}
		# check if anyone won the game
		if HIDER_WINS or self.SEEKER_WINS:    
			done = True
			self.reset()
		else: 
			done = False
		
		
		# display the points
		# print( "Seeker's points: ", seeker_points )
		# print( "Hider's points: ", hider_points )

		# Update display at the end
		pygame.display.flip()
		clock.tick(120) #run faster
			# # create observation:

		observation = [hider_x, hider_y, hider_angle, self.dist_towall, self.dist_toseeker, self.dist_toflag] + list(self.prev_actions)
		# observation = [hider_x, hider_y, hider_angle] + list(self.prev_actions)
		observation = np.array(observation)

		return observation, self.hider_reward, self.done, info
		


	def reset(self):

		global SEEKER_START_POS, HIDER_START_POS,HIDER_WINS, SEEKER_WINS, seeker_x, seeker_y, hider_x, hider_y, MAP, seeker_angle, hider_angle
		# # Initial hider and seeker position
		seeker_x, seeker_y = SEEKER_START_POS[0], SEEKER_START_POS[1]
		hider_x, hider_y = HIDER_START_POS[0], HIDER_START_POS[1] 
		seeker_angle, hider_angle = SEEKER_START_ANGLE, HIDER_START_ANGLE

		SEEKER_WINS = False
		HIDER_WINS = False

		MAP = ( '            '
                '  #     #   '
                '  ###   ### '
                '  ###   ### '
                '  ###   ##  '
                '            '
                '            '
                '   #        '
                '  ###   ### '
                '  ###   ##  '
                '    #   ##  '
                '            ')
		#to dooooo
		
		self.prev_actions = deque(maxlen = MAX_DEPTH)  # 
		for i in range(MAX_DEPTH):
			self.prev_actions.append(-1) # to create history

		self.dist_towall, self.dist_toseeker, self.dist_toflag = cast_rays_hider()
		# create observation:
		observation = [hider_x, hider_y, hider_angle, self.dist_towall, self.dist_toseeker, self.dist_toflag] + list(self.prev_actions)
		

		observation = np.array(observation)
		

		return observation