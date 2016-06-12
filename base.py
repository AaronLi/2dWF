# Base Platformer
# TODO: Multiple platforms put together
# TODO: Make everything shoot
# Have a master platform list that contains all platforms with preoffset platforms in them?
# Stitch together all platform visuals?
from pygame import *
mixer.init()
import glob, random, pyParticle, math
def sind(deg):
    return math.sin(math.radians(deg))
def cosd(deg):
    return math.cos(math.radians(deg))

class Mob:
    def __init__(self, x, y, w, h, vX, vY, vM, vAx, fA, jumps, health = 100):
        self.X, self.Y = x, y
        self.W, self.H = w, h
        self.vX, self.vY = vX, vY
        self.vM, self.vAx = vM, vAx  # velocity max, acceleration
        self.oG, self.oW = False, False
        self.fA = fA  # (player.fAcing) True for right, False for left
        self.jumps = jumps
        self.frame = 0
        self.hP, self.hW = [Rect(0, 0, 0, 0), 0], [Rect(0, 0, 0, 0), 0]  # Hit Plat, Hit Wall - last floor platform the mob hit
        self.health = health
    def move(self):
        self.X += int(self.vX)
        self.Y += int(self.vY)

    def enemyMove(self):
                # Moving left and right
        if player.X > self.X:
            enemyList[i].fA = True
        elif player.X < self.X:
            enemyList[i].fA = False

        if abs(player.X - self.X) > 195 or not self.oG:  # Distance from player
            if player.X > self.X:
                enemyList[i].fA = True
                self.vX += self.vAx
            elif player.X < self.X:
                enemyList[i].fA = False
                self.vX -= self.vAx
        elif abs(player.X - self.X) < 190 or not self.oG:  # Distance from player
            if player.X > self.X:
                enemyList[i].fA = False
                self.vX -= self.vAx
            elif player.X < self.X:
                enemyList[i].fA = True
                self.vX += self.vAx
bratonShoot = mixer.Sound('sfx/bratonShoot.ogg')
weaponList = [['braton', 20, 20, 45, 2, bratonShoot]]#name, damage per shot, rounds per second, mag size, reload speed, sfx
screen = display.set_mode((1280, 720))
display.set_icon(image.load('images/icon.png'))
idleRight, idleLeft, right, left, jumpRight, jumpLeft = 0, 1, 2, 3, 4, 5
player = Mob(400, 300, 33, 36, 0, 0, 4, 0.3, False, 2)
player.frame = 0
levelAtlas = image.load('images/tileTextures.png')
braton = image.load('images/braton.png')
frostUpper = image.load('images/frostUpper.png')
frostArms = image.load('images/frostArms.png')
frostLower = image.load('images/frostLower.png')
upperSurf=Surface((22,20),SRCALPHA)
upperSurf.blit(frostUpper,(1, 0))#(380, 288))
upperSurf.blit(braton,(1+4, 0+8))#(384,296))
upperSurf.blit(frostArms, (1-1, 0+10))#(379, 298))
upperSurf = transform.smoothscale(upperSurf, (int(upperSurf.get_width()*1.5), int(upperSurf.get_height()*1.5)))
lUpperSurf = transform.flip(upperSurf, False, True)
visualOff = 0
# Animations
praiseCube = image.load("images/cubeLove.png")
playerFrames = [[[image.load("images/frost001.png")], 1], [[image.load("images/frost003.png"), image.load("images/frost004.png"), image.load("images/frost005.png"), image.load("images/frost006.png"), image.load("images/frost007.png"), image.load("images/frost008.png")], 7], [[image.load("images/frost015.png"), image.load("images/frost016.png"), image.load("images/frost017.png"), image.load("images/frost018.png"), image.load("images/frost019.png"), image.load("images/frost020.png"), image.load("images/frost021.png")], 5]]
flippedFrame = Surface((0, 0))
ogFrames = [0, 2, 4]
flipFrameOrder = [1, 3, 5]
for i in range(len(playerFrames)):
    addToFrameList = []  # Frames and how fast to play them
    flipFrameList = []  # Just the frames
    workFrame = ogFrames[i]
    for j in range(len(playerFrames[workFrame][0])):
        flippedFrame = transform.flip(playerFrames[workFrame][0][j], True, False)
        flipFrameList.append(flippedFrame)
    addToFrameList.append(flipFrameList)
    addToFrameList.append(playerFrames[workFrame][1])
    playerFrames.insert(flipFrameOrder[i], addToFrameList)
