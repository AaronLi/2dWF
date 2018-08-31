import random
from math_tools import *
from pygame import *
class Particle:  # Class used for simulating particles (Guns, 'blood', bullet hits)
    def __init__(self, surface, x, y, rotation, lifetime, colour, speed, gravity, airResistance, fadeRate, length=1,
                 variation=10, size=1):
        colourOff = random.randint(0, 255 - max(colour))
        self.surf = surface
        self.X, self.Y = x, y  # position
        self.rot = rotation + random.randint(-variation, variation)  # direction
        self.life = lifetime  # amount of iterations before it disappears
        self.col = (colour[0] + colourOff, colour[1] + colourOff, colour[2] + colourOff)
        self.speed = speed  # distance it moves per iteration
        self.fG = gravity  # amount it's Y is affected per iteration
        self.aR = airResistance  # amount it's X is affected per iteration
        self.fR = fadeRate  # Amount it's colour fades per iteration
        self.live = True
        self.length = length  # Length of particle tail
        self.size = size

    def moveParticle(self, player):  # Move the particle based on it's speed and remove it if it's dead
        if self.live:
            draw.line(self.surf, self.col, (640 - player.X + int(self.X), 360 - player.Y + int(self.Y)), (
                640 - player.X + int(self.X - self.length * cosd(self.rot)),
                360 - player.Y + int(self.Y - self.length * sind(self.rot))), self.size)
            self.X += self.speed * cosd(self.rot)
            self.Y += self.speed * sind(self.rot)
            self.col = (max(self.col[0] - self.fR, 0), max(self.col[1] - self.fR, 0), max(self.col[2] - self.fR, 0))
            self.life -= 1
            self.speed = max(self.speed - self.aR, 0)
            self.Y = max(self.Y + self.fG, 0)
        if self.life <= 0:
            self.live = False
