from pygame import *
import math


class Door:
    def __init__(self,pos,vY,w,h,openHeight,sprite):
        self.x,self.y = pos
        self.offY = 0
        self.vY = vY
        self.h = h
        self.w = w
        self.openHeight = -openHeight
        self.sprite = sprite
        self.hitBox = Rect(self.x, self.y + self.offY, self.w, self.h)

    def moveDoor(self, mobList, companion, player):
        openDoor = False
        for i in mobList:
            if abs(math.hypot(i.X-self.x,i.Y-self.y)) < 70:
                openDoor = True
        if abs(math.hypot(companion.X-self.x,companion.Y-self.y))<70:
            openDoor = True
        if abs(math.hypot(player.X-self.x,player.Y-self.y))<70:
            openDoor = True
        if openDoor and self.offY >self.openHeight:
            self.offY -= self.vY
        elif not openDoor and self.offY < 0:
            self.offY += self.vY
        self.hitBox = Rect(self.x,self.y+self.offY,self.w,self.h)
    def draw(self, screen, player):
        screen.blit(self.sprite,(640-player.X+self.x,360-player.Y+self.y+self.offY))