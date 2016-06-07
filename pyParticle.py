#Python Particles!
#Aaron Li
from pygame import *
import random, math
def _sind(deg):
    return math.sin(math.radians(deg))
def _cosd(deg):
    return math.cos(math.radians(deg))
class Particle:
    def __init__(self,surface,x,y,rotation, lifetime, colour, speed, gravity, airResistance,fadeRate, length=1, variation = 10):
        colourOff=random.randint(0,255-max(colour))
        self.surf=surface
        self.X, self.Y=x,y
        self.rot=rotation+random.randint(-variation,variation)
        self.life=lifetime
        self.col=(colour[0]+colourOff, colour[1]+colourOff, colour[2]+colourOff)
        self.speed = speed
        self.fG = gravity
        self.aR = airResistance
        self.fR = fadeRate
        self.live = True
        self.length = length
        
    def moveParticle(self):
        if self.live:
            draw.line(self.surf, self.col, (int(self.X), int(self.Y)), (int(self.X-self.length*_cosd(self.rot)), int(self.Y-self.length*_sind(self.rot))))
            self.X+=self.speed*_cosd(self.rot)
            self.Y+=self.speed*_sind(self.rot)
            self.col=(max(self.col[0]-self.fR, 0), max(self.col[1]-self.fR, 0), max(self.col[2]-self.fR, 0))
            self.life-=1
            self.speed=max(self.speed-self.aR, 0)
            self.Y=max(self.Y+self.fG, 0)
        if self.life <= 0:
            self.live = False
