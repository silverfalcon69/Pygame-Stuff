import pyglet
from pyglet import app
from pyglet.window import key
import random
import math
import time

    ##############################################################################################

window = pyglet.window.Window(width=(WIDTH:=1000), height=(HEIGHT:=640))

keys = key.KeyStateHandler()
window.push_handlers(keys)

batch = pyglet.graphics.Batch()
background = pyglet.graphics.Group(0)
foreground = pyglet.graphics.Group(1)

def euclidean_distance(point1, point2):
    return ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)**0.5

    ##############################################################################################

class Rect:
    def __init__(self, left, bottom, width, height):
        self.x, self.y = left, bottom
        self.size = self.width, self.height = (width, height)

        self.top = self.y + self.height
        self.bottom = self.y
        self.left = self.x
        self.right = self.x + self.width

        self.topleft = (self.x, self.y + self.height)
        self.bottomleft = (self.x, self.y)
        self.topright = (self.y, self.y + self.height)
        self.bottomright = (self.y, self.y)

        self.midtop = (self.x + self.width/2, self.y + self.height)
        self.midleft = (self.x, self.y + self.height/2)
        self.midright = (self.x + self.width, self.y + self.height/2)
        self.midbottom = (self.x + self.width/2, self.y)

        self.center = self.centerx, self.centery = (self.x + self.width/2, self.y + self.height/2)

    def __str__(self):
        return f"Rect({self.x}, {self.y}, {self.width}, {self.height})"
    
    
    def intersect_area(self, rect):
        return (
            max(0,
                min(rect.topright[0], self.topright[0])
                - max(rect.bottomleft[0], self.bottomleft[0])
            ) *
            max(0,
                min(rect.topright[1], self.topright[1])
                - max(rect.bottomleft[1], self.bottomleft[1])
            )
        )

    def collidepoint(self, coord):
        return (self.left <= coord[0] <= self.right) and (self.bottom <= coord[1] <= self.top)
    
    def colliderect(self, rect):
        return self.intersect_area(rect) > 0
    
    def contains(self, rect):
        return self.intersect_area(rect) == (rect.width * rect.height)
    
    def collidelist(self, rects: list):
        return list(map(self.colliderect, rects)).index(True)
    
    def collidelistall(self, rects: list):
        collisions = list(map(self.colliderect, rects))
        return [i for i in range(len(collisions)) if collisions[i]]

    def draw(self, colour=(255, 255, 255)):
        pyglet.shapes.Rectangle(self.x, self.y, self.width, self.height, colour).draw()

    def update_rect(self):
        self.top = self.y + self.height
        self.bottom = self.y
        self.left = self.x
        self.right = self.x + self.width

        self.topleft = (self.x, self.y + self.height)
        self.bottomleft = (self.x, self.y)
        self.topright = (self.y, self.y + self.height)
        self.bottomright = (self.y, self.y)

        self.midtop = (self.x + self.width/2, self.y + self.height)
        self.midleft = (self.x, self.y + self.height/2)
        self.midright = (self.x + self.width, self.y + self.height/2)
        self.midbottom = (self.x + self.width/2, self.y)

        self.center = self.centerx, self.centery = (self.x + self.width/2, self.y + self.height/2)


class Ball(pyglet.shapes.Circle):
    def __init__(self,x, y, radius, color, group):
        super().__init__(x=x, y=y, radius=radius, color=color, batch=batch, group=group)
        self.vel = pyglet.math.Vec2(1, 1)
        self.speed = 5
        self.rect = Rect(x, y, radius, radius)

    def wall_collisions(self):
        if self.y + self.radius >= HEIGHT - 20:
            self.vel.y *= -1
        if self.y - self.radius <= 20:
            self.vel.y *= -1

        global paddles
        if self.x + self.radius >= WIDTH:
            paddles[0].score += 1
            time.sleep(1)
            self.x, self.y = WIDTH - WIDTH//5, HEIGHT//2
            self.vel.x *= -1
        if self.x - self.radius <= 0:
            paddles[1].score += 1
            time.sleep(1)
            self.x, self.y = WIDTH//5, HEIGHT//2
            self.vel.x *= -1

    def update(self):
        self.x += self.vel.x * self.speed
        self.y += self.vel.y * self.speed
        self.rect.x, self.rect.y = self.x, self.y

        self.wall_collisions()