for i in range(len(playerFrames)):
    for j in range(len(playerFrames[i][0])):
        workFrame = playerFrames[i][0][j]
        playerFrames[i][0][j] = transform.smoothscale(workFrame,(int(workFrame.get_width() * 1.5), int(workFrame.get_height() * 1.5)))
globalTicks = 0
partList=[]    
animation = 0
idle = idleRight
jump = jumpRight
friction = 0.2111
airFriction = 0.02111
gravity = 0.25
currentTile = 0
tileSetRects = glob.glob('tileset/plat?.txt')
drawTiles = []
tileRects = []
tileSizes = []
tileIO = []
counter = 0
shooting = False
paused = False
enemyList = [Mob(300, 400, 50, 50, 0, 0, 4, 0.3, False, 1), Mob(300, 400, 60, 60, 0, 0, 4, 0.4, False, 1),
             Mob(300, 400, 40, 40, 0, 0, 3, 0.3, False, 1)]
# Getting information from the level files
for i in range(len(tileSetRects)):
    tileFile = open(tileSetRects[i]).readlines()
    currentTileSize = [int(i) for i in tileFile[0].split()[0:2]]
    tileEntrance = tileFile[0].split()[2]
    tileExit = tileFile[0].split()[3]
    tileIO.append([tileEntrance, tileExit])
    tileSizes.append(currentTileSize)
    tileRects.append([])
    drawTiles.append(Surface((currentTileSize)))
    drawTiles[i].fill((255, 255, 255))
    for j in range(1, len(tileFile)):
        platInfo = tileFile[j].split()
        newPlat = [int(platInfo[i]) for i in range(4)]
        draw.rect(drawTiles[i], (0, 0, 0), newPlat)
        tileRects[i].append([Rect(newPlat), int(platInfo[4])])
running = True
playerStanding = Surface((player.W, player.H))
playerStanding.fill((255, 0, 0))
gameClock = time.Clock()
onGround = False
currentWeapon = 0
def checkBullTrajectory(bullAngle, x, y):
    hit = False
    startX,startY = x,y
    endX, endY = x, y
    retVal = None
    mx, my=mouse.get_pos()
    while not hit:
        #print(bullAngle)
        if math.hypot(startX-x,startY-y)>=700:
            hit = True
            endX, endY = x, y
            break
        for i in playTile[2]:
            #print(i)
            if i[0].collidepoint(x, y):
                hit = True
                endX, endY = x,y
                retVal = None
        for i in range(len(enemyList)):
            eInfo=enemyList[i]
            mobRect=Rect(eInfo.X,eInfo.Y,eInfo.W,eInfo.H)
            if mobRect.collidepoint(x,y):
                hit = True
                endX, endY = x, y
                retVal = i
        x+=cosd(bullAngle)
        y+=sind(-bullAngle)
    shotDistance = math.hypot(startX-endX, startY-endY)
    #draw.line(screen,(155,100,0), (655+10*cosd(bullAngle),375-10*sind(bullAngle)), (655+shotDistance*cosd(bullAngle),375-shotDistance*sind(bullAngle)))
    #display.flip()
    #time.wait(50)
    #screen.set_at((int(player.X+10*cosd(bullAngle)+x), int(player.Y-10*sind(bullAngle)+y)),(0,0,0))
    #display.flip()
    return retVal
