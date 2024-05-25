#!/usr/bin/env python
# coding: utf-8

# In[2]:


import gymnasium as gym
import numpy as np
import sys
import pygame
import math
import random
import os
import time 


# In[4]:


def signif(x:int, digits=2):
    """_summary_ Method gives significant bit as a value.

    Args:
        x (int): Significant bits position
        digits (int, optional): It is till how much significant bit is required. Defaults to 2.

    Returns:
        int: Rounded value
    """
    if x == 0 or not math.isfinite(x):
        return x
    digits -= math.ceil(math.log10(abs(x)))
    return round(x, digits)


# In[5]:


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
class starEnv(gym.Env):
    def __init__(self,grid_size=5) -> None:
        super().__init__()
        self.grid_size = grid_size
        self.cell_size = 80
        self.state = None
        self.reward = 0
        self.info = {}
        self.goal = np.array([4,4])
        self.done = False
        self.hurdle_states = []
        self.agent_health = 100
        

        # Action-space:
        self.action_space = gym.spaces.Discrete(4)
        
        # Observation space:
        self.observation_space = gym.spaces.Box(low=0, high=grid_size-1, shape=(2,), dtype=np.int32)

        # Initialize the window:
        pygame.init()
        self.screen = pygame.display.set_mode((self.cell_size*self.grid_size, self.cell_size*self.grid_size))
        self.font = pygame.font.SysFont("Arial", 24)
        
    def show_welcome_message(self):
        font = pygame.font.Font(None, 74)
        text = font.render("StarWays", True, (255, 182, 193))
        text_rect = text.get_rect(center=(self.cell_size * self.grid_size // 2, self.cell_size * self.grid_size // 2))

        self.screen.fill((0, 0, 0))
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        
    def show_gamewin_message(self):
        font = pygame.font.Font(None, 74)
        text = font.render("StarWays Won", True, (255, 182, 193))
        text_rect = text.get_rect(center=(self.cell_size * self.grid_size // 2, self.cell_size * self.grid_size // 2))

        self.screen.fill((0, 0, 0))
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        pygame.time.delay(8000)
    
    def show_gamelost_message(self):
        font = pygame.font.Font(None, 74)
        text = font.render("StarWays Game Over", True, (255, 182, 193))
        text_rect = text.get_rect(center=(self.cell_size * self.grid_size // 2, self.cell_size * self.grid_size // 2))

        self.screen.fill((0, 0, 0))
        self.screen.blit(text, text_rect)
        
        pygame.display.flip()
        pygame.time.delay(8000)

    def reset(self):
        """_summary_ This resets the game to initial  state and agent moves to the starting

        Returns:
            array,string: To know that the game has been reset
        """
        self.state = np.array([0,0])
        self.done = False
        self.reward = 0
        self.agent_health= 100

        self.info["Distance to goal"] = np.sqrt(
        (self.state[0]-self.goal[0])**2 + 
        (self.state[1]-self.goal[1])**2
        )

        return self.state, self.info

    def add_hurdle_states(self, hurdle_state_coordinates):
        self.hurdle_states.append(np.array(hurdle_state_coordinates))
        
    

    def step(self,action):
        """_summary_ This method gives the agent power to move over the screen

        Args:
            action (int): Here the agent can perform (Up,Down,Right,Left) --> (0,1,2,3)

        Returns:
            int,int,bool,str: Here we return the state,how much score,is the game over,what is the distance
        """
        # Up 
        if action == 0 and self.state[0] > 0:
            self.state[0] -= 1

        # Down
        if action == 1 and self.state[0] < self.grid_size - 1:
            self.state[0] += 1

        # Right
        if action == 2 and self.state[1] < self.grid_size - 1:
            self.state[1] += 1

        # Left
        if action == 3 and self.state[1] < self.grid_size - 1:
            self.state[1] -= 1
        
            
        distance_from_closest_hurdle = dict({"distance":10,"co_ordinate":None})
        
        
        # Logic to find the closest hell state and the distance from that hell states
        distancesList = []
        for each_hurdle in self.hurdle_states:
            # Logic to consider the hurdles which are close to state by row
            distanceFromHurdle = np.sqrt(
            (self.state[0]-each_hurdle[0])**2 + 
            (self.state[1]-each_hurdle[1])**2
            )
            distancesList.append(distanceFromHurdle)
            
        # print("CHECK 4: Distances List",distancesList,"Hurdles List",self.hurdle_states)
        distance_from_closest_hurdle["distance"] = np.min(distancesList)
        index_of_minhurdle = np.argmin(distancesList)
        
        distance_from_closest_hurdle["co_ordinate"] = each_hurdle[index_of_minhurdle]
            
        
        
        
             
        # If agent reaches the Goal 🥅 State
        if np.array_equal(self.state,self.goal):
            self.reward += 100
            self.done = True

        # If agent reaches the Hurdle  🥅 States
        elif True in [np.array_equal(self.state,each_hurdle) for each_hurdle in self.hurdle_states]:
            self.reward += -100
            self.done = True

        else:
            # Logic is that when agent is close to one block from the hell state
            if distance_from_closest_hurdle["distance"] <= 1:
                self.reward   += -((round(distance_from_closest_hurdle["distance"]))*10)
            else:
                self.reward += 0
                
            
                
            self.done = False

        # Setting up information how much distance it is from Goal and 
        self.info["Distance to goal"] = np.sqrt(
        (self.state[0]-self.goal[0])**2 + 
        (self.state[1]-self.goal[1])**2
        )
        self.info["Closest hell state co-ordinates"] = distance_from_closest_hurdle["co_ordinate"]
        self.info["Closest distance from hell state"] = distance_from_closest_hurdle["distance"]
        

        return self.state, self.reward, self.done, self.info
    
    

    def _draw_star(self, x, y, size):
        """
        Here we create grid lines with stars

        Args:
            x (int): x axis 
            y (int): y axis
            size (int): Size of the star
        """
        angle = math.pi / 5
        r = size / 2
        outer_points = [(x + r * math.cos(angle * (i * 2)), y + r * math.sin(angle * (i * 2))) for i in range(5)]
        inner_points = [(x + (r / 2) * math.cos(angle * (i * 2 + 1)), y + (r / 2) * math.sin(angle * (i * 2 + 1))) for i in range(5)]
        points = [point for sublist in zip(outer_points, inner_points) for point in sublist]
        pygame.draw.polygon(self.screen, (255, 255, 255), points,2)   
        
    # -----------------------------------------GAME DISPLAY-----------------------------------------------
    def render(self):
        """_summary_ Here we will process the game and will display over the screen
        
        """
        for event in pygame.event.get():
            if event == pygame.QUIT:
                pygame.quit()
                sys.exit()

        bg = pygame.image.load("bg-space.jpg").convert_alpha()
        bg = pygame.transform.smoothscale(bg,(self.cell_size*self.grid_size, self.cell_size*self.grid_size))
        self.screen.fill((255,255,255))
        self.screen.blit(bg,(0,0))

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                star_size = 6  # Adjust this value to change the size of the stars
                self._draw_star(x * self.cell_size, y * self.cell_size, star_size)
                    

        # Draw the Goal-state:
        goal_or_image = pygame.image.load('ufo.webp').convert_alpha()
        goal_ch_image = pygame.transform.smoothscale(goal_or_image,(self.cell_size,self.cell_size))
        goalRect = pygame.Rect(self.goal[1]*self.cell_size, self.goal[0]*self.cell_size, self.cell_size, self.cell_size)
        self.screen.blit(goal_ch_image,goalRect)

        gifpath = os.path.join(os.getcwd(),'blackhole.jpg')
        hurdleImage = pygame.image.load(gifpath).convert_alpha()
        
        # # Draw the hell-states:
        for each_hurdle in self.hurdle_states:
            hurdleChImage = pygame.transform.smoothscale(hurdleImage,(self.cell_size,self.cell_size))
            hellRect = pygame.Rect(each_hurdle[1]*self.cell_size, each_hurdle[0]*self.cell_size, self.cell_size, self.cell_size)
            self.screen.blit(hurdleChImage,hellRect)

        # Draw the agent:
        agent_or_image = pygame.image.load('alien-icon.png').convert_alpha()
        if(self.agent_health < 100):
            agent_or_image = pygame.image.load('alien-icon-damage.png').convert_alpha()
            pygame.display.update()
        agent_ch_image = pygame.transform.smoothscale(agent_or_image,(self.cell_size,self.cell_size))
        agentRect = pygame.Rect(self.state[1]*self.cell_size, self.state[0]*self.cell_size, self.cell_size, self.cell_size)
        # pygame.draw.rect(self.screen, (255,0,0), agent)
        self.screen.blit(agent_ch_image,agentRect)
        
        # Show the score
        print("CHECK2 : Self Reward Depleting health:",self.reward)
        self.agent_health += self.reward
        health_text = self.font.render(f"Health:  {self.agent_health}", True, (255, 0, 0))
        self.screen.blit(health_text, (0, 4)) 
        # Update contents on the window:
        pygame.display.flip()

    def close(self):
        """_summary_ This method is mainly for closing the pygame.
        """
        pygame.quit()

        


# In[4]:


star_env = starEnv(grid_size=10)
star_env.show_welcome_message()
star_env.add_hurdle_states(hurdle_state_coordinates=(0,5))
star_env.add_hurdle_states(hurdle_state_coordinates=(1,3))
star_env.add_hurdle_states(hurdle_state_coordinates=(3,6))
star_env.add_hurdle_states(hurdle_state_coordinates=(4,4))
star_env.add_hurdle_states(hurdle_state_coordinates=(5,9))
star_env.add_hurdle_states(hurdle_state_coordinates=(6,7))
star_env.add_hurdle_states(hurdle_state_coordinates=(7,3))
star_env.add_hurdle_states(hurdle_state_coordinates=(8,8))
star_env.add_hurdle_states(hurdle_state_coordinates=(9,1))


# In[5]:


observation,info = star_env.reset()

print(f"Initial state: {observation}, Info: {info}")


back = False
chances_dynamic = star_env.grid_size * 3
for _ in range(chances_dynamic):
    action = int(input("Choose the war: "))

    new_state, reward, done, info = star_env.step(action)
    print(f"New state: {new_state}, Reward: {reward}, Done: {done}, Info: {info}")
    pygame.display.update()
    pygame.display.flip()

    # Check for termination condition
    if done:
        if(reward > 0):
            star_env.show_gamewin_message()
        else:
            star_env.show_gamelost_message()
        star_env.close()
        break
        
     # Render the environment
    star_env.render()
        


# # Analysis
# - I found that if I take the path 3,4 it is optimal
# 
