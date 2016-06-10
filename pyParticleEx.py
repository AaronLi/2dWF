from pygame import *
import pyParticle, random, math
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
upperSurf=Surface((22,20),SRCALPHA)
upperSurf.blit(frostUpper,(1, 0))#(380, 288))
upperSurf.blit(braton,(1+4, 0+8))#(384,296))
upperSurf.blit(frostArms, (1-1, 0+10))#(379, 298))
mouse.set_visible(False)
def sind(deg):
    return math.sin(math.radians(deg))
def cosd(deg):
    return math.cos(math.radians(deg))
while running:
    for e in event.get():
        if e.type==QUIT:
            running=False
    mx, my=mouse.get_pos()
    if mouse.get_pressed()[0]:
        playerX, playerY = mx,my

        
    angle = math.degrees(math.atan2(mx-playerX, my-playerY))-90
    screen.blit(frostLower, (playerX-12, playerY+4))#(376, 299))
    rotUpper=transform.rotate(upperSurf,angle)
    screen.blit(rotUpper, (playerX-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2))
    if partTime%10 == 0:            
        if len(partList)<100:
            for i in range(10):
                partList.append(pyParticle.Particle(screen, playerX+10*cosd(angle), playerY-10*sind(angle), -angle, 100, (200, random.randint(100,200), 0), 5, 2, 0.1,10, 2, 20))
        draw.line(screen,(155,100,0), (playerX+10*cosd(angle), playerY-10*sind(angle)), (playerX+5000*cosd(angle), playerY-5000*sind(angle)))
    for i in range(len(partList)-1,-1,-1):
        partList[i].moveParticle()
        if not partList[i].live:
            del partList[i]

    partTime+=1
    clockity.tick(60)
    draw.circle(screen,(0,0,0), mouse.get_pos(), 3)
    display.flip()
    screen.fill((255,255,255))
quit()
    
