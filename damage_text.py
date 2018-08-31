from pygame import *
WHITE = (255, 255, 255)
font.init()
micRoboto = font.Font('fonts/Roboto-Light.ttf', 13)

class DamageText:
    def __init__(self,x,y,amount,type):
        global WHITE, micRoboto
        self.x = x
        self.y = y
        self.amount = amount
        if type == 0:
            self.colour = WHITE
        elif type == 1:
            self.colour = (255,255,0)
        self.vY = -0.5
        self.renderedText = micRoboto.render('-%s'%(str(round(self.amount,2))),True,self.colour)
        self.life = 50
    def move(self):
        self.y+=self.vY
        self.vY += 0.025
        self.life -= 1