def drawUpper(playerX, playerY):
    global upperSurf, currentWeapon, shootClock
    mx, my = mouse.get_pos()
    mb = mouse.get_pressed()
    angle = math.degrees(math.atan2(mx-playerX, my-playerY))-90
    #screen.blit(frostLower, (playerX-12, playerY+4))#(376, 299))
    if not player.fA:
        rotUpper=transform.rotate(upperSurf,angle)
        screen.blit(rotUpper, (playerX-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2-2))
    else:
        rotUpper=transform.rotate(lUpperSurf,angle)
        screen.blit(rotUpper, (playerX-5-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2-2))
    
    #print(globalTicks % weaponList[currentWeapon][2])
    if mb[0] and not shootClock % int(weaponList[currentWeapon][2]):
        if len(partList)<10:
            for i in range(10):
                partList.append(pyParticle.Particle(screen, playerX+15*cosd(angle), playerY-15*sind(angle), -angle, 5, (200, random.randint(100,200), 0), 4, 0.1, 0.1,7, 2, 20))
        enemyHit = playerShoot(weaponList[currentWeapon])
        weaponList[currentWeapon][5].play()
        if type(enemyHit) == int:
            enemyList[enemyHit].health -= weaponList[currentWeapon][1]
            print(enemyList[enemyHit].health)
        #draw.line(screen,(155,100,0), (playerX+10*cosd(angle), playerY-10*sind(angle)), (playerX+5000*cosd(angle), playerY-5000*sind(angle)))
    for i in range(len(partList)-1,-1,-1):
        partList[i].moveParticle()
        if not partList[i].live:
            del partList[i]
    player.fA =-270 < angle < -90
    
def enemyLogic():
    global enemyList
    for i in range(len(enemyList)-1,-1,-1):
        enemyInfo = enemyList[i]
        enemyRect = Rect(enemyInfo.X, enemyInfo.Y, enemyInfo.W, enemyInfo.H)
        playerRect = Rect(player.X, player.Y, player.W, player.H)
        losX = enemyInfo.X #line of sight x for checking whether you can shoot or not
        checkLos=True
        #Checking health
        if enemyInfo.health<=0:
            del enemyList[i]
            
        # Jumping over obstacles
        if enemyInfo.oW and enemyInfo.oG:
            enemyList[i].jumps -= 1
            enemyList[i].vY -= 7

        # Jumping across gaps
        if enemyInfo.fA:
            if (not enemyRect.move(int(enemyInfo.vM), 1).colliderect(enemyInfo.hP[0])) and enemyInfo.oG:
                enemyList[i].vY -= 7
        elif not enemyInfo.fA:
            if (not enemyRect.move(-int(enemyInfo.vM), 1).colliderect(enemyInfo.hP[0])) and enemyInfo.oG:
                enemyList[i].vY -= 7

        # Shooting
        if abs(enemyInfo.X-player.X) in range(190, 200):
            if abs(enemyInfo.Y - player.Y) <30 and int(enemyInfo.vX) == 0:
                    while checkLos:
                        for i in playTile[2]:
                            if i[0].collidepoint(losX,player.Y):
                                checkLos=False
                                break
                        if playerRect.collidepoint(losX, player.Y):
                            break
                        if player.X>enemyInfo.X:
                            losX+=3
                        elif player.X<enemyInfo.X:
                            losX-=3
                        screen.set_at((640-player.X+losX, 360), (255,0,0))
def makeTile(tileInfo):
    global levelAtlas
    tileSize = tileInfo.pop(0)
    tileVisual = Surface(tileSize,SRCALPHA)
    #tileVisual.fill((255, 255, 255))
    for i in tileInfo:
        if i[1] !=2:
            draw.rect(tileVisual, (0, 0, 0), i[0])
            tileVisual.blit(levelAtlas, i[0].topleft,(0,0,16,16))
            tileVisual.blit(levelAtlas, i[0].move(-16,0).topright, (32,32,16,16))
            tileVisual.blit(levelAtlas, i[0].move(0,-16).bottomleft, (16,64,16,16))
            tileVisual.blit(levelAtlas, i[0].move(-16,-16).bottomright, (80,32,16,16))
            if i[0].width>32:
                for j in range(16,i[0].width-16,16):
                    tileVisual.blit(levelAtlas,(i[0].left+j,i[0].top),(16,112,16,16))
                    tileVisual.blit(levelAtlas,(i[0].left+j,i[0].bottom-16),(48,128,16,16))
            if i[0].height >32:
                for j in range(16,i[0].height-16,16):
                    tileVisual.blit(levelAtlas, (i[0].left,i[0].top+j), (128,32,16,16))
                    tileVisual.blit(levelAtlas, (i[0].move(-16,0).right,i[0].top+j), (0,16,16,16))
    return (tileSize, tileVisual, tileInfo)


