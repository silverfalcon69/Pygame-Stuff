#use mousewheel to adjust windspeed+direction

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
font = pygame.font.SysFont('monospace', 30)
pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
pygame.mixer.init()
pygame.display.set_caption("Rain")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = (720, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

    ##############################################################################################

wind = 0

class RainDrop(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((5, 15)); self.image.fill((173, 206, 240))
        x, y = random.randint(-SIZE[0]*0.5, SIZE[0]*1.5), 0-self.image.get_height()
        self.rect = self.image.get_rect(center=(x, y))

        self.grav = 2
        self.speed = random.uniform(6, 12) * self.grav

    def calculate(self):
        self.rect.x += wind
        self.rect.y += self.speed

        if self.rect.y > SIZE[1]:
            rain.remove(self)
            return

        for ob in sorted(obstacles, reverse=True):
            if ob.rect.colliderect(self.rect) and random.randint(1, 2) == 1:
                rain.remove(self)

    def update(self):
        self.calculate()
        screen.blit(self.image, self.rect)

class RainSplash():
    pass

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.rect = pygame.Rect(x, y, w, h)

    def update(self):
        pygame.draw.rect(screen, (0, 30, 100), self.rect, 0)

    ##############################################################################################

rain = pygame.sprite.Group()
def gen_rain():
    for i in range(20):
        rain.add(RainDrop())

obstacles = pygame.sprite.Group()
obstacles.add(Obstacle(300, 400, 120, 80))

particles = pygame.sprite.Group()

    ##############################################################################################

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

        elif event.type == pygame.MOUSEWHEEL:
            wind += event.y

    screen.fill((5, 5, 5))

    obstacles.update()

    rain.update()
    if random.randint(1, 10) == 1:
        gen_rain()

    #fps
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))
    windSpeed = font.render(f'WSp: {wind}', True, (215, 215, 215))
    screen.blit(windSpeed, (0, 30))

    pygame.display.update()
    clock.tick(60)