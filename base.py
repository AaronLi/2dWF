# Base Platformer
# TODO: Make everything shoot
from pygame import *
init()
import glob, random, pyParticle, math
def sind(deg):
    return math.sin(math.radians(deg))
def cosd(deg):
    return math.cos(math.radians(deg))

class Mob:
    def __init__(self, x, y, w, h, vX, vY, vM, vAx, fA, jumps, health = 100,shield = 100, enemyType = 0, animation = 0, weapon = 'braton'):
        self.X, self.Y = x, y
        self.W, self.H = w, h
        self.vX, self.vY = vX, vY
        self.vM, self.vAx = vM, vAx  # velocity max, acceleration
        self.oG, self.oW = False, False
        self.fA = fA  # (player.fAcing) True for right, False for left
        self.jumps = jumps
        self.frame = 0
        self.hP, self.hW = [Rect(0, 0, 0, 0), 0], [Rect(0, 0, 0, 0), 0]  # Hit Plat, Hit Wall - last floor platform the mob hit
        self.maxHealth= health#Won't be changed, only read to find the limit
        self.maxShield = shield
        
        self.health = health
        self.shield = shield
        self.shieldTimer = 300
        self.animation = animation
        self.weapon = weapon
        self.shootCounter = 0
        self.mag = 45
        #Enemy Related things
        self.enemyType = enemyType
        self.attacking = False
    def move(self):
        self.X += int(self.vX)
        self.Y += int(self.vY)

    def enemyMove(self):
        #print(self.shootCounter)
                # Moving left and right
        if player.X > self.X:
            enemyList[i].fA = True
            if not self.attacking:
                self.shootCounter = 0
                self.animation = idleRight
        elif player.X < self.X :
            enemyList[i].fA = False
            if not self.attacking:
                self.shootCounter= 0
                self.animation = idleLeft

        if abs(player.X - self.X) > 195 or not self.oG:  # Distance from player
            if player.X > self.X:
                enemyList[i].fA = True
                self.vX += self.vAx
                self.animation = right
            elif player.X < self.X:
                enemyList[i].fA = False
                self.vX -= self.vAx
                self.animation = left
            self.shootCounter= 0
        elif abs(player.X - self.X) < 190 or not self.oG:  # Distance from player
            if player.X > self.X:
                enemyList[i].fA = False
                self.vX -= self.vAx
                self.animation=left
            elif player.X < self.X:
                enemyList[i].fA = True
                self.vX += self.vAx
                self.animation=right
            self.shootCounter= 0
class Bullet:
    def __init__(self,bulletRect,direction,speed,damage):
        self.hitRect = bulletRect
        self.fA = direction
        self.vX = speed
        self.damage = damage
        self.life = 200
    def moveBullet(self):
        if self.fA:
            self.hitRect.move_ip(self.vX,0)
        else:
            self.hitRect.move_ip(-self.vX,0)
def completeFrames(frameList,ogFrames,flipFrameOrder):
    for i in range(len(frameList)):
        addToFrameList = []  # Frames and how fast to play them
        flipFrameList = []  # Just the frames
        workFrame = ogFrames[i]
        for j in range(len(frameList[workFrame][0])):
            flippedFrame = transform.flip(frameList[workFrame][0][j], True, False)
            flipFrameList.append(flippedFrame)
        addToFrameList.append(flipFrameList)
        addToFrameList.append(frameList[workFrame][1])
        frameList.insert(flipFrameOrder[i], addToFrameList)
    for i in range(len(frameList)):
        for j in range(len(frameList[i][0])):
            workFrame = frameList[i][0][j]
            frameList[i][0][j] = transform.smoothscale(workFrame,(int(workFrame.get_width() * 1.5), int(workFrame.get_height() * 1.5)))
    return frameList