def keysDown(keys):
    global player
    mx, my = mouse.get_pos()
    mb=mouse.get_pressed()
    if keys[K_a]:
        player.vX -= player.vAx
        player.fA = True
    if keys[K_w] and player.oW:
        player.vY = max(-4, player.vY - 0.5)
    if keys[K_s]:
        print("Insert Crouch Thing")
    if keys[K_d]:
        player.vX += player.vAx
        player.fA = False

def applyFriction(mob):
    global friction
    if mob.vX > 0:
        if mob.oG:
            # Friction on Ground
            mob.vX = min(mob.vX, mob.vM)
            mob.vX -= friction
        else:
            # Friction in Air
            mob.vX = min(mob.vX, mob.vM)
            mob.vX -= airFriction
    elif mob.vX < 0:
        if mob.oG:
            # Friction On ground
            mob.vX = max(mob.vX, -mob.vM)
            mob.vX += friction
        else:
            # Friction in Air
            mob.vX = max(mob.vX, -mob.vM)
            mob.vX += airFriction
    elif mob.vX in range(1, -1):
        mob.vX = 0
    return mob


def hitSurface(mob, tilePlats):
    global gravity
    mobRect = Rect(mob.X, mob.Y, mob.W, mob.H)
    hitRect = [Rect(0, 0, 0, 0)]
    wallRect = [Rect(0, 0, 0, 0)]
    for platTile in tilePlats:
        if mobRect.move(0, 1).colliderect(Rect(platTile[0])) and (platTile[1] == 0 or platTile[1] == 2):
            mob.vY = 0
            mob.hP = platTile
            if mobRect.bottom < platTile[0].bottom:
                mob.Y = platTile[0].top - mob.H
                mob.oG = True
                mob.jumps = 2
            elif mobRect.top > platTile[0].top:
                mob.Y = platTile[0].bottom
                mob.vY *= -1
                mob.oG = False
        if mobRect.colliderect(platTile[0]) and platTile[1] == 1:
            mob.oW = True
            mob.hW = platTile
            if mobRect.left < platTile[0].left:
                mob.X = platTile[0].left - mob.W - 1
                mob.jumps = 1
            elif mobRect.right > platTile[0].right:
                mob.X = platTile[0].right + 1
                mob.jumps = 1
    if not mobRect.move(0, 1).colliderect(mob.hP[0]):
        mob.oG = False
        mob.vY += gravity
    if not (mobRect.move(0, 1).colliderect(mob.hW[0]) or mobRect.move(0, -1).colliderect(mob.hW[0])):
        mob.oW = False


