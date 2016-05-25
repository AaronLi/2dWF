#Base Platformer
#TODO: Multiple platforms put together
#Have a master platform list that contains all platforms with preoffset platforms in them?
#Stitch together all platform visuals?
from pygame import *
import glob,pprint,random
class Mob:
    def __init__(self):
        self.X, self.Y=400,300
        self.W, self.H=33,36
        self.vX, self.vY=0,0
        self.vM, self.vAx=4,0.3
        self.oG, self.oW = False, False
        self.fA = False #(player.fAcing) True for right, False for left
        self.jumps=2
idleRight, idleLeft, right, left, jumpRight, jumpLeft = 0, 1, 2, 3, 4, 5
player=Mob()
currentFrame=0
#Animations
frames=[[[image.load("images/frost001.png")],1],[[image.load("images/frost003.png"),image.load("images/frost004.png"),image.load("images/frost005.png"),image.load("images/frost006.png"),image.load("images/frost007.png"),image.load("images/frost008.png")],5],[[image.load("images/frost015.png"),image.load("images/frost016.png"),image.load("images/frost017.png"),image.load("images/frost018.png"),image.load("images/frost019.png"),image.load("images/frost020.png"),image.load("images/frost021.png")],5]]
flippedFrame=Surface((0,0))
ogFrames=[0,2,4]
flipFrameOrder=[1,3,5]
for i in range(len(frames)):
    addToFrameList=[]#Frames and how fast to play them
    flipFrameList=[]#Just the frames
    workFrame=ogFrames[i]
    for j in range(len(frames[workFrame][0])):
        flippedFrame=transform.flip(frames[workFrame][0][j],True,False)
        flipFrameList.append(flippedFrame)
    addToFrameList.append(flipFrameList) 
    addToFrameList.append(frames[workFrame][1])
    frames.insert(flipFrameOrder[i],addToFrameList)
    
animation=0
idle=idleRight
jump=jumpRight
friction=0.2111
airFriction=0.02111
gravity=0.25
currentTile=0
tileSetRects=glob.glob('tileset/plat?.txt')
drawTiles=[]
tileRects=[]
tileSizes=[]
counter=0
paused=False
for i in range(len(tileSetRects)):
    tileFile=open(tileSetRects[i]).readlines()
    currentTileSize=[int(i) for i in tileFile[0].split()]
    tileSizes.append(currentTileSize)
    tileRects.append([])
    drawTiles.append(Surface((currentTileSize)))
    drawTiles[i].fill((255,255,255))
    for j in range(1,len(tileFile)):
        platInfo=tileFile[j].split()
        newPlat=[int(platInfo[i]) for i in range(4)]
        draw.rect(drawTiles[i],(0,int(platInfo[4])*255,0),newPlat)
        tileRects[i].append([Rect(newPlat),int(platInfo[4])])
screen=display.set_mode((1280,720))
running=True
playerStanding=Surface((player.W,player.H))
playerStanding.fill((255,0,0))
gameClock=time.Clock()
onGround=False
def keysDown(keys):
    global player
    if keys[K_a]:
        player.vX-=player.vAx
        player.fA=True
    if keys[K_s]:
        print("Insert Crouch Thing")
    if keys[K_d]:
        player.vX+=player.vAx
        player.fA=False
def applyFriction(mob):
    global friction
    if mob.vX>0:
        if mob.oG:
            #Friction on Ground
            mob.vX=min(mob.vX,mob.vM)
            mob.vX-=friction
        else:
            #Friction in Air
            mob.vX=min(mob.vX,mob.vM)
            mob.vX-=airFriction
    elif mob.vX<0:
        if mob.oG:
            #Friction On ground
            mob.vX=max(mob.vX,-mob.vM)
            mob.vX+=friction
        else:
            #Friction in Air
            mob.vX=max(mob.vX,-mob.vM)
            mob.vX+=airFriction
    elif mob.vX in range(1,-1):
       mob.vX=0
    return mob

def move(mob):
    mob.X+=int(mob.vX)
    mob.Y+=int(mob.vY)
    
def hitSurface(mob,tile):
    global gravity
    mobRect=Rect(mob.X,mob.Y,mob.W,mob.H)
    hitRect=[Rect(0,0,0,0)]
    wallRect=[Rect(0,0,0,0)]
    for platTile in tileRects[tile]:
        if mobRect.move(0,1).colliderect(platTile[0]) and platTile[1]==0:
            mob.vY=0
            hitRect=platTile
            if mobRect.bottom < platTile[0].bottom:
                mob.Y=platTile[0].top-mob.H
                mob.oG=True
                mob.jumps=2
            elif mobRect.top>platTile[0].top:
                mob.Y=platTile[0].bottom
                mob.vY*=-1
                mob.oG=False
        if mobRect.colliderect(platTile[0]) and platTile[1]==1:
            mob.oW=True
            wallRect=platTile
            if mobRect.left < platTile[0].left:
                mob.X=platTile[0].left-mob.W-1
                mob.jumps=1
            elif mobRect.right>platTile[0].right:
                mob.X=platTile[0].right+1
                mob.jumps=1
    if not mobRect.move(0,1).colliderect(hitRect[0]):
        mob.oG=False
        mob.vY+=gravity
    if not (mobRect.move(0,1).colliderect(wallRect[0]) or mobRect.move(0,-1).colliderect(wallRect[0])):
        mob.oW=False

def drawStuff(tileNum,keys):
    global currentFrame,frames,animation
    if keys[K_a] and player.oG:
        animation=left
    elif keys[K_d] and player.oG:
        animation=right
    elif player.fA and not player.oG:
        animation=jumpLeft
    elif not player.fA and not player.oG:
        animation=jumpRight
    elif player.fA and player.oG:
        animation=idleLeft
    elif not player.fA and player.oG:
        animation=idleRight
    #print(frames[animation][1],currentFrame,currentFrame//frames[animation][1]%len(frames[animation][0]))
    pic = frames[animation][0][currentFrame//frames[animation][1]%len(frames[animation][0])]
    currentFrame+=1
    screen.fill((0,0,0))
    screen.blit(drawTiles[tileNum],(tileSizes[tileNum][0]//2-player.X,tileSizes[tileNum][1]//2-player.Y))
    screen.blit(pic,(640,360))
def makeNewLevel(levelLength):
    levelOut=[]
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
    keysIn=key.get_pressed()
    if not paused:
        keysDown(keysIn)
        move(player)
        hitSurface(player,currentTile)
        player=applyFriction(player)
        drawStuff(currentTile,keysIn)
    display.flip()
    gameClock.tick(60)
quit()
