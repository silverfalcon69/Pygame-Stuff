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
SIZE = WIDTH, HEIGHT = (1440, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

    ##############################################################################################

def euclidean_distance(pos1, pos2):
    x = abs(pos2.x - pos1.x); y = abs(pos2.y - pos1.y); return math.sqrt(x**2 + y**2)

def line_collision(point, l1, l2):
    line = pygame.math.Vector2(l1[1] - l2[1], l2[0] - l1[0])
    linePoint = pygame.math.Vector2(l1)
    mouse = pygame.math.Vector2(point)
    return abs(line.normalize().dot(mouse - linePoint))

    ##############################################################################################

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super().__init__()
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-1, 1]))
        self.width = width
        self.speed = random.randint(1, 2)
        self.col = (255, 255, 255)

    def move(self):
        self.pos += self.vel * self.speed


    def collisions_border(self):
        #border
        if self.pos.x <= self.width:
            self.vel.x *= -1
        elif self.pos.x >= WIDTH-self.width:
            self.vel.x *= -1

        if self.pos.y <= self.width:
            self.vel.y *= -1
        elif self.pos.y >= HEIGHT-self.width:
            self.vel.y *= -1

    def collisions_particle(self, particle):
        x = self.pos.x - particle.pos.x
        y = self.pos.y - particle.pos.y

        if x==0:x=1
        if y==0:y=1

        if abs(x) >= abs(y):
            self.vel = pygame.math.Vector2(x/abs(x), y/abs(x))
        else:
            self.vel = pygame.math.Vector2(x/abs(y), y/abs(y))


    def update(self, screen, particles):
        for p in particles:
            if p != self:

                distance = euclidean_distance(p.pos, self.pos)
                if distance < self.width:
                    self.collisions_particle(p)

                elif 0 < distance < 200:
                    col = abs(distance-255)
                    line = pygame.draw.line(
                        screen,
                        (col, col, col),
                        self.pos,
                        p.pos
                    )

                    if line.collidepoint(pygame.mouse.get_pos()):
                        if line_collision(pygame.mouse.get_pos(), self.pos, p.pos) < 0.5:
                            print("collision")
                            print("#")

        self.collisions_border()
        self.move()
        self.draw(screen)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.col,
            self.pos,
            self.width
        )


particles = pygame.sprite.Group()
pos = []
for i in range(60):
    width =  5
    particles.add(
        Particle(random.randint(width, WIDTH-width), random.randint(width, HEIGHT-width), width)
    )

    ##############################################################################################

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_SPACE:
                MOVE = not MOVE

    screen.fill((10, 10, 10))
    particles.update(screen, particles)

    #fps
    font = pygame.font.SysFont('monospace', 30)
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()