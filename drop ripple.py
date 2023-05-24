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
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
pygame.display.set_caption("")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = WIDTH, HEIGHT = (720, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

    ##############################################################################################

class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.radius = 0
        self.col = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        self.limit = random.randint(50, 200)

    def update(self, screen):
        self.draw(screen)

        self.radius += 1
        if self.radius > self.limit:
            drops.remove(self)

    def draw(self, screen):
        surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
        pygame.draw.circle(
            surf,
            self.col,
            (self.radius, self.radius),
            self.radius,
            2
        )
        
        transparency = 255 - int((self.radius/self.limit)*255)
        surf.set_alpha(transparency)
        screen.blit(surf, list(map(lambda x:x-self.radius, self.pos)))

drops = pygame.sprite.Group()

    ##############################################################################################

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

    screen.fill((255, 255, 255))

    drops.update(screen)
    if random.randint(1, 5) == 1:
        drops.add(Drop(random.randint(0, WIDTH), random.randint(0, HEIGHT)))

    #fps
    font = pygame.font.SysFont('monospace', 30)
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()