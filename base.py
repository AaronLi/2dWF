# Base Platformer
from pygame import *
init()
import glob, random, math
def sind(deg):
    return math.sin(math.radians(deg))
def cosd(deg):
    return math.cos(math.radians(deg))
class Particle:#Class used for simulating particles (Guns, 'blood', bullet hits)
    def __init__(self,surface,x,y,rotation, lifetime, colour, speed, gravity, airResistance,fadeRate, length=1, variation = 10):
        colourOff=random.randint(0,255-max(colour))
        self.surf=surface
        self.X, self.Y=x,y#position
        self.rot=rotation+random.randint(-variation,variation)#direction
        self.life=lifetime#amount of iterations before it disappears
        self.col=(colour[0]+colourOff, colour[1]+colourOff, colour[2]+colourOff)
        self.speed = speed#distance it moevs per iteration
        self.fG = gravity#amount it's Y is affected per iteration
        self.aR = airResistance#amount it's X is affected per iteration
        self.fR = fadeRate#Amount it's colour fades per iteration
        self.live = True
        self.length = length#Length of particle tail
        
    def moveParticle(self):#Move the particle based on it's speed and remove it if it's dead
        if self.live:
            draw.line(self.surf, self.col, (640-player.X+int(self.X), 360-player.Y+int(self.Y)), (640-player.X+int(self.X-self.length*cosd(self.rot)), 360-player.Y+int(self.Y-self.length*sind(self.rot))))
            self.X+=self.speed*cosd(self.rot)
            self.Y+=self.speed*sind(self.rot)
            self.col=(max(self.col[0]-self.fR, 0), max(self.col[1]-self.fR, 0), max(self.col[2]-self.fR, 0))
            self.life-=1
            self.speed=max(self.speed-self.aR, 0)
            self.Y=max(self.Y+self.fG, 0)
        if self.life <= 0:
            self.live = False

class Mob:#Class used for the player and enemies
    def __init__(self, x, y, w, h, vX, vY, vM, vAx, fA, jumps, health = 100,shield = 100, enemyType = 0, animation = 0, weapon = 'braton',avoidance = 50,shootRange = 200):
        self.X, self.Y = x, y
        self.W, self.H = w, h
        self.vX, self.vY = vX, vY
        self.vM, self.vAx = vM, vAx  # max velocity for mob to travel at, acceleration rate to the max
        self.oG, self.oW = False, False#whether the mob is on the ground/floor, whether the mob is on a wall
        self.fA = fA  # (player.fAcing) True for right, False for left
        self.jumps = jumps#amount of jumps the mob has left
        self.frame = 0#Current frame the mob is on
        self.hP, self.hW = [Rect(0, 0, 0, 0), 0], [Rect(0, 0, 0, 0), 0]  # Hit Plat, Hit Wall - last floor platform the mob hit
        self.maxHealth= health#Won't be changed, only read to find the limit
        self.maxShield = shield#same as maxHealth
        self.money = 0#Credits, for purchasing weapons
        
        self.health = health#current Health
        self.shield = shield#current shields
        
        self.shieldTimer = 300#Time until shield begins regenerating
        self.animation = animation#current frame set the mob is on
        self.weapon = weapon#current weapon the mob is using (Used more with enemies)
        self.shootCooldown = 0#Fire rate timer
        self.mag = 45#Current magazine size, changes with weapon
        self.reloading = 0#Reload timer
        self.reserveAmmo = [500,200,2500,60] #Rifle Ammo, Shotgun Ammo, laser Ammo, sniperAmmo
        #Enemy Related things
        self.enemyType = enemyType
        self.attacking = False
        self.dying=0#0 if alive >0 if not alive
        self.avoidance=avoidance#How close the player can be
        self.shootRange = shootRange#How far the mob tries to stay
        self.shootCounter = 0#Enemy fire rate timer
    def move(self):
        self.X += int(self.vX)
        self.Y += int(self.vY)

    def enemyMove(self):
                # Moving left and right
        if self.animation !=6:#Won't work if mob is currently dying
            if player.X > self.X:#face right if player is on right
                enemyList[i].fA = True
                if not self.attacking:#use standing animation if not attacking
                    self.shootCounter = 0
                    self.animation = idleRight
            elif player.X < self.X :#Face left is player is on left
                enemyList[i].fA = False
                if not self.attacking:
                    self.shootCounter= 0
                    self.animation = idleLeft

            if abs(player.X - self.X) > self.shootRange or not self.oG:  # Move towards player if not on ground or if outside of shooting range
                if player.X > self.X:#begin walking to the right
                    enemyList[i].fA = True
                    self.vX += self.vAx
                    self.animation = right
                elif player.X < self.X:#begin walking to the left
                    enemyList[i].fA = False
                    self.vX -= self.vAx
                    self.animation = left
                self.shootCounter= 0
            elif abs(player.X - self.X) < self.avoidance or not self.oG:  # Move away from player if not on ground or inside avoidance area
                if player.X > self.X:#Move left
                    enemyList[i].fA = False
                    self.vX -= self.vAx
                    self.animation=left
                elif player.X < self.X:#Move right
                    enemyList[i].fA = True
                    self.vX += self.vAx
                    self.animation=right
                self.shootCounter= 0
class Pickup:#Class for ammo, health, and credit drops
    def __init__(self,x,y,dropType,amount):
        self.X=x
        self.Y=y
        self.vY=0
        self.dropType=dropType#an int that describes what kind of ammo the drop is
        self.amount=amount#int for ammo amount, string if credits or health
    def fallToGround(self):
        canFall = True
        for i in playTile[2]:
            if i[0].colliderect(Rect(self.X,self.Y,16,16).move(0,1)):#if pickup is hitting any platform in the level
                self.Y = i[0].top-pickupSprites[self.dropType].get_height()
                self.vY = 0
                canFall = False
                break
        if canFall:
            self.vY+=0.5
            self.Y+=int(self.vY)
    def checkCollide(self):#Checks if player is colliding with the pickup
        if Rect(self.X,self.Y,16,16).colliderect(Rect(player.X,player.Y,player.W,player.H)):#if colliding
            if type(self.amount) == int:#if the drop is ammo
                player.reserveAmmo[self.dropType]+=self.amount#add ammo to respective reserve
                ammoPickup.play()
                return True
            elif self.amount == 'health' and player.health<player.maxHealth:#if the drop is health and the player isn't at max health
                healthPickup.play()
                player.health=min(player.maxHealth,player.health+25)#add health
                return True
            elif self.amount == 'credits':#if the drop is credits
                player.money += 50*random.randint(100,200)#Add a random amount of credits
                return True
        return False
def flipFrames(frameList):#Reflects the sprites in a spritelist if they're all facing the wrong direction
    flippedList=[]#output
    for i in range(len(frameList)):
        flippedList.append([])#Create a new list in the output
        flippedList[-1].append([])#Create a new list in the new list
        for j in frameList[i][0]:
           flippedList[i][0].append(transform.flip(j,True,False))#append to the new list the flipped frame
        flippedList[i].append(frameList[i][1])#Append the rate at which the frames should be played
    return flippedList
class Bullet:#Enemy bullets
    def __init__(self,bulletRect,direction,speed,damage,colour,faction = 0):#0 is enemy, 1 is friendly
        self.hitRect = bulletRect
        self.fA = direction
        self.vX = speed
        self.damage = damage
        self.life = 400#Iterations before it is deleted
        self.faction = faction#0 will hit the player, 1 will hit enemies
        self.colour = colour
    def moveBullet(self):#Move a bullet
        if self.fA:
            self.hitRect.move_ip(self.vX,0)
        else:
            self.hitRect.move_ip(-self.vX,0)
