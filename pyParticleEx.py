from pygame import *
import pyParticle, random
screen=display.set_mode((800,600))
partList=[]
running=True
clockity=time.Clock()
partTime=0
playerX,playerY = 400, 300
braton = image.load('images/braton.png')
frostUpper = image.load('images/frostUpper.png')
frostArms = image.load('images/frostArms.png')
frostLower = image.load('images/frostLower.png')
while running:
    for e in event.get():
        if e.type==QUIT:
            running=False
    if mouse.get_pressed()[0]:
        playerX, playerY = mouse.get_pos()
    
    screen.blit(frostLower, (playerX-4, playerY+11))#(376, 299))
    screen.blit(frostUpper,(playerX, playerY))#(380, 288))
    screen.blit(braton,(playerX+4, playerY+8))#(384,296))
    screen.blit(frostArms, (playerX-1, playerY+10))#(379, 298))

    if partTime%10 == 0:            
        if len(partList)<10:
            for i in range(2):
                partList.append(pyParticle.Particle(screen, playerX+20, playerY+12, 0, 3, (200, random.randint(100,200), 0), 5, 0.1, 0.1,10, 2, 20))
        draw.line(screen,(155,100,0), (playerX+20,playerY+12), (800, playerY+12))
    for i in range(len(partList)-1,-1,-1):
        partList[i].moveParticle()
        if not partList[i].live:
            del partList[i]

    partTime+=1
    clockity.tick(60)
    display.flip()
    screen.fill((255,255,255))
quit()
    