hudFont=font.Font('fonts/Roboto-Light.ttf',30)
descFont = font.Font('fonts/Roboto-Light.ttf',20)
bratonShoot = mixer.Sound('sfx/weapons/corpus/bratonShoot.ogg')
deraShoot = mixer.Sound('sfx/weapons/corpus/deraShoot.ogg')
weaponList = {'braton':[ 20, 20, 45, 2, bratonShoot], 'dera':[16, 30, 30, 2, deraShoot]}#damage per shot, fire rate, mag size, reload speed, sfx
screen = display.set_mode((1280, 720))
display.set_icon(image.load('images/icon.png'))
idleRight, idleLeft, right, left, jumpRight, jumpLeft = 0, 1, 2, 3, 4, 5
player = Mob(400, 300, 33, 36, 0, 0, 4, 0.3, False, 2)
beginShieldRegen = mixer.Sound('sfx/warframes/shield/shieldRegen.ogg')
levelAtlas = image.load('images/tileTextures.png')
braton = image.load('images/weapons/corpus/braton.png')
frostUpper = image.load('images/warframes/frost/frostUpper.png')
frostArms = image.load('images/warframes/frost/frostArms.png')
frostLower = image.load('images/warframes/frost/frostLower.png')
upperSurf=Surface((22,20),SRCALPHA)
upperSurf.blit(frostUpper,(1, 0))#(380, 288))
upperSurf.blit(braton,(1+4, 0+8))#(384,296))
upperSurf.blit(frostArms, (1-1, 0+10))#(379, 298))
upperSurf = transform.smoothscale(upperSurf, (int(upperSurf.get_width()*1.5), int(upperSurf.get_height()*1.5)))
lUpperSurf = transform.flip(upperSurf, False, True)
visualOff = 0
# Animations
crewmanFrames = [[[image.load('images/enemies/crewman/crewman001.png')],1], [[image.load('images/enemies/crewman/crewman002.png'), image.load('images/enemies/crewman/crewman003.png'), image.load('images/enemies/crewman/crewman004.png'), image.load('images/enemies/crewman/crewman005.png'), image.load('images/enemies/crewman/crewman006.png'), image.load('images/enemies/crewman/crewman007.png'), image.load('images/enemies/crewman/crewman008.png'), image.load('images/enemies/crewman/crewman009.png')], 7], [[image.load('images/enemies/crewman/crewman010.png'), image.load('images/enemies/crewman/crewman011.png'), image.load('images/enemies/crewman/crewman012.png'), image.load('images/enemies/crewman/crewman013.png')], 5], [[image.load('images/enemies/crewman/crewman014.png'), image.load('images/enemies/crewman/crewman015.png'), image.load('images/enemies/crewman/crewman016.png'), image.load('images/enemies/crewman/crewman017.png'), image.load('images/enemies/crewman/crewman018.png'), image.load('images/enemies/crewman/crewman019.png'), image.load('images/enemies/crewman/crewman020.png')], 5]]
playerFrames = [[[image.load("images/warframes/frost/frost001.png")], 1], [[image.load("images/warframes/frost/frost003.png"), image.load("images/warframes/frost/frost004.png"), image.load("images/warframes/frost/frost005.png"), image.load("images/warframes/frost/frost006.png"), image.load("images/warframes/frost/frost007.png"), image.load("images/warframes/frost/frost008.png")], 7], [[image.load("images/warframes/frost/frost015.png"), image.load("images/warframes/frost/frost016.png"), image.load("images/warframes/frost/frost017.png"), image.load("images/warframes/frost/frost018.png"), image.load("images/warframes/frost/frost019.png"), image.load("images/warframes/frost/frost020.png"), image.load("images/warframes/frost/frost021.png")], 5]]
flippedFrame = Surface((0, 0))
#Player frames
print(len(playerFrames), len(crewmanFrames))
playerFrames=completeFrames(playerFrames, [0,2,4], [1,3,5])
crewmanFrames = completeFrames(crewmanFrames, [0,2, 4, 6], [1,3, 5, 7])
globalTicks = 0
partList=[]    
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
regenTimer = 0
canRegenShields = False
enemyList = [Mob(300, 400, 45, 45, 0, 0, 4, 0.3, False, 1,weapon = 'dera'), Mob(300, 400, 45, 45, 0, 0, 4, 0.4, False, 1, weapon = 'dera'),
             Mob(300, 400, 45, 45, 0, 0, 3, 0.3, False, 1, weapon = 'dera')]
bulletList = []
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
currentWeapon = 'braton'