def completeFrames(frameList,ogFrames,flipFrameOrder):#will return a list of frames that contains the frames and their reflected form for use
    for i in range(len(frameList)):
        #frameList is the actual frames
        #ogFrames is the positions of the old frames
        #flipFrame Order is the positions of the new frames
        addToFrameList = []  # Frames and how fast to play them
        flipFrameList = []  # the flipped frames in the current animation set
        workFrame = ogFrames[i]#the frame
        for j in range(len(frameList[workFrame][0])):
            flippedFrame = transform.flip(frameList[workFrame][0][j], True, False)
            flipFrameList.append(flippedFrame)
        addToFrameList.append(flipFrameList)#prepare the flipped frames to output
        addToFrameList.append(frameList[workFrame][1])
        frameList.insert(flipFrameOrder[i], addToFrameList)
    for i in range(len(frameList)):
        for j in range(len(frameList[i][0])):
            workFrame = frameList[i][0][j]
            frameList[i][0][j] = transform.smoothscale(workFrame,(int(workFrame.get_width() * 1.5), int(workFrame.get_height() * 1.5))).convert_alpha()#go through framelist scaling everything up 1.5x
    return frameList

def swordHit():#check for sword hits
    global playerRect
    swingBox = Rect(player.X, player.Y, 40,player.H)#sword area
    for i in enemyList:
        enemyRect = Rect(i.X,i.Y,i.W,i.H)#enemy area
        #Swing
        if player.fA:#if player is facing left
            if enemyRect.colliderect(swingBox.move(-swingBox.w,0)):#if enemy is colliding with the sword
                i.health -=50
                break
        elif not player.fA:#if player is facing right
            if enemyRect.colliderect(swingBox.move(player.W,0)):
                i.health -=50
                break
    #reflecting bullets
    for i in bulletList:#go through list of enemy bullets
        if player.fA:#if player is facing left
            if i.hitRect.colliderect(swingBox.move(-swingBox.w,0)):#check if bullet is hitting sword
                i.fA = not player.fA#changes direction to player's
                i.faction = 1#change bullet into player's bullet
                break
        elif not player.fA:
            if i.hitRect.colliderect(swingBox.move(player.W,0)):
                i.fA = not player.fA
                i.faction = 1
                break
def drawUpperSprite():#creates a new surface for when the player is standing around and aiming
    global currentWeapon, upperSurf, lUpperSurf
    upperSurf=Surface((22,20),SRCALPHA)
    upperSurf.blit(frostUpper,(1, 0))#regular upper half of body
    upperSurf.blit(eval(currentWeapon),(5, 8))#weapon
    upperSurf.blit(frostArms, (0, 10))#arms
    upperSurf = transform.smoothscale(upperSurf, (int(upperSurf.get_width()*1.5), int(upperSurf.get_height()*1.5)))#scale it all up
    lUpperSurf = transform.flip(upperSurf, False, True)#left version