def drawStuff(tileSurf, tileSize, keys):
    global player, frames, animation, visualOff
    if keys[K_a] and player.oG:
        animation = left
    elif keys[K_d] and player.oG:
        animation = right
    elif player.fA and not player.oG:
        animation = jumpLeft
    elif not player.fA and not player.oG:
        animation = jumpRight
    elif player.fA and player.oG:
        animation = idleLeft
    elif not player.fA and player.oG:
        animation = idleRight
    pic = playerFrames[animation][0][player.frame // playerFrames[animation][1] % len(playerFrames[animation][0])]
    player.frame += 1
    screen.fill((0, 0, 0))
    screen.blit(tileSurf, (640 - player.X, 360 - player.Y))
    for i in enemyList:
        screen.blit(transform.smoothscale(praiseCube, (i.W, i.H)), (640 - player.X + i.X, 360 - player.Y + i.Y))
    screen.blit(pic, (640, 360 + (36 - pic.get_height())))
    if not (keys[K_a] or keys[K_w] or keys[K_d] or not player.oG):
        drawUpper(660,376 + (36 - pic.get_height()))

def makeNewLevel(levelLength):
    levelOut = []
    tileH = 0
    levelSeq = [0,0]
    for i in range(levelLength):
        levelSeq.append(random.randint(0, len(drawTiles) - 1))
    xOff, yOff = 0, 0
    checkPlatList = []
    sameRect = []
    stitchedLevel=[]
    rectOuts=[]
    for i in range(len(levelSeq)):
        tileEnter = int(tileIO[levelSeq[i]][0])
        lastTileExit = int(tileIO[levelSeq[i-1]][1])
        yOff += lastTileExit-tileEnter
        for plat in tileRects[levelSeq[i]]:
            stitchedLevel.append([plat[0].move(xOff, yOff), plat[1]])
        xOff += tileSizes[levelSeq[i]][0]
        tileH += tileSizes[levelSeq[i]][1]
        # Placing rects together
        for i in stitchedLevel:
            if i[1] == 0 or i[1] == 2:
                checkPlatList.append([[i[0][1],i[0][0],i[0][2],i[0][3]],i[1]])#Because adjacent tiles should have same height first
            else:
                levelOut.append(i)
        checkPlatList.sort()
    while len(checkPlatList)>1:
        #print(len(checkPlatList))
        pCheck=[checkPlatList[1][0][1],checkPlatList[1][0][0],checkPlatList[1][0][2],checkPlatList[1][0][3]]
        previousPlat = [checkPlatList[0][0][1],checkPlatList[0][0][0],checkPlatList[0][0][2],checkPlatList[0][0][3]]
        
        if previousPlat[0]+previousPlat[2] == pCheck[0] and previousPlat[3] == pCheck[3] and pCheck[1] == previousPlat[1]:
                print('join',previousPlat,pCheck)
                levelOut.append([Rect(previousPlat).union(Rect(pCheck)),0])
                rectOuts.append(Rect(previousPlat).union(Rect(pCheck)))
                del checkPlatList[0]
                del checkPlatList[0]
        else:
            if [Rect(pCheck),0] not in levelOut and Rect(pCheck).collidelist(rectOuts)==-1:
                print('added')
                levelOut.append([Rect(previousPlat),0])
                rectOuts.append(Rect(previousPlat))
            del checkPlatList[0]
        print(len(checkPlatList))
    levelOut.insert(0, (xOff, tileH))
    return levelOut

def playerShoot(weapon):
    mx, my = mouse.get_pos()
    angle = math.degrees(math.atan2(mx-640, my-360))-90+random.randint(-1,1)
    return checkBullTrajectory(angle, player.X, player.Y+20)
def fixLevel(levelIn): #Moves the level so that it isn't outside of the bounding box
    global visualOff
    print(len(levelIn))
    platHeights=[]
    platRectList=[]
    platTypes=[]
    newTile=[levelIn.pop(0)]
    finalRects=[]
    for i in levelIn:
        #print(i)
        platHeights.append(i[0].top)
        platRectList.append(Rect(i[0]))
        platTypes.append(i[1])
    visualOff = min(platHeights)
##    print(len(platRectList))
##    for i in platRectList:
##        collidedRects = i.collidelistall(platRectList)
##        print(collidedRects)
##        if len(collidedRects)>0:
##            for i in range(len(collidedRects)-1,-1,-1):
##                del platRectList[collidedRects[i]]
##    print(len(platRectList))
    print(len(levelIn))
    for i in levelIn:
        newTile.append([i[0].move(0,-min(platHeights)+640),i[1]])
    return newTile
playTile = makeTile(fixLevel(makeNewLevel(10)))
#player.Y = visualOff
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
            if e.key == K_w and player.jumps > 0:
                player.vY = -7
                # player.oG=False
                player.jumps -= 1
            if e.key == K_p:
                if paused:
                    paused = False
                elif not paused:
                    paused = True
            if e.key==K_c:
                if len(enemyList)>0:
                    del enemyList[-1]
        if e.type == MOUSEBUTTONDOWN:
            #print(e.button)
            if e.button == 1:
                shooting = True
                shootClock = 0
        if e.type == MOUSEBUTTONUP:
            if e.button == 1:
                shooting = False
    display.set_caption(str(int(gameClock.get_fps())) + " - Dev Build")
    keysIn = key.get_pressed()
    #print(player.hP)
    if not paused:
        keysDown(keysIn)
        player.move()
        hitSurface(player, playTile[2])
        player = applyFriction(player)
        drawStuff(playTile[1], playTile[0], keysIn)
        enemyLogic()
        for i in range(len(enemyList)):
            enemyList[i].move()
            enemyList[i].enemyMove()
            hitSurface(enemyList[i], playTile[2])
            enemyList[i] = applyFriction(enemyList[i])
    if shooting:
        shootClock += 1
    display.flip()
    gameClock.tick(60)
quit()
print('cya')