def drawHud():
    global currentWeapon, weaponList,hudFont, screen
    angledHudSec=Surface((300,43),SRCALPHA)
    ammoHud = Surface((150,20),SRCALPHA)
    ammoCounter=descFont.render('%10s: %-3d/ %2d' % (currentWeapon, player.mag, weaponList[currentWeapon][2]),True, (255,255,255))
    healthCounter = hudFont.render(str(max(0,player.health)), True, (255,40,40))
    shieldCounter = hudFont.render(str(max(0,int(player.shield))), True, (100,170,255))
    angledHudSec.blit(healthCounter, (300-healthCounter.get_width(), 10))
    draw.line(angledHudSec,(255,40,40),(300-(math.ceil(45*(max(0,player.health)/player.maxHealth))), 42), (300, 42),3)
    angledHudSec.blit(shieldCounter, (245-shieldCounter.get_width(), 10))
    if player.shield>0:
        draw.line(angledHudSec,(100,170,255),(245-(math.ceil(45*(max(0,player.shield)/player.maxShield))), 42), (245, 42),3)
    ammoHud.blit(ammoCounter,(0,0))
    rotatedHud = transform.rotate(angledHudSec, 2)
    rotatedAmmoHud = transform.rotate(ammoHud, -2)
    screen.blit(rotatedHud,(965,2))
    screen.blit(rotatedAmmoHud, (1102, 685))
    
    
def checkBullTrajectory(bullAngle, x, y):
    hit = False
    startX,startY = x,y
    endX, endY = x, y
    retVal = None
    mx, my=mouse.get_pos()
    while not hit:
        if math.hypot(startX-x,startY-y)>=700:
            hit = True
            endX, endY = x, y
            break
        for i in playTile[2]:
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
    
    return retVal

def calcBullets():
    global regenTimer
    playerRect = Rect(player.X,player.Y,player.W,player.H)
    for i in range(len(bulletList)-1,-1,-1):
        if bulletList[i].hitRect.colliderect(playerRect):
            if player.shield != player.maxShield:
                regenTimer = 200
            if player.shield>0:
                player.shield-=bulletList[i].damage
            else:
                player.health-=bulletList[i].damage
            del bulletList[i]
        elif bulletList[i].life<=0:
            del bulletList[i]
        else:
            bulletList[i].moveBullet()
            bulletList[i].life-=1

