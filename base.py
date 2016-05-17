#Base Platformer
#TODO: Seperate walls and platforms, x y w h wall(0)/plat(1)
from pygame import *
import glob
class Mob:
    def __init__(self):
        self.X, self.Y=400,300
        self.W, self.H= 16, 32
        self.vX, self.vY=0,0
        self.vM, self.vAx=4,0.3
        self.oG = False
        self.jumps=2
player=Mob()
friction=0.1111
gravity=0.25
currentTile=0
tileSetRects=glob.glob('tileset/plat?.txt')
drawTiles=[]
tileRects=[]
counter=0
paused=False
for i in range(len(tileSetRects)):
    tileFile=open(tileSetRects[i])
    tileRects.append([])
    drawTiles.append(Surface((1280,720)))
    drawTiles[i].fill((255,255,255))
    for j in tileFile:
        platInfo=j.split()
        newPlat=[int(platInfo[i]) for i in range(4)]
        draw.rect(drawTiles[i],(0,0,0),newPlat)
        tileRects[i].append([Rect(newPlat),int(platInfo[4])])
screen=display.set_mode((1280,720))
running=True
playerStanding=Surface((player.W,player.H))
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
    mob.X+=int(mob.vX)
    mob.Y+=int(mob.vY)
    
def hitSurface(mob,tile):
    global gravity
    mobRect=Rect(mob.X,mob.Y,mob.W,mob.H)
    for platTile in tileRects[tile]:
        if mobRect.move(0,1).colliderect(platTile[0]) and platTile[1]==0:
            mob.vY=0
            if mobRect.bottom < platTile[0].bottom:
                mob.Y=platTile[0].top-mob.H
                mob.oG=True
                mob.jumps=2
            elif mobRect.top>platTile[0].top:
                mob.Y=platTile[0].bottom
                mob.vY*=-1
                mob.oG=False
        if mobRect.colliderect(platTile[0]) and platTile[1]==1:
            if mobRect.left < platTile[0].left:
                mob.X=platTile[0].left-mob.W-1
                mob.jumps=2
            elif mobRect.right>platTile[0].right:
                mob.X=platTile[0].right+1
                mob.jumps=2
        if not mobRect.move(0,0).colliderect(platTile[0]):
            mob.oG=False
    if not mob.oG:
        mob.vY+=gravity
def drawStuff(tileNum):
    screen.blit(drawTiles[tileNum],(0,0))
    screen.blit(playerStanding,(int(player.X), int(player.Y)))
while running:
    for e in event.get():
        if e.type==QUIT:
            running=False
        if e.type==KEYDOWN:
            if e.key ==K_w and player.jumps>0:
                player.vY=-6
                player.oG=False
                player.jumps-=1
            if e.key==K_p:
                if paused:
                    paused=False
                elif not paused:
                    paused=True
            if e.key==K_c:
                counter+=1
                currentTile=counter%len(drawTiles)
    display.set_caption(str(int(gameClock.get_fps())))
    if not paused:
        keysDown()
        move(player)
        hitSurface(player,currentTile)
        player=applyFriction(player)

        drawStuff(currentTile)
    display.flip()
    gameClock.tick(60)
quit()
