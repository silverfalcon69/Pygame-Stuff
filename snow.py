import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import contextlib
with contextlib.redirect_stdout(None):
    import pygame
    from pygame.locals import *
    
import random
import sys
import math
import time

    ##############################################################################################

#initialising pygame stuff
pygame.init()  #general pygame
pygame.font.init() #font stuff
pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
pygame.mixer.init()
pygame.event.set_blocked(None) #setting allowed events to reduce lag
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])
pygame.display.set_caption("Snow")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = (1200, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

    ##############################################################################################

class Snowflake(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = random.randint(2, 8)
        x, y = random.randint(0, SIZE[0]), 0-self.width
        self.rect = pygame.Rect(0, 0, self.width, self.width); self.rect.center = (x, y)

        self.speed = random.randint(1, 2)

    def calculate(self):
        self.rect.x += self.speed if random.randint(0,1) == 0 else -self.speed
        self.rect.y += self.speed
        if self.rect.y > SIZE[1]:
            snow.remove(self)
            
        self.width = random.randint(2, 10)
        self.speed = random.randint(1, 2)

    def update(self):
        self.calculate()
        pygame.draw.circle(screen, (255, 255, 255), self.rect.center, self.width//2)

snow = pygame.sprite.Group()
def gen_snow():
    for i in range(5):
        snow.add(Snowflake())

    ##############################################################################################

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    screen.fill((5, 5, 5))
    snow.update()
    if random.randint(1, 10) == 1:
        gen_snow()
    if pygame.key.get_pressed()[pygame.K_SPACE]:
        gen_snow()

    pygame.display.update()
    clock.tick(60)