def drawUpper(playerX, playerY):# Also includes shooting
    global upperSurf, currentWeapon
    mx, my = mouse.get_pos()
    mb = mouse.get_pressed()
    angle = math.degrees(math.atan2(mx-playerX, my-playerY))-90
    if not player.fA:
        rotUpper=transform.rotate(upperSurf,angle)
        screen.blit(rotUpper, (playerX-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2-2))
    else:
        rotUpper=transform.rotate(lUpperSurf,angle)
        screen.blit(rotUpper, (playerX-5-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2-2))
    
    if mb[0] and not player.shootCounter % int(weaponList[currentWeapon][1]) and player.mag>0:
        if len(partList)<10:
            for i in range(10):
                partList.append(pyParticle.Particle(screen, playerX+15*cosd(angle), playerY-15*sind(angle), -angle, 5, (200, random.randint(100,200), 0), 4, 0.1, 0.1,7, 2, 20))
        enemyHit = playerShoot(weaponList[currentWeapon])
        weaponList[currentWeapon][4].play()
        player.mag-=1
        if type(enemyHit) == int:
            enemyList[enemyHit].health -= weaponList[currentWeapon][1]
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
            enemyList[i].animation = 6
            if enemyInfo.frame%7 == 0:
                    del enemyList[i]
        else:          
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
                            for j in playTile[2]:
                                if j[0].collidepoint(losX,player.Y):
                                    checkLos=False
                                    break
                            if playerRect.collidepoint(losX, player.Y):
                                enemyList[i].attacking=True
                                enemyList[i].shootCounter+=1
                                if enemyInfo.fA:
                                    enemyList[i].animation = 4
                                else:
                                    enemyList[i].animation = 5
                                if enemyInfo.shootCounter % weaponList[enemyInfo.weapon][1] == 0:
                                    bulletList.append(Bullet(Rect(enemyInfo.X,enemyInfo.Y+25,10,2), enemyInfo.fA, 3, weaponList[enemyInfo.weapon][0]))
                                    weaponList[enemyInfo.weapon][4].play()
                                break
                            if player.X>enemyInfo.X:
                                losX+=3
                            elif player.X<enemyInfo.X:
                                losX-=3
                            screen.set_at((640-player.X+losX, 360), (255,0,0))
                else:
                    enemyList[i].attacking=False
        
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
        player.animation = left
    elif keys[K_d] and player.oG:
        player.animation = right
    elif player.fA and not player.oG:
        player.animation = jumpLeft
    elif not player.fA and not player.oG:
        player.animation = jumpRight
    elif player.fA and player.oG:
        player.animation = idleLeft
    elif not player.fA and player.oG:
        player.animation = idleRight
        
    pic = playerFrames[player.animation][0][player.frame // playerFrames[player.animation][1] % len(playerFrames[player.animation][0])]
    player.frame += 1
    screen.blit(tileSurf, (640 - player.X, 360 - player.Y))
    for i in bulletList:
        draw.rect(screen,(255,255,255),i.hitRect.move(640-player.X,360-player.Y))
    for i in enemyList:
        if i.enemyType == 0:
            enemyPic = crewmanFrames[i.animation][0][i.frame // crewmanFrames[i.animation][1]  % len(crewmanFrames[i.animation][0])]
            i.frame+=1
            screen.blit(transform.smoothscale(enemyPic, (i.W, i.H)), (640 - player.X + i.X, 360 - player.Y + i.Y))
    screen.blit(pic, (640, 360 + (36 - pic.get_height())))
    if not (keys[K_a] or keys[K_w] or keys[K_d] or not player.oG):
        drawUpper(660,376 + (36 - pic.get_height()))
    drawHud()
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
        pCheck=[checkPlatList[1][0][1],checkPlatList[1][0][0],checkPlatList[1][0][2],checkPlatList[1][0][3]]#Change back to original after it's been sorted
        previousPlat = [checkPlatList[0][0][1],checkPlatList[0][0][0],checkPlatList[0][0][2],checkPlatList[0][0][3]]
        
        if (previousPlat[0]+previousPlat[2] == pCheck[0] or Rect(previousPlat).colliderect(pCheck)) and previousPlat[3] == pCheck[3] and pCheck[1] == previousPlat[1]:
                unionedRect=Rect(previousPlat).union(Rect(pCheck))
                checkPlatList.insert(2,[[unionedRect[1],unionedRect[0],unionedRect[2],unionedRect[3]],0])#Change back into height prioritized format
                del checkPlatList[0]
                del checkPlatList[0]
        else:
            if [Rect(pCheck),0] not in levelOut and Rect(pCheck).collidelist(rectOuts)==-1:
                levelOut.append([Rect(previousPlat),0])
                rectOuts.append(Rect(previousPlat))
            del checkPlatList[0]
    levelOut.insert(0, (xOff, tileH))
    return levelOut

def playerShoot(weapon):
    mx, my = mouse.get_pos()
    angle = math.degrees(math.atan2(mx-640, my-360))-90+random.randint(-1,1)
    return checkBullTrajectory(angle, player.X, player.Y+20)
def fixLevel(levelIn): #Moves the level so that it isn't outside of the bounding box
    global visualOff
    #print(len(levelIn))
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
            if e.key==K_ESCAPE:
                running=False
            if e.key == K_r:
                player.mag = weaponList[currentWeapon][2]
            if e.key == K_t:
                currentWeapon = 'dera'
            if e.key == K_y:
                currentWeapon = 'braton'
        if e.type == MOUSEBUTTONDOWN:
            #print(e.button)
            if e.button == 1:
                shooting = True
                player.shootCounter = 0
        if e.type == MOUSEBUTTONUP:
            if e.button == 1:
                shooting = False
    screen.fill((0, 0, 0))                
    display.set_caption(str(int(gameClock.get_fps())) + " - Dev Build")
    keysIn = key.get_pressed()
    if not paused:
        keysDown(keysIn)
        player.move()
        hitSurface(player, playTile[2])
        player = applyFriction(player)
        enemyLogic()
        for i in range(len(enemyList)):
            enemyList[i].move()
            enemyList[i].enemyMove()
            hitSurface(enemyList[i], playTile[2])
            enemyList[i] = applyFriction(enemyList[i])
        canRegenShields = player.shield < player.maxShield
        calcBullets()
        #Shield regen and sfx
        if int(player.shield) == 0 and regenTimer == 0:
            beginShieldRegen.play()
        if canRegenShields and regenTimer == 0:
            player.shield += 0.3
        if shooting:
            player.shootCounter += 1
        regenTimer = max(0,regenTimer-1)

    drawStuff(playTile[1], playTile[0], keysIn)
    display.flip()
    gameClock.tick(60)
quit()
print('cya')
