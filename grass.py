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
import numpy as np

    ##############################################################################################

#initialising pygame stuff
pygame.init()  #general pygame
pygame.font.init() #font stuff
pygame.mixer.pre_init(44100, 16, 2, 4096) #music stuff
pygame.mixer.init()
pygame.event.set_blocked(None) #setting allowed events to reduce lag
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEWHEEL])
pygame.display.set_caption("")

#initalising pygame window
flags = pygame.DOUBLEBUF #| pygame.FULLSCREEN
SIZE = WIDTH, HEIGHT = (1000, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

#renaming common functions
vec = pygame.math.Vector2
font = pygame.font.SysFont('monospace', 12)

    ##############################################################################################

WIND = 0.125

def rotate_vec(origin, point, angle):
    angle = math.radians(angle)
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        self.pos = pygame.math.Vector2()
        self.radius = 20

        self.surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(
            self.surf, 
            (255, 255, 255), 
            (self.surf.get_width()//2, self.surf.get_width()//2), 
            self.surf.get_width()//2, 
            self.surf.get_width()//20)
        
        # self.clicked = self.surf.copy()
        # pygame.draw.circle(
        #     self.clicked,
        #     ()
        # )
        
        self.shadow = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.shadow.fill((255, 255, 255))
        pygame.draw.circle(
            self.shadow, 
            (128, 128, 128), 
            (self.surf.get_width()//1.5, self.surf.get_width()//1.5), 
            self.surf.get_width()//1.5)
        
        self.surf = pygame.transform.scale(self.surf, (self.radius*2, self.radius*2))
        self.shadow = pygame.transform.scale(self.shadow, (self.radius*2.2, self.radius*1.6))

    def add_grass(self, screen):
        mouse = pygame.mouse.get_pressed()
        mousePos = vec(pygame.mouse.get_pos())

        if mouse[0]:
            tiles_ = []
            for y in range(int(mousePos.y - self.radius), int(mousePos.y + self.radius), 1):
                for x in range(int(mousePos.x - self.radius), int(mousePos.x + self.radius), 1):
                    tile_pos = vec(x // Tile.TILE_WIDTH, (y // Tile.TILE_HEIGHT)+self.radius//Tile.TILE_WIDTH)
                    if tile_pos not in tiles_:
                        tiles_.append(tile_pos)

            for tile_pos in tiles_:
                if tile_pos in tile_positions:
                    return
                
                tile_positions.append(tile_pos)
                try:
                    tile = Tile(
                        (tile_pos.x * Tile.TILE_WIDTH, tile_pos.y * Tile.TILE_HEIGHT), 
                        0
                    )
                    tiles.add(tile)
                except KeyError:
                    return
            
    def change_radius(self, wheel_y):
        self.radius += wheel_y
        if self.radius < 1:
            self.radius = 1

        self.surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(
            self.surf, 
            (255, 255, 255), 
            (self.surf.get_width()//2, self.surf.get_width()//2), 
            self.surf.get_width()//2, 
            self.surf.get_width()//20)
        
        self.shadow = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.shadow.fill((255, 255, 255))
        pygame.draw.circle(
            self.shadow, 
            (128, 128, 128), 
            (self.surf.get_width()//1.5, self.surf.get_width()//1.5), 
            self.surf.get_width()//1.5)
        
        self.surf = pygame.transform.scale(self.surf, (self.radius*2, self.radius*2))
        self.shadow = pygame.transform.scale(self.shadow, (self.radius*2.2, self.radius*1.6))
    
    def update(self, screen):
        self.pos = vec(pygame.mouse.get_pos())
        self.add_grass(screen)
        self.draw(screen)

    def draw(self, screen):
        screen.blit(
            self.shadow, 
            (self.pos.x - self.shadow.get_width()//2.3, self.pos.y - self.shadow.get_height()//3.5), 
            special_flags=pygame.BLEND_RGB_MULT)
        
        if pygame.mouse.get_pressed()[0]:
            pygame.draw.circle(screen, (255, 255, 255), self.pos, self.radius*0.8)

        screen.blit(
            self.surf, 
            list(map(lambda x: x-self.radius, self.pos)))


class GrassBlade(pygame.sprite.Sprite):
    def __init__(self, pos, angle):
        super().__init__()
        self.pos = vec(pos)
        self.width = random.randint(12, 24)
        self.points = [
            vec(self.pos.x, self.pos.y - random.randint(-8, 8)),
            vec(self.pos.x + self.width, self.pos.y - random.randint(-8, 8)) ,
            vec(self.pos.x + self.width - random.randint(4, 12), self.pos.y - random.randint(10, 30)),
            vec(self.pos.x + self.width/2, self.pos.y-(self.width*1.5)),
            vec(self.pos.x + random.randint(4, 12), self.pos.y - random.randint(10, 30)),
        ]
        self.ogRot = self.points[3].copy()
        self.angle = angle
        self.colour = random.choice([
            (179, 190, 64), 
            (56, 108, 48), 
            (137, 178, 70),
            (120, 152, 51),
            (81, 130, 87),
            (91, 152, 56)
        ])
        self.pressed = False

    def mouse_collide(self):
        mousePos = vec(pygame.mouse.get_pos())
        radius = cursor.radius * 1.5

        point = self.points[0] + ((self.points[1] - self.points[0])/2)
        if mousePos.distance_to(point) < radius:
            if self.points[3].x < mousePos.x:
                self.points[3] = vec(rotate_vec((self.pos.x + 20, self.pos.y), self.ogRot.copy(), -30))
            elif self.points[3].x >= mousePos.x:
                self.points[3] = vec(rotate_vec((self.pos.x + 20, self.pos.y), self.ogRot.copy(), 30))
            self.pressed = 20

        else:
            if self.pressed:
                self.pressed -= 1
                if self.points[3].x < mousePos.x:
                    self.points[3] = vec(rotate_vec((self.pos.x + 20, self.pos.y), self.ogRot.copy(), -self.pressed))
                elif self.points[3].x >= mousePos.x:
                    self.points[3] = vec(rotate_vec((self.pos.x + 20, self.pos.y), self.ogRot.copy(), self.pressed))

    def sway(self):
        angle = 10 * math.sin(WIND*2 + self.angle)
        self.points[3] = vec(rotate_vec((self.pos.x + 20, self.pos.y), self.ogRot.copy(), angle))

    def update(self, screen):
        self.mouse_collide()
        #self.draw(screen)

    def draw(self, screen):
        pygame.draw.polygon(
            screen,
            self.colour,
            self.points
        )


class Tile(pygame.sprite.Sprite):
    TILE_WIDTH = WIDTH//32
    TILE_HEIGHT = HEIGHT//32

    CACHED_DATA = {}
    angle = 0
    for tile_y in range(0, HEIGHT, TILE_HEIGHT):
        for tile_x in range(0, WIDTH, TILE_WIDTH):
            CACHED_DATA[(tile_x, tile_y)] = pygame.sprite.Group()

            for y in range(0, TILE_HEIGHT, 20):
                for x in range(0, TILE_WIDTH, 12):
                    CACHED_DATA[(tile_x, tile_y)].add(GrassBlade((tile_x+x, tile_y+y), angle))
                angle += 0.002

    def __init__(self, pos, start_wind):
        super().__init__()
        self.pos = vec(pos)
        self.grass = Tile.CACHED_DATA[pos].copy()
        self.wind_angle = start_wind

    def update(self, screen):
        if pygame.Rect(self.pos.x, self.pos.y, Tile.TILE_WIDTH, Tile.TILE_HEIGHT).collidepoint(pygame.mouse.get_pos()):
            self.grass.update(screen)

        for g in self.grass.sprites():
            g.sway()
            g.draw(screen)
        


cursor = Cursor()

tiles = pygame.sprite.Group()
tile_positions = []

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
            cursor.change_radius(event.y)

    screen.fill((19, 56, 33))
    tiles.update(screen)
    cursor.update(screen)

    WIND += 0.01

    #fps
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()