def miniMap():#draws minimap in top left of hud
    mMapSurf=Surface((200,100),SRCALPHA)
    mMapSurf.fill((255,255,255))#fill with white
    mMapSurf.blit(minimap,(100-player.X//7,50-player.Y//7))#blit scaled down tile
    mMapSurf = transform.rotate(mMapSurf, -1)#tilt it so it looks like the warframe minimap

    screen.blit(mMapSurf,(5,5))
def drawHud():#Draw hud, credits, health, shields, minimap, ammo
    global currentWeapon, weaponList,hudFont, screen
    angledHudSec=Surface((300,43),SRCALPHA)
    ammoHud = Surface((165,25),SRCALPHA)
    creditHud = Surface((200,25),SRCALPHA)
    creditDisplay = descFont.render(str(player.money),True,(255,255,255))#render current money
    ammoCounter=descFont.render('%10s: %-3d/ %2d' % (currentWeapon, player.mag, player.reserveAmmo[weaponList[currentWeapon][9]]),True, (255,255,255))#render current ammo / ammo reserve
    healthCounter = hudFont.render(str(max(0,player.health)), True, (255,40,40))#render health
    shieldCounter = hudFont.render(str(max(0,int(player.shield))), True, (100,170,255))#render shields
    angledHudSec.blit(healthCounter, (300-healthCounter.get_width(), 10))
    creditHud.blit(hudCredit, (0,5))
    creditHud.blit(creditDisplay, (20,0))
    draw.line(angledHudSec,(255,40,40),(300-(math.ceil(45*(max(0,player.health)/player.maxHealth))), 42), (300, 42),3)#draw line for player health
    angledHudSec.blit(shieldCounter, (245-shieldCounter.get_width(), 10))
    if player.shield>0:#don't show player shields bar if they're at 0
        draw.line(angledHudSec,(100,170,255),(245-(math.ceil(45*(max(0,player.shield)/player.maxShield))), 42), (245, 42),3)#draw line for player shields
    ammoHud.blit(ammoCounter,(0,0))
    rotatedCreditHud = transform.rotate(creditHud,-2)#rotate so it looks like warframe hud
    rotatedHud = transform.rotate(angledHudSec, 2)
    rotatedAmmoHud = transform.rotate(ammoHud, -2)
    screen.blit(rotatedHud,(965,2))
    screen.blit(rotatedCreditHud,(10,690))
    screen.blit(rotatedAmmoHud, (1270-rotatedAmmoHud.get_width(), 685))
    miniMap()
    
def checkBullTrajectory(bullAngle, x, y):#check trajectory of player shots
    #bullAngle is the angle of the bullet
    #x, y is the position the player is at
    global particleList
    hit = False
    startX,startY = x,y
    endX, endY = x, y
    retVal = None
    mx, my=mouse.get_pos()
    while not hit:#loop while the bullet hasn't reached anything
        if math.hypot(startX-x,startY-y)>=900:#if bullet has checked 900 pixels distance
            hit = True
            endX, endY = x, y
            break
        for i in playTile[2]:#if bullet hits environment
            if i[0].collidepoint(x, y) and i[1] != 3:
                hit = True
                endX, endY = x,y
                for i in range(5):#make particles on the environment at the hit location
                    particleList.append(Particle(screen, endX,endY,180+bullAngle, 5, weaponList[currentWeapon][5], 4, 0.2, 0.2, 0.4, 1, 10))
                retVal = None
        for i in range(len(enemyList)):#if bullet hits enemy
            eInfo=enemyList[i]
            mobRect=Rect(eInfo.X,eInfo.Y,eInfo.W,eInfo.H)#enemy hitbox
            if mobRect.collidepoint(x,y) and eInfo.dying == 0:#if it hits an enemy that isn't dying
                hit = True
                endX, endY = x, y
                retVal = i
                for i in range(5):#add particles for BLOOD
                    particleList.append(Particle(screen, endX, endY,bullAngle+180, 20, [255,0,0], 3, 1, 0.2, 0, 1, 10))
        x+=7*cosd(bullAngle)#move bullet checking coordinates
        y+=7*sind(-bullAngle)
    bulletTrailList.append([startX,startY,endX,endY])#queue bullet trail for drawing
    return retVal

def calcBullets():#check if the enemy bullets hit anything
    global regenTimer, playerRect
    
    for i in range(len(bulletList)-1,-1,-1):
        nextBullet = False#will stop checking things if the bullet no longer exists
        for j in playTile[2]:
            if bulletList[i].hitRect.colliderect(j[0]):#if bullet hit a platform or wall
                del bulletList[i]
                nextBullet = True
                break
        if not nextBullet:
            for j in range(len(enemyList)-1,-1,-1):#checking player bullets
                enemyRect = Rect(enemyList[j].X,enemyList[j].Y,enemyList[j].W,enemyList[j].H)
                if enemyRect.colliderect(bulletList[i].hitRect) and bulletList[i].faction == 1 and enemyList[j].dying == 0:#if bullet hits an enemy that's not dying
                    enemyList[j].health -= bulletList[i].damage
                    bulletList[i].life = 0
        if not nextBullet:
            if len(bulletList)>0:
                if bulletList[i].hitRect.colliderect(playerRect) and bulletList[i].faction == 0 and bulletList[i].life >0:#if bullet is still alive and it hit the player
                    if player.shield != player.maxShield:
                        regenTimer = 200#begin shield regen
                    if player.shield>0:#if the player has shields
                        player.shield-=bulletList[i].damage#hit shields
                    else:
                        player.health=max(0,player.health-bulletList[i].damage)#hit health
                    bulletList[i].life=0
                else:
                    bulletList[i].moveBullet()
                    bulletList[i].life-=1
                if bulletList[i].life<=0:
                    del bulletList[i]

def drawUpper(playerX, playerY):# Also includes shooting
    global upperSurf, currentWeapon, particleList
    mx, my = mouse.get_pos()
    mb = mouse.get_pressed()
    angle = math.degrees(math.atan2(mx-playerX, my-playerY))-90
    if not player.fA:
        rotUpper=transform.rotate(upperSurf,angle)#rotate upper body
        screen.blit(rotUpper, (playerX-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2-2))
    else:
        rotUpper=transform.rotate(lUpperSurf,angle)#rotate upper body
        screen.blit(rotUpper, (playerX-5-rotUpper.get_width()//2, playerY-rotUpper.get_height()//2-2))
    
    if mb[0] and player.shootCooldown == 0 and player.mag>0:#if player can shoot and is trying to shoot
        player.shootCooldown= weaponList[currentWeapon][1] #fire rate timer
        for i in range(10):#add particles at muzzle of gun
            particleList.append(Particle(screen, player.X+(player.W//2)+20*cosd(angle), player.Y+20-20*sind(angle), -angle, 5, weaponList[currentWeapon][5], 4, 0.1, 0.1,7, 2, 20))
        weaponList[currentWeapon][4].play()
        player.mag-=1
        for i in range(weaponList[currentWeapon][6]):#check if the bullet hit an enemy
            enemyHit = playerShoot(weaponList[currentWeapon])
            if type(enemyHit) == int:#if it hit an enemy
                enemyList[enemyHit].health -= weaponList[currentWeapon][0]
    elif mb[0] and not player.mag and not player.reloading:#if you have no ammo but are trying to shoot
        weaponList[currentWeapon][8].play()
        player.reloading+=1
                
    player.fA =-270 < angle < -90   #change player direction if they are aiming on the left or right
def enemyLogic():#enemy AI
    global enemyList, playerRect
    for i in range(len(enemyList)-1,-1,-1):
        enemyInfo = enemyList[i]#3 characters less to type
        distX = abs(enemyInfo.X-player.X)#distance from player
        distY = abs(enemyInfo.Y - player.Y)
        enemyRect = Rect(enemyInfo.X, enemyInfo.Y, enemyInfo.W, enemyInfo.H)#enemy hitbox
        losX = enemyInfo.X #line of sight x for checking whether you can shoot or not
        checkLos=True
        #Checking health
        if enemyInfo.health<=0:#start dying if not enough health
            if enemyList[i].fA:
                enemyList[i].animation = 6
            else:
                enemyList[i].animation = 7
            if enemyList[i].enemyType != 1:
                random.choice(enemyDeathSounds).play()#find a lovely death sound
            enemyList[i].dying+=1
            if enemyInfo.dying == 1:
                enemyList[i].frame = 1
            if enemyInfo.frame%25 == 0:#wait until enemy death animation is done
                    del enemyList[i]
                    if random.randint(0,2) == 0:#spawn a drop
                        dropType = random.randint(0,len(pickupSprites)-1)
                        dropAmounts = [20,10,50,10,'health','credits']#Rifle, shotgun, laser, health, sniper
                        pickupList.append(Pickup(enemyInfo.X+enemyInfo.W//2, enemyInfo.Y+enemyInfo.H-pickupSprites[dropType].get_height(), dropType, dropAmounts[dropType]))
        elif distY>1000 or distX>1200: #if enemy is too far away then despawn it
            del enemyList[i]
        else:          
            # Jumping over obstacles
            if enemyInfo.oW and enemyInfo.oG:#if there's a wall and the enemy is on the ground
                enemyList[i].jumps -= 1
                enemyList[i].vY -= 7

            # Jumping across gaps
            if enemyInfo.fA:
                if (not enemyRect.move(int(enemyInfo.vM), 1).colliderect(enemyInfo.hP[0])) and enemyInfo.oG:#if the moved enemy won't be still on the platform (hP)
                    enemyList[i].vY -= 7#jump
            elif not enemyInfo.fA:
                if (not enemyRect.move(-int(enemyInfo.vM), 1).colliderect(enemyInfo.hP[0])) and enemyInfo.oG:
                    enemyList[i].vY -= 7

            # Shooting
            if abs(enemyInfo.X-player.X) in range(enemyInfo.avoidance, enemyInfo.shootRange):# if player distance is in between the enemy avoidance and the sooting range
                if abs(enemyInfo.Y - player.Y) <30 and int(enemyInfo.vX) == 0:#if player and enemy are both on the same level
                        while checkLos:#if the mob can shoot the playeer
                            for j in playTile[2]:
                                if j[0].collidepoint(losX,player.Y):#if there is a tile between the mob and the player
                                    checkLos=False
                                    break
                            if abs(player.X-losX) >enemyInfo.shootRange:#if the player is out of range
                                checkLos = False
                            if playerRect.collidepoint(losX, player.Y):#if the player is in line of sight
                                enemyList[i].attacking=True#begin attacking
                                enemyList[i].shootCounter+=1
                                if enemyInfo.fA:#shooting animation
                                    enemyList[i].animation = 4
                                else:
                                    enemyList[i].animation = 5
                                if enemyInfo.shootCounter % weaponList[enemyInfo.weapon][1] == 0:
                                    #different bullet based on different enemy type
                                    if enemyInfo.enemyType == 0:
                                        bulletList.append(Bullet(Rect(enemyInfo.X+enemyInfo.W//2,enemyInfo.Y+25,10,2), enemyInfo.fA, 3, weaponList[enemyInfo.weapon][0],weaponList[enemyInfo.weapon][5]))
                                    elif enemyInfo.enemyType ==1:
                                        bulletList.append(Bullet(Rect(enemyInfo.X+enemyInfo.W//2,enemyInfo.Y,10,2), enemyInfo.fA, 3, weaponList[enemyInfo.weapon][0],weaponList[enemyInfo.weapon][5]))
                                    elif enemyInfo.enemyType == 2:
                                        bulletList.append(Bullet(Rect(enemyInfo.X+enemyInfo.W//2,enemyInfo.Y+25,10,2), enemyInfo.fA, 7, weaponList[enemyInfo.weapon][0],weaponList[enemyInfo.weapon][5]))
                                    weaponList[enemyInfo.weapon][4].play()
                                break
                            if player.X>enemyInfo.X:#check 3 pixels along the line of sight
                                losX+=3
                            elif player.X<enemyInfo.X:
                                losX-=3
                else:
                    enemyList[i].attacking=False
def makeTile(tileInfo):#draw the tile
    global levelAtlas,visualOff
    tileSize = tileInfo.pop(0)
    tileVisual = Surface(tileSize,SRCALPHA)
    for i in tileInfo:
        if i[1] !=2 and i[1]!=3:#if tile is a platform or a wall and not an invisible platform or spawn box
            draw.rect(tileVisual, (0, 0, 0), i[0])#draw a black box
            tileVisual.blit(levelAtlas, i[0].topleft,(0,0,16,16))#draw corner pieces
            tileVisual.blit(levelAtlas, i[0].move(-16,0).topright, (32,32,16,16))
            tileVisual.blit(levelAtlas, i[0].move(0,-16).bottomleft, (16,64,16,16))
            tileVisual.blit(levelAtlas, i[0].move(-16,-16).bottomright, (80,32,16,16))
            if i[0].width>32:#throughout the length of the box, draw the sides and bottom and top textures
                for j in range(16,i[0].width-16,16):
                    tileVisual.blit(levelAtlas,(i[0].left+j,i[0].top),(16,112,16,16))
                    tileVisual.blit(levelAtlas,(i[0].left+j,i[0].bottom-16),(48,128,16,16))
            if i[0].height >32:
                for j in range(16,i[0].height-16,16):
                    tileVisual.blit(levelAtlas, (i[0].left,i[0].top+j), (128,32,16,16))
                    tileVisual.blit(levelAtlas, (i[0].move(-16,0).right,i[0].top+j), (0,16,16,16))
        elif i[1]==3:# if the tile is a spawn box the draw the liset (ship)
            tileVisual.blit(lisetSprite,i[0].move(-50,-20).topleft)
    return (tileSize, tileVisual, tileInfo)


def keysDown(keys):#check what keys are being held
    global player, canUseSword, currentFrame
    mx, my = mouse.get_pos()
    mb=mouse.get_pressed()
    if keys[K_a]:
        player.vX -= player.vAx#moves left
        player.fA = True #player is facing left
    if keys[K_w] and player.oW and (keys[K_a] or keys[K_d]):#if player is wall running
        player.vY = max(-4, player.vY - 0.5)#move player up
        if player.fA:#wall running animation
            player.animation = 9
        elif not player.fA:
            player.animation = 8
    if keys[K_d]:
        player.vX += player.vAx#moves right
        player.fA = False #player is facing right
    if keys[K_e] and not keys[K_a] and not keys[K_d]:#if player is stationary and meleeing
        if player.fA:
            player.animation = 7#melee animation
        elif not player.fA:
            player.animation = 6
        if (currentFrame == 0 or currentFrame == 2):#frames that have the sword swipe 
            if canUseSword:
                swordHit()#check if the sword hit anything
                sword1.play() #make sword swinging sound
                canUseSword=False#can only hit one target per swing
        elif currentFrame == 1 or currentFrame == 3:#frames that no longer have the sword swipe
            canUseSword = True
    elif player.oG:#if the player isn't doing anything and is stationary
        if player.fA:
            player.animation = idleLeft
        elif not player.fA:
            player.animation = idleRight
def applyFriction(mob):
    global friction
    if mob.vX > 0:#if mob is moving, apply friction
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


def hitSurface(mob, tilePlats):#player colliding with the level
    global gravity
    mobRect = Rect(mob.X, mob.Y, mob.W, mob.H)
    hitRect = [Rect(0, 0, 0, 0)]
    wallRect = [Rect(0, 0, 0, 0)]
    for platTile in tilePlats:
        if mobRect.move(0, 1).colliderect(Rect(platTile[0])) and (platTile[1] == 0 or platTile[1] == 2):#if the tile is a platform or an invisible platform
            mob.vY = 0
            mob.hP = platTile
            if mobRect.bottom < platTile[0].bottom:#if the mob is clipping into the tile and is closer to the top of it
                mob.Y = platTile[0].top - mob.H#move mob to top of platform
                mob.oG = True
                mob.jumps = 2
            elif mobRect.top > platTile[0].top:#if mob is closer to bottom
                mob.Y = platTile[0].bottom#move to bototm
                mob.vY *= -1#reflect vY
                mob.oG = False
        if mobRect.colliderect(platTile[0]) and platTile[1] == 1:#if colliding with a wall
            mob.oW = True
            mob.hW = platTile
            if mobRect.left < platTile[0].left:#if mob is on the right side of the wall
                mob.X = platTile[0].left - mob.W - 1#move to right
                mob.jumps = 1#more jumps for jumping off of the wall
            elif mobRect.right > platTile[0].right:
                mob.X = platTile[0].right + 1
                mob.jumps = 1
    if not mobRect.move(0, 1).colliderect(mob.hP[0]):#if player isn't hitting the ground
        mob.oG = False
        mob.vY += gravity
    if not (mobRect.move(0, 1).colliderect(mob.hW[0]) or mobRect.move(0, -1).colliderect(mob.hW[0])):#if player isn't hitting a wall
        mob.oW = False


def drawStuff(tileSurf, tileSize, keys):#render everything
    global player, frames, animation, visualOff, pic, currentFrame
    if keys[K_a] and player.oG:#conditional animations
        player.animation = left
    elif keys[K_d] and player.oG:
        player.animation = right
    elif player.fA and not player.oG and not player.oW:
        player.animation = jumpLeft
    elif not player.fA and not player.oG and not player.oW:
        player.animation = jumpRight
    elif player.fA and player.oG and player.animation != 7 and player.animation != 8:
        player.animation = idleLeft
    elif not player.fA and player.oG and player.animation!= 6 and player.animation !=9:
        player.animation = idleRight
   
    pic = playerFrames[player.animation][0][player.frame // playerFrames[player.animation][1] % len(playerFrames[player.animation][0])]#current frame to show
    player.frame += 1
    screen.blit(tileSurf, (640 - player.X, 360 - player.Y))#blit the level
    for i in bulletList:
        draw.rect(screen,i.colour,i.hitRect.move(640-player.X,360-player.Y))#render the bullets
    for i in range(len(pickupList)):
        screen.blit(pickupSprites[pickupList[i].dropType], (640-player.X+pickupList[i].X,360-player.Y+pickupList[i].Y))#draw the pickups/drops
    for i in range(len(bulletTrailList)-1,-1,-1):#draw the bullet trails from the player
        draw.line(screen,weaponList[currentWeapon][5],(640-player.X+bulletTrailList[i][0],360-player.Y+bulletTrailList[i][1]),(640-player.X+bulletTrailList[i][2],360-player.Y+bulletTrailList[i][3]))
        del bulletTrailList[i]
    for i in enemyList:
        
        if i.enemyType == 0:#draw the enemies based on their type
            enemyPic = crewmanFrames[i.animation][0][i.frame // crewmanFrames[i.animation][1]  % len(crewmanFrames[i.animation][0])]
        elif i.enemyType == 1:
            enemyPic = moaFrames[i.animation][0][i.frame // moaFrames[i.animation][1]  % len(moaFrames[i.animation][0])]
        elif  i.enemyType == 2:
            enemyPic = sCrewmanFrames[i.animation][0][i.frame // sCrewmanFrames[i.animation][1]  % len(sCrewmanFrames[i.animation][0])]            
        i.frame+=1
        screen.blit(enemyPic, (640 - player.X + i.X, 379 - player.Y + i.Y+(25-enemyPic.get_height())))
        draw.line(screen,(255,40,40),(640-player.X+i.X+(30*max(0,i.health)//i.maxHealth),360-player.Y+i.Y+(25-enemyPic.get_height())), (640-player.X+i.X,360-player.Y+i.Y+(25-enemyPic.get_height())))
    currentFrame = player.frame // playerFrames[player.animation][1] % len(playerFrames[player.animation][0])#the current frame for use in other functions
    screen.blit(pic, (640+additionalOffsets[player.animation][player.frame // playerFrames[player.animation][1] % len(playerFrames[player.animation][0])], 360 + (36 - pic.get_height())))#blit the player on the center of the screen
    if not (keys[K_a] or keys[K_w] or keys[K_d] or not player.oG or player.animation == 7 or player.animation == 6):#if the player isn't moving or meleeing
        drawUpper(660,376 + (36 - pic.get_height()))
    drawHud()
def moveParticles():
    for i in range(len(particleList)-1,-1,-1):
        particleList[i].moveParticle()
        if not particleList[i].live:#remove if dead
            del particleList[i]
def spawnEnemies():
    mobSpawnY = player.Y-500#height at which the mob should spawn
    if len(enemyList)<2:#if there are less than 2 enemies
        for i in range(3):#spawn 3 
            newEnemyType = random.randint(0,2)#pick random enemy type
            if newEnemyType == 0:#refer to mob
                enemyList.append(Mob(player.X+random.choice([-1200,1200]), mobSpawnY+50, 30, 45, 0, 0, 3+random.random(), 0.3, False, 1, weapon = 'dera',avoidance=50+random.randint(-5,60),shootRange = 150+random.randint(-10,10)))
            elif newEnemyType == 1:
                enemyList.append(Mob(player.X+random.choice([-1200,1200]), mobSpawnY+50, 45, 45, 0, 0, 4+random.random(), 0.3, False, 1,weapon = 'laser', enemyType =1,avoidance=40+random.randint(-5,30),health = 150,shootRange = 130+random.randint(-20,10)))
            elif newEnemyType == 2:
                enemyList.append(Mob(player.X+random.choice([-1200,1200]), mobSpawnY+50, 45, 45, 0, 0, 2+random.random(), 0.3, False, 1,weapon = 'lanka', enemyType =2,avoidance=430+random.randint(-5,40),shootRange = 500+random.randint(0,100),health=60))
def makeNewLevel(levelLength):#stitches the rects from different tiles together
    levelOut = []
    tileH = 0
    levelSeq = [0]
    for i in range(levelLength):
        levelSeq.append(random.randint(1, len(drawTiles) - 1))#add tile to the list of tiles
    xOff, yOff = 0, 0
    checkPlatList = []
    sameRect = []
    stitchedLevel=[]
    rectOuts=[]
    for i in range(len(levelSeq)):#place tiles together
        tileEnter = int(tileIO[levelSeq[i]][0])
        lastTileExit = int(tileIO[levelSeq[i-1]][1])
        yOff += lastTileExit-tileEnter#difference in entrance and exit heights
        for plat in tileRects[levelSeq[i]]:
            stitchedLevel.append([plat[0].move(xOff, yOff), plat[1]])
        xOff += tileSizes[levelSeq[i]][0]#width of tile
        tileH += tileSizes[levelSeq[i]][1]#height of tiles
        # Placing rects together
    for i in stitchedLevel:
        if i[1] == 0:
            checkPlatList.append([[i[0][1],i[0][0],i[0][2],i[0][3]],i[1]])#Because adjacent tiles should have same height first
        else:
            levelOut.append(i)#walls and invisible platforms won't be stitched together
    checkPlatList.sort()
    while len(checkPlatList)>1:#begin stitching tiles that are adjacent and are the same height together
        pCheck = [checkPlatList[1][0][1],checkPlatList[1][0][0],checkPlatList[1][0][2],checkPlatList[1][0][3]]#Change back to original after it's been sorted
        previousPlat = [checkPlatList[0][0][1],checkPlatList[0][0][0],checkPlatList[0][0][2],checkPlatList[0][0][3]]
        if (previousPlat[0]+previousPlat[2] == pCheck[0] or Rect(previousPlat).colliderect(pCheck)) and pCheck[1] == previousPlat[1]:#if platforms are at the same height and are adjacent or colliding
                unionedRect=Rect(previousPlat).union(Rect(pCheck))#union the tiles
                checkPlatList.insert(2,[[unionedRect[1],unionedRect[0],unionedRect[2],unionedRect[3]],0])#Change back into height prioritized format
                del checkPlatList[0]
                del checkPlatList[0]
        else:
            if [Rect(pCheck),0] not in levelOut and Rect(pCheck).collidelist(rectOuts)==-1:#if not able to be unioned
                levelOut.append([Rect(previousPlat),0])#add to levelout
                rectOuts.append(Rect(previousPlat))
            del checkPlatList[0]
    levelOut.append([Rect([checkPlatList[0][0][1],checkPlatList[0][0][0],checkPlatList[0][0][2],checkPlatList[0][0][3]]),0])#add last platform
    levelOut.insert(0, (xOff, tileH))#insert information about tile width and height
    return levelOut

def playerShoot(weapon):#finds what the player hit
    global pic, movedTileTops,mx,my
    angle = math.degrees(math.atan2(mx-660,my-376 + (36 - pic.get_height())))-90+random.randint(-weaponList[currentWeapon][7],weaponList[currentWeapon][7])#angle from player's upper body to mouse
    return checkBullTrajectory(angle, player.X+player.W//2, player.Y+20)
def fixLevel(levelIn): #Moves the level so that it isn't outside of the bounding box
    global visualOff, mobSpawnY,spawnX,spawnY,movedTileTops
    platHeights=[]
    platTypes=[]
    movedTileTops=[]
    newTile=[levelIn.pop(0)]
    finalRects=[]
    for i in levelIn:
        platHeights.append(i[0].top)#heights of the platforms
        platTypes.append(i[1])#types of the platform (wall, platform, invisible platform, etc.)
    visualOff = min(platHeights)#highest tile
    for i in levelIn:#move everything so the highest tile still has 1280 pixels above it
        movedRect=i[0].move(0,abs(visualOff)+1280)
        movedTileTops.append(movedRect.top)
        newTile.append([movedRect,i[1]])
        if i[1] == 3:#make the player's spawn location the spawn box's coordinates
            spawnX,spawnY = newTile[-1][0].topleft
    newTile.append([Rect(-16,min(movedTileTops)-720,20000,32),2]  )#platform so player can't leave level
    newTile.append([Rect(-16,min(movedTileTops)-720,32,newTile[0][1]),1]  )#wall on left
    newTile.append([Rect(newTile[0][0]-16,min(movedTileTops)-720,32,newTile[0][1]),1]  )#wall on right
    return newTile
def pauseMenu():
    global running,animationStatus,menuAnimation,mx,my,mb,gameState,canClick
    options = ['Back To Game', 'Return To Ship', 'Quit']
    for i in range(len(options)):#draw the options
        optionRect= Rect(500,70*i+160,340,60)
        if optionRect.collidepoint((mx,my)):#if mouse is colliding with an option
            draw.rect(screen,(255,255,255),optionRect)#highlight it
            draw.rect(screen,(0,0,255),optionRect,2)
            optionText = hudFont.render(options[i], True, (0,0,0))
            screen.blit(optionText, (670-optionText.get_width()//2,70*i+170))
            if mb[0]==1:
                draw.rect(screen,(255,0,0),optionRect,2)
                option = i
                if option == 0:#do what the option picked was
                    closeMenu.play()
                    animationStatus =-1
                    menuAnimation = 20
                elif option == 1:
                    canClick=False
                    gameState = 'ship'
                elif option == 2:
                    running=False
        else:#draw the boxes with regular colouring
            draw.rect(screen,(0,0,0),optionRect)
            draw.rect(screen,(0,0,255),optionRect,2)
            optionText = hudFont.render(options[i], True, (255,255,255))
            screen.blit(optionText, (670-optionText.get_width()//2,70*i+170))
def shipMenu():#menu for the store
    global mx,my,mb,gameState,playTile,drawnmap,minimap,selectedWeaponType,purchasedWeapons,weaponCosts,currentWeapon,canClick
    screen.fill((0,0,0))
    weaponOffX=0
    startGameButton = Rect(1130,640,140,70)
    riflesButton = Rect(95,20,264,50)
    shotgunsButton = Rect(369,20,264,50)
    snipersButton = Rect(643,20,264,50)
    heavyButton = Rect(917,20,264,50)
    weaponTypeButtons = [riflesButton,shotgunsButton,snipersButton,heavyButton]
    typeSortedWeapons = [['dera','braton','grakata'],['tigris','hek','boarP'],['rubico','vulkar'],['gorgon','laser']]
    weaponTypes = ['Rifles', 'Shotguns', 'Snipers', 'Heavy']
    weapons=list(weaponList.keys())#list of weapon names from the dictionary that contains the weapon information
    weapons.sort()#sort alphabetically
    draw.rect(screen,(150,150,150),(0,25,1280,50))
    for i,j in zip(weaponTypeButtons,weaponTypes):
        listPos=weaponTypes.index(j)
        weaponTypeName = hudFont.render(j,True,(255,255,255))
        screen.blit(weaponTypeName,i.move(0,10).topleft)
        if selectedWeaponType == listPos:#draw a line under the selected weapon type
            draw.line(screen,(255,255,255),i.bottomleft,i.bottomright,2)
        if i.collidepoint((mx,my)):#if mouse is hovering over the weapon button
            weaponTypeName = hudFont.render(j,True,(255,255,190))
            if mb[0]==1:
                selectedWeaponType = listPos
        screen.blit(weaponTypeName,i.move(0,10).topleft)
    for i,j,k in zip(typeSortedWeapons[selectedWeaponType],purchasedWeapons[selectedWeaponType],weaponCosts[selectedWeaponType]):
        wepSpr = eval(i)#weapon Sprite, shorter than eval(i) by a bit
        scaledSprite = transform.smoothscale(wepSpr,(wepSpr.get_width()*5,wepSpr.get_height()*5))
        if j:#if weapon is purchased
            draw.rect(screen,(0,255,0),Rect(weaponOffX+395,270,120,85),2)
        else:
            draw.rect(screen,(150,150,150),Rect(weaponOffX+395,270,120,85),2)
        #draw weapon name and cost
        screen.blit(descFont.render(i.title(),True,(255,255,255)),(weaponOffX+400,270))
        screen.blit(scaledSprite,(weaponOffX+400,300))
        creditCost=descFont.render(str(k),True,(255,255,255))
        screen.blit(creditCost,(weaponOffX+513-creditCost.get_width(),330))
        screen.blit(hudCredit,(weaponOffX+500-creditCost.get_width(),337))
        
        
        if mb[0]==1 and canClick:
            if Rect(weaponOffX+400,270,120,85).collidepoint(mx,my):
                if player.money >=k and not j:#if player has enough money and hasn't already purchased weapon
                    player.money-=k
                    purchasedWeapons[selectedWeaponType][typeSortedWeapons[selectedWeaponType].index(i)]=1
                elif j:
                    currentWeapon=typeSortedWeapons[selectedWeaponType][typeSortedWeapons[selectedWeaponType].index(i)]
        if currentWeapon == i:#status of weapon
            draw.circle(screen,(0,255,0),(weaponOffX+505,280),7)
        elif j:
            draw.circle(screen,(0,0,255),(weaponOffX+505,280),7)
        elif player.money<k:
            draw.circle(screen,(255,0,0),(weaponOffX+505,280),7)
        weaponOffX+=150
    #draw store legend and start button
    startGameButtonText = hudFont.render('Start',True,(0,0,0))
    draw.rect(screen,(255,255,255),startGameButton)
    screen.blit(startGameButtonText,(1167,660,140,70))
    creditHud = Surface((200,25),SRCALPHA)
    creditDisplay = descFont.render(str(player.money),True,(255,255,255))
    creditHud.blit(hudCredit, (0,5))
    creditHud.blit(creditDisplay, (20,0))
    screen.blit(creditHud,(10,690))
    legendText=descFont.render('Buyable',True,(255,255,255))
    screen.blit(legendText,(19,588))
    legendText=descFont.render('Not Enough Money',True,(255,255,255))
    screen.blit(legendText,(19,608))
    legendText=descFont.render('Purchased',True,(255,255,255))
    screen.blit(legendText,(19,628))
    legendText=descFont.render('Equipped',True,(255,255,255))
    screen.blit(legendText,(19,648))
    draw.circle(screen,(255,255,255),(10,600),7,1)
    draw.circle(screen,(255,0,0),(10,620),7)
    draw.circle(screen,(0,0,255),(10,640),7)
    draw.circle(screen,(0,255,0),(10,660),7)
    if startGameButton.collidepoint(mx,my):#if player presses the start button
        startGameButtonText = hudFont.render('Start',True,(255,255,255))
        draw.rect(screen,(0,0,0),startGameButton)
        draw.rect(screen,(255,255,255),startGameButton,2)
        screen.blit(startGameButtonText,(1167,660,140,70))
        if mb[0]==1:
            deathAnimation = 0
            gameState = 'game'
            playTile,drawnmap,minimap=startGame()
            
def reloadTime():
    global weaponList
    if player.reloading >0:
        player.reloading+=1
    if player.reloading == weaponList[currentWeapon][3]:
        player.reloading = 0
        player.reserveAmmo[weaponList[currentWeapon][9]]+=player.mag#move ammo from mag to reserve
        transferAmmo = min(weaponList[currentWeapon][2],player.reserveAmmo[weaponList[currentWeapon][9]])#prepare to move one mag worth of ammo back
        player.mag = transferAmmo
        player.reserveAmmo[weaponList[currentWeapon][9]] -= transferAmmo

def startGame():#reset all game related variables
    global spawnX,spawnY,menuAnimation,animationStatus,enemyList,pickupList,regenTimer,bulletList
    playTile = makeTile(fixLevel(makeNewLevel(10)))
    drawnMap = playTile[1]
    minimap = transform.smoothscale(drawnMap, [drawnMap.get_width()//7,drawnMap.get_height()//7])
    player.health,player.shield = player.maxHealth,player.maxShield
    player.reserveAmmo = [500,200,2500,60]
    player.X,player.Y = spawnX,spawnY
    enemyList = []
    canRegenShields = False
    pickupList = []
    bulletList = []
    regenTimer = 0
    menuAnimation = 0
    animationStatus =-1
    player.mag = weaponList[currentWeapon][2]
    drawUpperSprite()
    return (playTile,drawnMap,minimap)

def mainMenu():
    global mx,my,mb,gameState,running
    options = ['Play', 'Instructions'] 
    screen.blit(mainPic,(-150,0))
    screen.blit(title,(750,50))
    buttons=[Rect(1000,500,200,60),Rect(1000,600,200,60)]
    for r,v in zip(buttons,options):
        draw.rect(screen,(150,150,150),r)
        draw.rect(screen,(255,255,255),r,2)
        for i in range(len(options)):#check what option you clicked
            optionText = hudFont.render(options[i], True, (255,255,255))
            screen.blit(optionText, (1100-optionText.get_width()//2,100*i+530-optionText.get_height()//2))
        if r.collidepoint(mx,my):
            draw.rect(screen,(255,0,0),r,2)
        if mb[0]==1 and buttons[0].collidepoint(mx,my):
            gameState = 'ship'
        if mb[0]==1 and buttons[1].collidepoint(mx,my):
            gameState = 'instructions'
        
def instructions():#draw the instructoins
    global mb, gameState
    screen.blit(mainPic,(-150,0))
    screen.blit(title,(750,50))
    screen.blit(controls,(640-controls.get_width()//2,360-controls.get_height()//2))
    if mb[0]==1:
        gameState="menu"
        mainMenu()
#Main Menu
mainPic = image.load('images/menu/Mainpic.jpg')
title = image.load('images/menu/title.png')
title = transform.scale(title,(500,160))
#instructions
controls = image.load('images/menu/instructions.png')
controls = transform.scale(controls,(controls.get_width()*2,controls.get_height()*2))        
#Fonts
hudFont=font.Font('fonts/Roboto-Light.ttf',30)
descFont = font.Font('fonts/Roboto-Light.ttf',20)
lisetSprite = image.load('images/levels/liset.png')
lisetSprite = transform.smoothscale(lisetSprite, (int(lisetSprite.get_width()*1.5),int(lisetSprite.get_height()*1.5)))
#Sounds
#Music
mixer.music.load('sfx/music/theme.ogg') #loads music
    #Shooting
bratonShoot = mixer.Sound('sfx/weapons/corpus/bratonShoot.ogg')
deraShoot = mixer.Sound('sfx/weapons/corpus/deraShoot.ogg')
boarShoot = mixer.Sound('sfx/weapons/orokin/boarP.ogg')
laserShoot = mixer.Sound('sfx/weapons/factionless/moaGun.ogg')
hekShoot = mixer.Sound('sfx/weapons/grineer/hekShoot.ogg')
rubicoShoot = mixer.Sound('sfx/weapons/tenno/rubico.ogg')
tigrisShoot = mixer.Sound('sfx/weapons/tenno/tigris.ogg')
gorgonShoot = mixer.Sound('sfx/weapons/grineer/gorgon.ogg')
grakataShoot = mixer.Sound('sfx/weapons/grineer/grakataShoot.ogg')
twinviperShoot = mixer.Sound('sfx/weapons/grineer/twinviper.ogg')
vulkarShoot = mixer.Sound('sfx/weapons/grineer/vulkar.ogg')
lankaShoot = mixer.Sound('sfx/weapons/corpus/lankaShoot.ogg')
    #Reloading
laserReload = mixer.Sound('sfx/weapons/factionless/moaGunReload.ogg')
bratonReload = mixer.Sound('sfx/weapons/corpus/bratonReload.ogg')
deraReload = mixer.Sound('sfx/weapons/corpus/deraReload.ogg')
boarReload = mixer.Sound('sfx/weapons/orokin/boarPreload.ogg')
hekReload = mixer.Sound('sfx/weapons/grineer/hekReload.ogg')
rubicoReload = mixer.Sound('sfx/weapons/tenno/rubicoReload.ogg')
tigrisReload = mixer.Sound('sfx/weapons/tenno/tigrisReload.ogg')
gorgonReload = mixer.Sound('sfx/weapons/grineer/gorgonReload.ogg')
grakataReload = mixer.Sound('sfx/weapons/grineer/grakataReload.ogg')
twinviperReload = mixer.Sound('sfx/weapons/grineer/twinviperReload.ogg')
vulkarReload = mixer.Sound('sfx/weapons/grineer/vulkarReload.ogg')
lankaReload = mixer.Sound('sfx/weapons/corpus/lankaReload.ogg')
    #Other
ammoPickup = mixer.Sound('sfx/misc/ammoPickup.ogg')
healthPickup = mixer.Sound('sfx/misc/healthPickup.ogg')
sword1 = mixer.Sound('sfx/weapons/tenno/nikana1.ogg')
sword2 = mixer.Sound('sfx/weapons/tenno/nikana2.ogg')
enemyDeathSounds = [mixer.Sound('sfx/misc/corpusDeath.ogg'),mixer.Sound('sfx/misc/corpusDeath1.ogg')]
weaponList = {'braton':[ 25, 20, 45, 100, bratonShoot,(200, 150, 0),1,1,bratonReload,0], 'dera':[16, 17, 30, 80, deraShoot,(50,170,255),1,3,deraReload,0],'boarP':[5,13,20,100,boarShoot, (200,150,0),13,12,boarReload,1],'laser':[3,2,250,100,laserShoot, (255,0,0),1,0,laserReload,2],
              'hek':[19,30,4,100,hekShoot,(200,150,0),7,5,hekReload,1], 'tigris':[25,15,2,120,tigrisShoot,(200,150,0),5,8,tigrisReload,1], 'rubico':[150, 150, 5, 100, rubicoShoot,(255,255,255),1,0,rubicoReload,3],'gorgon':[20,10,90,180,gorgonShoot,(200,150,0),1,3,gorgonReload,0],
              'grakata':[14,5,60,100,grakataShoot,(200,150,0),1,10,grakataReload,0], 'twinviper':[13,2,28,80,twinviperShoot,(255,255,255),1,8,twinviperReload,0],'vulkar':[120,100,6,100,vulkarShoot,(200,150,0),1,0,vulkarReload,3],'lanka':[70,150,10,100,lankaShoot,(0,255,0),1,1,lankaReload,3]}#damage per shot, fire rate, mag size, reload speed, sfx, muzzleFlash Colour, projectiles per shot, accuracy, reload sound, ammo type
screen = display.set_mode((1280, 720))
display.set_icon(image.load('images/deco/icon.png'))
idleRight, idleLeft, right, left, jumpRight, jumpLeft = 0, 1, 2, 3, 4, 5
beginShieldRegen = mixer.Sound('sfx/warframes/shield/shieldRegen.ogg')
openMenu = mixer.Sound('sfx/misc/openMenu.ogg')
closeMenu = mixer.Sound('sfx/misc/closeMenu.ogg')
levelAtlas = image.load('images/levels/tileTextures.png')
hudCredit = image.load('images/drops/lifeSupport/hudCredits.png')
#Guns
braton = image.load('images/weapons/corpus/braton.png')
dera = image.load('images/weapons/corpus/dera.png')
boarP = image.load('images/weapons/orokin/boarP.png')
laser = image.load('images/weapons/corpus/moaGun.png')
rubico = image.load('images/weapons/tenno/rubico.png')
tigris = image.load('images/weapons/tenno/tigris.png')
hek = image.load('images/weapons/grineer/hek.png')
gorgon = image.load('images/weapons/grineer/gorgon.png')
grakata = image.load('images/weapons/grineer/grakata.png')
twinviper = image.load('images/weapons/grineer/twinviper.png')
vulkar = image.load('images/weapons/grineer/vulkar.png')
lanka = image.load('images/weapons/corpus/lanka.png')

frostUpper = image.load('images/warframes/frost/frostUpper.png')
frostArms = image.load('images/warframes/frost/frostArms.png')
frostLower = image.load('images/warframes/frost/frostLower.png')
currentWeapon = 'dera'

pic = Surface((20,30))
pickupSprites = [image.load('images/drops/ammo/rifleAmmo.png'),image.load('images/drops/ammo/shotgunAmmo.png'),image.load('images/drops/ammo/laserAmmo.png') ,image.load('images/drops/ammo/sniperAmmo.png'),image.load('images/drops/lifeSupport/health.png'),image.load('images/drops/lifeSupport/credits.png')]#money is now required to live
pickupList=[]
encouragement =['Go Again','Keep Trying','Finish the Job',"You're making progress",'Finish them off','Finish the job']
encouragementText=''
# Animations
moaFrames = [[[image.load('images/enemies/moa/Moa001.png')],1], [[image.load('images/enemies/moa/Moa002.png'),image.load('images/enemies/moa/Moa003.png'),image.load('images/enemies/moa/Moa004.png'),image.load('images/enemies/moa/Moa005.png'),image.load('images/enemies/moa/Moa006.png'),image.load('images/enemies/moa/Moa007.png')],7], [[image.load('images/enemies/moa/Moa008.png'),image.load('images/enemies/moa/Moa009.png')],7], [[image.load('images/enemies/moa/Moa010.png'),image.load('images/enemies/moa/Moa011.png'),image.load('images/enemies/moa/Moa012.png'),image.load('images/enemies/moa/Moa013.png'),image.load('images/enemies/moa/Moa014.png'),image.load('images/enemies/moa/Moa015.png'),image.load('images/enemies/moa/Moa016.png')],7]]
crewmanFrames = [[[image.load('images/enemies/crewman/crewman001.png')],1], [[image.load('images/enemies/crewman/crewman002.png'), image.load('images/enemies/crewman/crewman003.png'), image.load('images/enemies/crewman/crewman004.png'), image.load('images/enemies/crewman/crewman005.png'), image.load('images/enemies/crewman/crewman006.png'), image.load('images/enemies/crewman/crewman007.png'), image.load('images/enemies/crewman/crewman008.png'), image.load('images/enemies/crewman/crewman009.png')], 9], [[image.load('images/enemies/crewman/crewman010.png'), image.load('images/enemies/crewman/crewman011.png'), image.load('images/enemies/crewman/crewman012.png'), image.load('images/enemies/crewman/crewman013.png')], 5], [[image.load('images/enemies/crewman/crewman014.png'), image.load('images/enemies/crewman/crewman015.png'), image.load('images/enemies/crewman/crewman016.png'), image.load('images/enemies/crewman/crewman017.png'), image.load('images/enemies/crewman/crewman018.png'), image.load('images/enemies/crewman/crewman019.png'), image.load('images/enemies/crewman/crewman020.png')], 5]]
sCrewmanFrames = [[[image.load('images/enemies/sniperCrewman/sCrewman001.png')],1],[[image.load('images/enemies/sniperCrewman/sCrewman002.png'),image.load('images/enemies/sniperCrewman/sCrewman003.png'),image.load('images/enemies/sniperCrewman/sCrewman004.png'),image.load('images/enemies/sniperCrewman/sCrewman005.png'),image.load('images/enemies/sniperCrewman/sCrewman006.png'),image.load('images/enemies/sniperCrewman/sCrewman007.png'),image.load('images/enemies/sniperCrewman/sCrewman008.png'),image.load('images/enemies/sniperCrewman/sCrewman009.png')],7],[[image.load('images/enemies/sniperCrewman/sCrewman010.png')],1],[[image.load('images/enemies/sniperCrewman/sCrewman014.png'),image.load('images/enemies/sniperCrewman/sCrewman015.png'),image.load('images/enemies/sniperCrewman/sCrewman016.png'),image.load('images/enemies/sniperCrewman/sCrewman017.png'),image.load('images/enemies/sniperCrewman/sCrewman018.png'),image.load('images/enemies/sniperCrewman/sCrewman019.png'),image.load('images/enemies/sniperCrewman/sCrewman020.png')],5]]
playerFrames = [[[image.load("images/warframes/frost/frost001.png")], 1], [[image.load("images/warframes/frost/frost003.png"), image.load("images/warframes/frost/frost004.png"), image.load("images/warframes/frost/frost005.png"), image.load("images/warframes/frost/frost006.png"), image.load("images/warframes/frost/frost007.png"), image.load("images/warframes/frost/frost008.png")], 7], [[image.load("images/warframes/frost/frost015.png"), image.load("images/warframes/frost/frost016.png"), image.load("images/warframes/frost/frost017.png"), image.load("images/warframes/frost/frost018.png"), image.load("images/warframes/frost/frost019.png"), image.load("images/warframes/frost/frost020.png"), image.load("images/warframes/frost/frost021.png")], 5],[[image.load('images/warframes/frost/frostMelee001.png'),image.load('images/warframes/frost/frostMelee002.png'),image.load('images/warframes/frost/frostMelee003.png'),image.load("images/warframes/frost/frostMelee004.png")],15],[[image.load('images/warframes/frost/frost022.png'),image.load('images/warframes/frost/frost023.png'),image.load('images/warframes/frost/frost024.png'),image.load('images/warframes/frost/frost025.png'),image.load('images/warframes/frost/frost026.png'),image.load('images/warframes/frost/frost027.png')],7]]
flippedFrame = Surface((0, 0))

#Player frames
playerFrames=completeFrames(playerFrames, [0,2,4,6,8,10], [1,3,5,7,9,11])
crewmanFrames = completeFrames(crewmanFrames, [0,2, 4, 6], [1,3, 5, 7])
moaFrames = flipFrames(completeFrames(moaFrames, [0,2,4,6], [1,3,5,7]))
sCrewmanFrames = completeFrames(sCrewmanFrames,[0,2,4,6],[1,3,5,7])
globalTicks = 0
mobSpawnY=0
idle = idleRight
jump = jumpRight
additionalOffsets=[[0],[0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[-20,-20,0,0],[-49,-19,-19,-7],[0,0,0,0,0,0],[0,0,0,0,0,0]]#used only for melee animations

#Particles
particleList=[]


#Physics
friction = 0.2111
airFriction = 0.02111
gravity = 0.25

#Tiles
currentTile = 0
tileSetRects = glob.glob('tileset/plat?.txt')
canClick=True
drawTiles = []
tileRects = []
tileSizes = []
movedTiles = []
tileIO = []
visualOff = 0
movedTileTops=[]
#Get information from tileset files
for i in range(len(tileSetRects)):
    tileFile = open(tileSetRects[i]).readlines()#read tile info
    currentTileSize = [int(i) for i in tileFile[0].split()[0:2]]#tile size
    tileEntrance = tileFile[0].split()[2]
    tileExit = tileFile[0].split()[3]
    tileIO.append([tileEntrance, tileExit])
    tileSizes.append(currentTileSize)
    tileRects.append([])
    drawTiles.append(Surface(currentTileSize))
    drawTiles[i].fill((255, 255, 255))
    for j in range(1, len(tileFile)):
        platInfo = tileFile[j].split()#append tile rect, type
        newPlat = [int(platInfo[i]) for i in range(4)]
        draw.rect(drawTiles[i], (0, 0, 0), newPlat)
        tileRects[i].append([Rect(newPlat), int(platInfo[4])])
playTile=((0,0),Surface((0,0)),[[Rect(0,0,0,0)],0])
minimap = Surface((0,0))
drawMap=playTile[1]
#Player
player = Mob(400, 300, 33, 36, 0, 0, 4, 0.3, False, 2,health = 100,shield = 100)#refer to mob
currentFrame = 0

#Store info
purchasedWeapons =[[1,0,0],[0,0,0],[0,0],[0,0]]
weaponCosts = [[0,5000,10000],[15000,20000,25000],[20000,17500],[20000,25000]]
bulletTrailList=[]
counter = 0
shooting = False
paused = False
caseNumber = random.randint(0,999999)
regenTimer = 0
deathAnimation =0
canRegenShields = False
selectedWeaponType=0




# Getting information from the level files

# Other
running = True
playerStanding = Surface((player.W, player.H))
playerStanding.fill((255, 0, 0))
gameClock = time.Clock()

animationStatus=-1#positive for opening, negative for closing
menuOn = 0
menuAnimation=0
canUseSword = True
gameState = 'menu'
enemyList =[]
bulletList = []
mixer.music.play(-1) #plays music on repeat
drawUpperSprite()
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
            if e.key == K_w and player.jumps > 0:#if player can jump
                player.vY = -7
                player.jumps -= 1
            if e.key == K_ESCAPE:#pausing the game
                if gameState == 'game':
                    animationStatus *=-1
                    if animationStatus>0:
                        menuAnimation = 0
                        openMenu.play()
                        pauseScreen=screen.copy()
                    elif animationStatus<0:
                        closeMenu.play()
                        menuAnimation = 20
            if e.key == K_r:#reload
                if player.reloading == 0:
                    weaponList[currentWeapon][8].play()
                    player.reloading+=1
        if e.type == MOUSEBUTTONDOWN:#shooting
            if e.button == 1:
                shooting = True
        if e.type == MOUSEBUTTONUP:#not shooting
            canClick=True
            if e.button == 1:
                shooting = False
    mb = mouse.get_pressed()
    mx,my=mouse.get_pos()
    playerRect = Rect(player.X,player.Y,player.W,player.H)
    screen.fill((0, 0, 0))                
    display.set_caption('pyFrame - %d fps' %(int(gameClock.get_fps())))
    keysIn = key.get_pressed()
    if gameState == 'ship':
        shipMenu()
    if gameState == 'menu':
        mainMenu()
    if gameState == 'instructions':
        instructions()
    if gameState == 'game':
        if menuAnimation <= 0 and player.health >0:#go through all game related functions if not in the pause menu and if alive
            spawnEnemies()
            keysDown(keysIn)
            reloadTime()
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
            if int(player.shield) == 0 and regenTimer == 0:#play sound only if player has hit 0 health
                beginShieldRegen.play()
            if canRegenShields and regenTimer == 0:
                player.shield += 0.4

            regenTimer = max(0,regenTimer-1)
            #pickups
            for i in range(len(pickupList)-1,-1,-1):
                pickupList[i].fallToGround()
                if pickupList[i].checkCollide():
                    del pickupList[i]
            moveParticles()
            drawStuff(playTile[1], playTile[0], keysIn)
            if player.shootCooldown >0:#fire rate
                player.shootCooldown-=1
        elif menuAnimation >= 1:#if paused
            screen.blit(pauseScreen,(0,0))
            draw.rect(screen,(255,255,255),(670-min(menuAnimation*10,180),350-min(menuAnimation*20,200),2*min(menuAnimation*10,180),2*min(menuAnimation*10,110)))
            if menuAnimation>=20:
                pauseMenu()
        elif player.health <=0:#if dead
            if player.health<=0 and deathAnimation == 0:
                encouragementText=random.choice(encouragement)
            deathAnimation +=1
            if deathAnimation<350:
                screen.fill((min(200,deathAnimation*3),0,0))
            elif deathAnimation >=350:
                screen.fill((min(200,max(200-((deathAnimation-350)*3),0)),0,0))
            if deathAnimation in range(50,500):
                screen.blit(hudFont.render('You Died', True, (0,0,0)),(580,300))
            if deathAnimation in range(200,500):
                encouragementRender=hudFont.render(encouragementText, True, (0,0,0))
                screen.blit(encouragementRender,(640-encouragementRender.get_width()//2,350))
            if deathAnimation >500:
                gameState = 'ship'
                deathAnimation =0
                
        menuAnimation+=animationStatus
    display.flip()
    gameClock.tick(60)
quit()
print('cya')
