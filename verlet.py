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
import json

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
SIZE = WIDTH, HEIGHT = (720, 720)
screen = pygame.display.set_mode(SIZE, flags, 16)
clock = pygame.time.Clock()

#renaming common functions
vec = pygame.math.Vector2

#useful functions
def gen_colour():
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))

def euclidean_distance(point1, point2):
    return vec(point1).distance_to(vec(point2))

    ##############################################################################################

GRAV = 9.81/4
FRIC = 0.95
WIND = 0

    ##############################################################################################

class Point(pygame.sprite.Sprite):
    def __init__(self, pos=None, mass=1, radius=None, pinned=False, fabric=False):
        super().__init__()
        self.pos = vec(pos) if pos != None else vec(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
        self.old_pos = vec(self.pos.copy())
        self.mass = mass
        self.pinned = pinned
        self.fabric = fabric

        self.col = gen_colour()
        self.radius = random.randint(30, 50) if radius == None else radius
        self.held = False

    def move(self, dt):
        coords = self.pos.copy()
        old_coords = self.old_pos.copy()

        v = coords - old_coords

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            v.x -= 10
        if keys[pygame.K_d]:
            v.x += 10
        if keys[pygame.K_w]:
            v.y -= 10
        if keys[pygame.K_s]:
            v.y += 10

        v.x *= FRIC
        v.y *= FRIC
        v.y += GRAV
        v.x += WIND
        #v /= self.mass

        self.old_pos = coords
        self.pos = coords + v

    def collide_walls(self):
        coords = self.pos.copy()
        old_coords = self.old_pos.copy()

        v = coords - old_coords
        h = HEIGHT - self.radius

        if coords.x > WIDTH - self.radius:
            self.pos.x = WIDTH - self.radius
            self.old_pos.x = self.pos.x + v.x
        if coords.x < self.radius:  
            self.pos.x = self.radius
            self.old_pos.x = self.pos.x + v.x

        if coords.y > HEIGHT - self.radius:
            self.pos.y = HEIGHT - self.radius
            self.old_pos.y = self.pos.y + v.y
        if coords.y < self.radius:  
            self.pos.y = self.radius
            self.old_pos.y = self.pos.y + v.y

    def collide_balls(self):
        for p in points:
            if p != self:
                overlap = (self.radius * 2) - self.pos.distance_to(p.pos)
                if overlap > 0:
                    try:
                        distance = (self.pos - p.pos).normalize()
                    except ValueError:
                        distance = (self.pos - p.pos)
                    self.pos += distance/2
                    p.pos -= distance/2

        for shape in shapes:
            for p in shape.points:
                if p != self:
                    overlap = (self.radius * 2) - self.pos.distance_to(p.pos)
                    if overlap > 0:
                        try:
                            distance = (self.pos - p.pos).normalize()
                        except ValueError:
                            distance = (self.pos - p.pos)
                        self.pos += distance/2
                        p.pos -= distance/2


    def mouse_move(self):
        mouse = pygame.mouse.get_pressed()
        mousePos = pygame.mouse.get_pos()

        if mouse[0]:
            if vec(mousePos).distance_to(self.pos) < self.radius:
                for p in points:
                    if p != self:
                        if p.held == True:
                            break
                else:
                    self.held = True
        else:
            self.held = False

        if self.held:
            self.pos = vec(mousePos)


    def update(self, screen, dt, draw_flag: bool):
        if not self.pinned: 
            self.collide_balls() if not self.fabric else ...
            self.move(dt)
        self.mouse_move()
        self.collide_walls()

        if draw_flag:
            self.draw(screen)

    def draw(self, screen):
        pygame.draw.circle(screen, self.col, self.pos, self.radius)

class Shape(pygame.sprite.Sprite):

    @classmethod
    def Box(cls, x, y, length, point_radius, line_thickness, colour):
        points = [
            Point((x, y), radius=point_radius),
            Point((x+length, y), radius=point_radius),
            Point((x+length, y+length), radius=point_radius),
            Point((x, y+length), radius=point_radius),
        ]
        joints = [[0, 1], [1, 2], [2, 3], [3, 0], [1, 3], [2, 0]]
        lengths = [euclidean_distance(points[joints[i][0]].pos, points[joints[i][1]].pos) for i in range(len(joints))]
        return cls(points, joints, lengths, line_thickness, colour)
    
    @classmethod
    def Triangle(cls, x, y, length, point_radius, line_thickness, colour):
        points = [
            Point((x, y), radius=point_radius),
            Point((x+length, y), radius=point_radius),
            Point((x+(length/2), y+(length * math.sin(60))), radius=point_radius),
        ]
        joints = [[0, 1], [1, 2], [2, 0]]
        lengths = [length for i in range(len(joints))]
        return cls(points, joints, lengths, line_thickness, colour)
    
    @classmethod
    def Chain(cls, x, y, segment_length, segment_num, pinned, point_radius, line_thickness, colour):
        points = [Point((x+i*segment_length, y), radius=point_radius) for i in range(segment_num)]

        for i in pinned:
            points[i].pinned = True
        
        joints = [[i,i+1] for i in range(len(points)-1)]
        lengths = [segment_length for i in range(len(joints))]
        return cls(points, joints, lengths, line_thickness, colour, False)
    
    @classmethod
    def Fabric(cls, x, y, num_horizontal, num_vert, eye, point_radius, pins, line_thickness, colour):
        points = [Point((x+(i*eye), y+(j*eye)), radius=point_radius, fabric=True) for j in range(num_horizontal) for i in range(num_vert)]

        for i in np.linspace(0, num_horizontal-1, pins):
            points[int(i)].pinned = True
        points[num_horizontal-1].pinned = True

        joints = [[i,i+1] for i in range(len(points)-1) if i%num_horizontal != num_horizontal-1]
        joints += [[i,i+num_horizontal] for i in range(len(points)-num_horizontal)]
        lengths = [euclidean_distance(points[joints[i][0]].pos, points[joints[i][1]].pos) for i in range(len(joints))]
        return cls(points, joints, lengths, line_thickness, colour, False)
    
    @classmethod
    def from_json(cls, offset, json_name, point_radius, line_thickness, colour):
        with open("shapes/"+json_name) as json_file:
            data = json.load(json_file)

        points = list(map(lambda point: Point(vec(point) + offset, radius=point_radius), data["points"]))
        joints = data["joints"]
        lengths = [euclidean_distance(points[joints[i][0]].pos, points[joints[i][1]].pos) for i in range(len(joints))]
        return cls(points, joints, lengths, line_thickness, colour)


    def __init__(self, points, joints: list, lengths, line_thickness: int, colour, draw_flag: bool=False):
        super().__init__()
        self.points = pygame.sprite.Group(points)
        self.joints = joints
        self.lengths = lengths
        self.line_thickness = line_thickness
        self.col = colour
        self.draw_flag = draw_flag

    def constrain(self):
        for i, joint in enumerate(self.joints):
            l = self.lengths[i]

            point1, point2 = self.points.sprites()[joint[0]], self.points.sprites()[joint[1]]
            p1, p2 = point1.pos, point2.pos
            dist = euclidean_distance(p1, p2)

            diffx, diffy = p1.x - p2.x, p1.y - p2.y
            diff = l - dist

            try: updatex = 0.5 * diffx * diff/dist
            except ZeroDivisionError: updatex = 0
            try: updatey = 0.5 * diffy * diff/dist
            except ZeroDivisionError: updatey = 0


            if not (point1.pinned or point2.pinned):
                point1.pos.x += updatex
                point1.pos.y += updatey
                point2.pos.x -= updatex
                point2.pos.y -= updatey

            if not point1.pinned and point2.pinned:
                point1.pos.x += int(updatex) * 2
                point1.pos.y += int(updatey) * 2
            if point1.pinned and not point2.pinned:
                point2.pos.x -= updatex * 2
                point2.pos.y -= updatey * 2

    def update(self, screen, dt):
        self.draw(screen)
        self.points.update(screen, dt, draw_flag=self.draw_flag)
        self.constrain()
        return 1

    def draw(self, screen):
        for j in self.joints:
            start = self.points.sprites()[j[0]].pos
            end = self.points.sprites()[j[1]].pos
            pygame.draw.line(screen, self.col, start, end, self.line_thickness)

    ##############################################################################################

points = pygame.sprite.Group()
# for i in range(10):
#     points.add(Point((WIDTH+i//2, HEIGHT//4), radius=20))

shapes = pygame.sprite.Group()
# shapes.add(Shape.Box(x=100, y=100, length=100, point_radius=3, line_thickness=5, colour=(255, 255, 255)))
# shapes.add(Shape.Triangle(x=300, y=250, length=100, point_radius=5, line_thickness=4, colour=(255, 128, 128)))
# shapes.add(Shape.Box(x=300, y=50, length=150, point_radius=5, line_thickness=8, colour=(255, 128, 128)))
# shapes.add(Shape.Chain(x=20, y=20, segment_length=8, segment_num=50, pinned=[0, 25, -1], point_radius=4, line_thickness=5, colour=(255, 255, 255)))
shapes.add(Shape.Fabric(x=20, y=20, num_horizontal=20, num_vert=20, eye=20, point_radius=4, line_thickness=3, pins=4, colour=(255, 255, 255)))
# shapes.add(Shape.from_json(vec(0, 0), "1.json", 20, 5, (255, 255, 255)))

    ##############################################################################################

last_time = time.time()

running = True
while running:

    dt = time.time() - last_time
    last_time = time.time()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False

        elif event.type == pygame.MOUSEWHEEL:
            WIND += event.y / 10

    screen.fill((30, 30, 30))
    #points.update(screen, dt, True)

    shapes.update(screen, dt)
    # map(lambda x: x.update(screen, dt), shapes)

    #fps
    font = pygame.font.SysFont('monospace', 30)
    fps = font.render(f'FPS: {int(clock.get_fps())}', True, (215, 215, 215))
    screen.blit(fps, (0, 0))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()