#Base Platformer
from pygame import *
import glob
class Mob:
    def __init__(self):
        self.X, self.Y=400,300
        self.W, self.H= 16, 48
        self.vX, self.vY=0,0
        self.vM, self.vAx=1.5,0.4
        self.oG = False
player=Mob()
friction=0.111
gravity=0.25
currentTile=0
tileSetRects=glob.glob('tileset/plat?.txt')
drawTiles=[]
tileRects=[]
paused=False
for i in range(len(tileSetRects)):
    tileFile=open(tileSetRects[i])
    tileRects.append([])
    drawTiles.append(Surface((800,600)))
    drawTiles[i].fill((255,255,255))
    for j in tileFile:
        newPlat=[int(i) for i in j.split()]
        draw.rect(drawTiles[i],(0,0,0),newPlat)
        tileRects[i].append(Rect(newPlat))
screen=display.set_mode((800,600))
running=True
playerStanding=Surface((16,48))
playerStanding.fill((255,0,0))
gameClock=time.Clock()
onGround=False
def keysDown():
    global player
    keys=key.get_pressed()
    if keys[K_a]:
        player.vX-=player.vAx
    if keys[K_s]:
        print("Insert Crouch Thing")
    if keys[K_d]:
        player.vX+=player.vAx
        
def applyFriction(mob):
    global friction
    if mob.vX>0:
        mob.vX=min(mob.vX,mob.vM)
        mob.vX-=friction
    elif mob.vX<0:
        mob.vX=max(mob.vX,-mob.vM)
        mob.vX+=friction
    elif mob.vX in range(1,-1):
       mob.vX=0
    return mob

def move(mob):
    mob.X+=mob.vX
    mob.Y+=mob.vY
    
def hitSurface(mob,tile):
    global gravity
    mobRect=Rect(mob.X,mob.Y,mob.W,mob.H)
    for platTile in tileRects[tile]:
        if mobRect.colliderect(platTile):
            mob.vY=0
            mob.oG=True
            if mobRect.bottom < platTile.bottom:
                mob.Y=platTile.top-mob.H
                mob.oG=True
            elif mobRect.top>platTile.top:
                mob.Y=platTile.bottom
            else:
                mob.Y=platTile.top-mob.H
        if mobRect.move(0,2).colliderect(platTile):
            mob.oG=False
        print(mob.oG)
    if not mob.oG:
        mob.vY+=gravity
def drawStuff(tileNum):
    screen.blit(drawTiles[tileNum],(0,0))
    screen.blit(playerStanding,(int(player.X)-8, int(player.Y)))
while running:
    for e in event.get():
        if e.type==QUIT:
            running=False
        if e.type==KEYDOWN:
            if e.key ==K_w:
                player.vY=-6
                player.oG=False
            if e.key==K_p:
                if paused:
                    paused=False
                elif not paused:
                    paused=True
    display.set_caption(str(int(gameClock.get_fps())))
    if not paused:
        keysDown()
        hitSurface(player,currentTile)
        player=applyFriction(player)
        move(player)
        drawStuff(currentTile)
    display.flip()
    gameClock.tick(60)
quit()