class Paddle(pyglet.shapes.Rectangle):
    def __init__(self, x, width, height):
        super().__init__(x=x, y=HEIGHT//2 - height//2, width=width, height=height, color=(255, 255, 255), batch=batch, group=foreground)
        self.index = 0 if x < WIDTH//2 else 1
        self.controls = {"up":key.W, "down":key.S} if self.index else {"up":key.UP, "down":key.DOWN}
        self.speed = 5
        self.rect = Rect(x, HEIGHT//2 - height//2, width, height)
        self.score = 0


    def collision(self, ball: Ball):
        
        if ((ball.x - ball.radius < self.x + self.width and ball.x + ball.radius > self.x) and
            (ball.y - ball.radius < self.y + self.height and ball.y + ball.radius > self.y)):
            #collision detected

            if ball.x > self.x:
                ball.x += 1
                ball.vel.x = 1
            if ball.x < self.x:
                ball.x -= 1
                ball.vel.x = -1


    def update(self, ball):
        if keys[self.controls["up"]]:
            self.y += self.speed
        if keys[self.controls["down"]]:
            self.y -= self.speed

        if self.y < 30:
            self.y = 30
        if self.y + self.height > HEIGHT - 30:
            self.y = HEIGHT - 30 - self.height
        
        self.collision(ball)

class AIPaddle(pyglet.shapes.Rectangle):
    def __init__(self, x, width, height):
        super().__init__(x=x, y=HEIGHT//2 - height//2, width=width, height=height, color=(255, 255, 255), batch=batch, group=foreground)
        self.index = 0 if x < WIDTH//2 else 1
        self.speed = 5
        self.score = 0


    def collision(self, ball: Ball):
        
        if ((ball.x - ball.radius < self.x + self.width and ball.x + ball.radius > self.x) and
            (ball.y - ball.radius < self.y + self.height and ball.y + ball.radius > self.y)):
            #collision detected

            if ball.x > self.x:
                ball.x += 1
                ball.vel.x = 1
            if ball.x < self.x:
                ball.x -= 1
                ball.vel.x = -1

    def update(self, ball):
        if ball.x > WIDTH//2:
            if ball.y > self.y + self.height//2:
                self.y += 5
            else:
                self.y -= 5

        if self.y < 30:
            self.y = 30
        if self.y + self.height > HEIGHT - 30:
            self.y = HEIGHT - 30 - self.height

        self.collision(ball)

ball = Ball(WIDTH//5, HEIGHT//2, 12, (255, 255, 255), foreground)
paddles = [
    Paddle(40, 40, 120),
    AIPaddle(WIDTH-80, 40, 120),
]

background_stuff = [pyglet.shapes.Rectangle(0, 0, WIDTH, HEIGHT, (255, 255, 255), batch=batch, group=background),
                    pyglet.shapes.Rectangle(20, 20, WIDTH-40, HEIGHT-40, (0, 0, 0), batch=batch, group=background)]
for y in range(30, HEIGHT-30, 40):
    background_stuff.append(pyglet.shapes.Rectangle(WIDTH//2 - 10, y, 20, 20, (255, 255, 255), batch=batch, group=background))
        
    ##############################################################################################

#main update loop
def update(dt):
    ball.update()
    [p.update(ball) for p in paddles]
pyglet.clock.schedule_interval(update, 1/60)

#actual drawing
@window.event
def on_draw():
    window.clear()

    label1 = pyglet.text.Label(
        f"{paddles[0].score}",
        font_name="Times New Roman",
        font_size=72,
        x=WIDTH//2 - 150, y=HEIGHT//1.3,
        batch=batch,
        group=background
    )
    label2 = pyglet.text.Label(
        f"{paddles[1].score}",
        font_name="Times New Roman",
        font_size=72,
        x=WIDTH//2 + 100, y=HEIGHT//1.3,
        batch=batch,
        group=background
    )

    batch.draw()

app.run()