import math
from pygame import *

class DamageArea:
    def __init__(self,shape,size,x,y,colour,duration,damage,tickLength):
        self.shape = shape
        if shape == 0:
            self.w = size[0]
            self.h = size[1]
            self.cRect = Rect(x,y,w,h)
        elif shape == 1:
            self.radius = size
        self.x = x
        self.y = y
        self.colour = colour
        self.duration = duration
        self.damage = damage
        self.tickLength = tickLength
        self.currentTick = 0
    def updateCloud(self, mobList):
        if self.currentTick == 0:
            self.currentTick = self.tickLength
            if self.shape == 0:
                for i in mobList:
                    enemyCenter = (i.X+(i.w//2),i.Y+(i.h//2))
                    if math.hypot(self.x-enemyCenter[0],self.y-enemyCenter[1]) <=self.radius:
                        i.damage(self.damage)
            elif self.shape == 1:
                for i in mobList:
                    if self.cRect.collidepoint(i.X,i.Y):
                        i.damage(self.damage)