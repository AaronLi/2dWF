# Base Platformer
from pygame import *
import glob, random, math, pickle


init()
mixer.music.set_volume(0.1)
startTime = time.get_ticks()
startingMoney = 5000


class Particle:  # Class used for simulating particles (Guns, 'blood', bullet hits)
    def __init__(self, surface, x, y, rotation, lifetime, colour, speed, gravity, airResistance, fadeRate, length=1,
                 variation=10, size=1):
        colourOff = random.randint(0, 255 - max(colour))
        self.surf = surface
        self.X, self.Y = x, y  # position
        self.rot = rotation + random.randint(-variation, variation)  # direction
        self.life = lifetime  # amount of iterations before it disappears
        self.col = (colour[0] + colourOff, colour[1] + colourOff, colour[2] + colourOff)
        self.speed = speed  # distance it moevs per iteration
        self.fG = gravity  # amount it's Y is affected per iteration
        self.aR = airResistance  # amount it's X is affected per iteration
        self.fR = fadeRate  # Amount it's colour fades per iteration
        self.live = True
        self.length = length  # Length of particle tail
        self.size = size

    def moveParticle(self):  # Move the particle based on it's speed and remove it if it's dead
        if self.live:
            draw.line(self.surf, self.col, (640 - player.X + int(self.X), 360 - player.Y + int(self.Y)), (
                640 - player.X + int(self.X - self.length * cosd(self.rot)),
                360 - player.Y + int(self.Y - self.length * sind(self.rot))), self.size)
            self.X += self.speed * cosd(self.rot)
            self.Y += self.speed * sind(self.rot)
            self.col = (max(self.col[0] - self.fR, 0), max(self.col[1] - self.fR, 0), max(self.col[2] - self.fR, 0))
            self.life -= 1
            self.speed = max(self.speed - self.aR, 0)
            self.Y = max(self.Y + self.fG, 0)
        if self.life <= 0:
            self.live = False

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
    def moveDoor(self):
        openDoor = False
        for i in enemyList:
            if abs(math.hypot(i.X-self.x,i.Y-self.y)) < 70:
                openDoor = True
        if abs(math.hypot(player.X-self.x,player.Y-self.y))<70:
            openDoor = True
        if openDoor and self.offY >self.openHeight:
            self.offY -= self.vY
        elif not openDoor and self.offY < 0:
            self.offY += self.vY
        self.hitBox = Rect(self.x,self.y+self.offY,self.w,self.h)
    def draw(self):
        screen.blit(self.sprite,(640-player.X+self.x,360-player.Y+self.y+self.offY))
class Mob:  # Class used for the player and enemies
    def __init__(self, x, y, w, h, vX, vY, vM, vAx, fA, jumps, health=100, shield=100, enemyType=0, animation=0,
                 weapon='braton', avoidance=50, shootRange=200, money=5000):
        self.X, self.Y = x, y
        self.W, self.H = w, h
        self.vX, self.vY = vX, vY
        self.vM, self.vAx = vM, vAx  # max velocity for mob to travel at, acceleration rate to the max
        self.oG, self.oW = False, False  # whether the mob is on the ground/floor, whether the mob is on a wall
        self.fA = fA  # (player.fAcing) True for right, False for left
        self.jumps = jumps  # amount of jumps the mob has left
        self.frame = 0  # Current frame the mob is on
        self.hP, self.hW = [Rect(0, 0, 0, 0), 0], [Rect(0, 0, 0, 0),
                                                   0]  # Hit Plat, Hit Wall - last floor platform the mob hit
        self.maxHealth = health  # Won't be changed, only read to find the limit
        self.maxShield = shield  # same as maxHealth
        self.money = money  # Credits, for purchasing weapons

        self.health = health  # current Health
        self.shield = shield  # current shields

        self.shieldTimer = 300  # Time until shield begins regenerating
        self.animation = animation  # current frame set the mob is on
        self.weapon = weapon  # current weapon the mob is using (Used more with enemies)
        self.shootCooldown = 0  # Fire rate timer
        self.mag = 45  # Current magazine size, changes with weapon
        self.reloading = 0  # Reload timer
        # Enemy Related things
        self.enemyType = enemyType
        self.attacking = False
        self.dying = 0  # 0 if alive >0 if not alive
        self.avoidance = avoidance  # How close the player can be
        self.shootRange = shootRange  # How far the mob tries to stay
        self.shootCounter = 0  # Enemy fire rate timer
        self.despawn = False
    def move(self):
        self.X += int(self.vX)
        self.Y += int(self.vY)

    def enemyLogic(self):
        #Logic
        distX = abs(self.X - player.X)  # distance from player
        distY = abs(self.Y - player.Y)
        enemyRect = Rect(self.X, self.Y, self.W, self.H)  # enemy hitbox
        losX = self.X  # line of sight x for checking whether you can shoot or not
        checkLos = True
        # Checking health
        if self.health <= 0:  # start dying if not enough health
            if self.fA:
                self.animation = 6
            else:
                self.animation = 7
            if self.enemyType != 1:
                random.choice(enemyDeathSounds).play()  # find a lovely death sound
            self.dying += 1
            if self.dying == 1:
                self.frame = 1
            if self.frame % 25 == 0:  # wait until enemy death animation is done
                if random.randint(0, 2) == 0:  # spawn a drop
                    dropType = random.randint(0, len(pickupSprites) - 1)
                    dropAmounts = [20, 10, 50, 10, 'health', 'credits']  # Rifle, shotgun, laser, health, sniper
                    pickupList.append(Pickup(self.X + self.W // 2,
                                             self.Y + self.H - pickupSprites[dropType].get_height(),
                                             dropType,
                                             dropAmounts[dropType]))
        elif distY > 1000 or distX > 1200:  # if enemy is too far away then despawn it
            self.despawn = True
        else:
            # Jumping over obstacles
            if self.oW and self.oG:  # if there's a wall and the enemy is on the ground
                self.jumps -= 1
                self.vY -= 7

            # Jumping across gaps
            if self.fA:
                if (not enemyRect.move(int(self.vM), 1).colliderect(
                        self.hP[
                            0])) and self.oG:  # if the moved enemy won't be still on the platform (hP)
                    self.vY -= 7  # jump
            elif not self.fA:
                if (not enemyRect.move(-int(self.vM), 1).colliderect(self.hP[0])) and self.oG:
                    self.vY -= 7

            # Shooting
            if abs(self.X - player.X) in range(self.avoidance,
                                                    self.shootRange):  # if player distance is in between the enemy avoidance and the sooting range
                if abs(self.Y - player.Y) < 30 and int(
                        self.vX) == 0:  # if player and enemy are both on the same level
                    while checkLos:  # if the mob can shoot the playeer
                        for j in playTile[2]:
                            if j[0].collidepoint(losX,
                                                 player.Y):  # if there is a tile between the mob and the player
                                checkLos = False
                                break
                        for j in doorList:
                            if j.hitBox.collidepoint(losX, player.Y):
                                checkLos = False
                                break
                        if abs(player.X - losX) > self.shootRange:  # if the player is out of range
                            checkLos = False
                        if playerRect.collidepoint(losX, player.Y):  # if the player is in line of sight
                            self.attacking = True  # begin attacking
                            self.shootCounter += 1
                            if self.fA:  # shooting animation
                                self.animation = 4
                            else:
                                self.animation = 5
                            if self.shootCounter % weaponList[self.weapon].firerate == 0:
                                # different bullet based on different enemy type
                                if self.enemyType == 0:
                                    if self.fA:
                                        bulletList.append(
                                            Bullet2(self.X, self.Y + 25, 0,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                    weaponList[self.weapon].bulletColour,
                                                    (255, 0, 0), 7, 0, 0, 2))
                                    else:
                                        bulletList.append(
                                            Bullet2(self.X + self.W, self.Y + 25, 180,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                    weaponList[self.weapon].bulletColour, (255, 0, 0), 7,
                                                    0, 0, 2))
                                elif self.enemyType == 1:
                                    if self.fA:
                                        bulletList.append(
                                            Bullet2(self.X + self.W // 2, self.Y, 0,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                    weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                    0, 0, 4))
                                    else:
                                        bulletList.append(
                                            Bullet2(self.X + self.W // 2, self.Y, 180,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                    weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                    0, 0, 4))
                                elif self.enemyType == 2:
                                    if self.fA:
                                        bulletList.append(
                                            Bullet2(self.X + self.W // 2, self.Y + 25, 0,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 7,
                                                    weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                    0, 0, 4))
                                    else:
                                        bulletList.append(
                                            Bullet2(self.X + self.W // 2, self.Y + 25, 180,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 7,
                                                    weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                    0, 0, 4))
                                weaponList[self.weapon].fireSound.play()
                            break
                        if player.X > self.X:  # check 3 pixels along the line of sight
                            losX += 3
                        elif player.X < self.X:
                            losX -= 3
                else:
                    self.attacking = False


        # Moving left and right
        if self.animation != 6:  # Won't work if mob is currently dying
            if player.X > self.X:  # face right if player is on right
                self.fA = True
                if not self.attacking:  # use standing animation if not attacking
                    self.shootCounter = 0
                    self.animation = idleRight
            elif player.X < self.X:  # Face left is player is on left
                self.fA = False
                if not self.attacking:
                    self.shootCounter = 0
                    self.animation = idleLeft

            if abs(
                            player.X - self.X) > self.shootRange or not self.oG:  # Move towards player if not on ground or if outside of shooting range
                if player.X > self.X:  # begin walking to the right
                    self.fA = True
                    self.vX += self.vAx
                    self.animation = right
                elif player.X < self.X:  # begin walking to the left
                    self.fA = False
                    self.vX -= self.vAx
                    self.animation = left
                self.shootCounter = 0
            elif abs(
                            player.X - self.X) < self.avoidance or not self.oG:  # Move away from player if not on ground or inside avoidance area
                if player.X > self.X:  # Move left
                    self.fA = False
                    self.vX -= self.vAx
                    self.animation = left
                elif player.X < self.X:  # Move right
                    self.fA = True
                    self.vX += self.vAx
                    self.animation = right
                self.shootCounter = 0

    def damage(self,amount,type = 0):
        self.health -= amount
        damagePopoff.append(DamageText(self.X+(self.W//2)+random.randint(-30,30),self.Y+random.randint(-10,0),amount,type))

    #def think(self):  # enemy AI
    
    def applyFriction(self):
            if self.vX > 0:  # if self is moving, apply friction
                if self.oG:
                    # Friction on Ground
                    self.vX = min(self.vX, self.vM)
                    self.vX -= friction
                else:
                    # Friction in Air
                    self.vX = min(self.vX, self.vM)
                    self.vX -= airFriction
            elif self.vX < 0:
                if self.oG:
                    # Friction On ground
                    self.vX = max(self.vX, -self.vM)
                    self.vX += friction
                else:
                    # Friction in Air
                    self.vX = max(self.vX, -self.vM)
                    self.vX += airFriction
            elif self.vX in range(1, -1):
                self.vX = 0
    def hitStuff(self):
        mobRect = Rect(self.X, self.Y, self.W, self.H)
        hitRect = [Rect(0, 0, 0, 0)]
        wallRect = [Rect(0, 0, 0, 0)]
        for platTile in playTile[2]:
            if mobRect.move(0, 1).colliderect(Rect(platTile[0])) and (
                            platTile[1] == 0 or platTile[1] == 2):  # if the tile is a platform or an invisible platform
                self.vY = 0
                self.hP = platTile
                if mobRect.bottom < platTile[
                    0].bottom:  # if the mob is clipping into the tile and is closer to the top of it
                    self.Y = platTile[0].top - self.H  # move mob to top of platform
                    self.oG = True
                    self.jumps = 2
                elif mobRect.top > platTile[0].top:  # if mob is closer to bottom
                    self.Y = platTile[0].bottom  # move to bototm
                    self.vY *= -1  # reflect vY
                    self.oG = False
            if mobRect.colliderect(platTile[0]) and platTile[1] == 1:  # if colliding with a wall
                self.oW = True
                self.hW = platTile
                if mobRect.left < platTile[0].left:  # if mob is on the right side of the wall
                    self.X = platTile[0].left - self.W - 1  # move to right
                    self.jumps = 1  # more jumps for jumping off of the wall
                elif mobRect.right > platTile[0].right:
                    self.X = platTile[0].right + 1
                    self.jumps = 1
        if not mobRect.move(0, 1).colliderect(self.hP[0]):  # if player isn't hitting the ground
            self.oG = False
            self.vY += gravity
        if not (mobRect.move(0, 1).colliderect(self.hW[0]) or mobRect.move(0, -1).colliderect(
                self.hW[0])):  # if player isn't hitting a wall
            self.oW = False


class Pickup:  # Class for ammo, health, and credit drops
    def __init__(self, x, y, dropType, amount):
        self.X = x
        self.Y = y
        self.vY = 0
        self.dropType = dropType  # an int that describes what kind of ammo the drop is
        self.amount = amount  # int for ammo amount, string if credits or health

    def fallToGround(self):
        canFall = True
        for i in playTile[2]:
            if i[0].colliderect(
                    Rect(self.X, self.Y, 16, 16).move(0, 1)):  # if pickup is hitting any platform in the level
                self.Y = i[0].top - pickupSprites[self.dropType].get_height()
                self.vY = 0
                canFall = False
                break
        if canFall:
            self.vY += 0.5
            self.Y += int(self.vY)

    def checkCollide(self):  # Checks if player is colliding with the pickup
        if Rect(self.X, self.Y, 16, 16).colliderect(Rect(player.X, player.Y, player.W, player.H)):  # if colliding
            if type(self.amount) == int:  # if the drop is ammo
                player.reserveAmmo[self.dropType] += self.amount  # add ammo to respective reserve
                ammoPickup.play()
                return True
            elif self.amount == 'health' and player.health < player.maxHealth:  # if the drop is health and the player isn't at max health
                healthPickup.play()
                player.health = min(player.maxHealth, player.health + 25)  # add health
                return True
            elif self.amount == 'credits':  # if the drop is credits
                player.money += 50 * random.randint(100, 200)  # Add a random amount of credits
                return True
        return False
class damageArea:
    def __init__(self,shape,size,x,y,colour,duration,damage,tickLength):
        self.shape = shape
        if shape == 0:
            self.w = size[0]
            self.h = size[1]
            self.cRect = Rect(x,y,w,h)
        elif shape == 1:
            self.radius = size
        self.x = x
        self.y = y
        self.colour = colour
        self.duration = duration
        self.damage = damage
        self.tickLength = tickLength
        self.currentTick = 0
    def updateCloud(self):
        if self.currentTick == 0:
            self.currentTick = self.tickLength
            if self.shape == 0:
                for i in enemyList:
                    enemyCenter = (i.X+(i.w//2),i.Y+(i.h//2))
                    if math.hypot(self.x-enemyCenter[0],self.y-enemyCenter[1]) <=self.radius:
                        i.damage(self.damage)
            elif self.shape == 1:
                for i in enemylist:
                    if self.cRect.collidepoint(i.X,i.Y):
                        i.damage(self.damage)
class Bullet2:
    def __init__(self, x, y, angle, damage, faction, range, speed, colour, hitColour, length, gravity, slowdown,
                 thickness, isExplosive=0, explosiveRadius=0, explosiveFalloff=0,
                 fuse=0,isCrit = 0):  # Gravity reduces vY, slowdown decreases vX
        self.x, self.y = x, y
        self.angle = angle
        self.vX, self.vY = speed * cosd(angle), speed * sind(angle)
        self.damage = damage
        self.faction = faction
        self.range = range
        self.speed = speed
        self.colour = colour
        self.hitColour = hitColour
        self.length = length
        self.gravity = gravity
        self.slowdown = slowdown
        self.thickness = thickness
        self.isExplosive = isExplosive
        self.explosiveRadius = explosiveRadius
        self.explosiveFalloff = explosiveFalloff
        self.fuse = fuse
        self.isCrit = isCrit
    def move(self):
        self.x += self.vX
        self.y += self.vY
        if self.vX > 0:
            self.vX -= self.slowdown
        elif self.vX < 0:
            self.vX += self.slowdown
        self.vY += self.gravity
        self.range -= 1

    def draw(self, surface):
        screen.set_at((int(self.x), int(self.y)), self.colour)
        draw.line(surface, self.colour, (self.x + 640 - player.X, self.y + 360 - player.Y), (
            int((self.length * cosd(self.angle)) + self.x + (640 - player.X)),
            int((self.length * sind(self.angle)) + self.y + (360 - player.Y))), self.thickness)


class Weapon:
    def __init__(self, damage, firerate, magSize, reloadSpeed, fireSound, bulletColour, bulletsPerShot, inaccuracy,
                 reloadSound, ammoType, bulletType=0, bulletGravity=0, bulletSpeed=0, bulletLength=0, bulletThickness=0,
                 bulletRange=900, cost=0, wepType=0, isExplosive=0, explosiveRadius=0, explosiveFalloff=0, fuse=0,critChance = 5,critMult = 1.5, fireMode = 0, burstDelay = 1):
        self.damage = damage
        self.firerate = firerate
        self.magSize = magSize
        self.reloadSpeed = reloadSpeed
        self.fireSound = fireSound
        self.bulletColour = bulletColour
        self.bulletsPerShot = bulletsPerShot
        self.inaccuracy = inaccuracy
        self.reloadSound = reloadSound
        self.ammoType = ammoType
        self.bulletType = bulletType
        self.bulletGravity = bulletGravity
        self.bulletSpeed = bulletSpeed
        self.bulletLength = bulletLength
        self.bulletThickness = bulletThickness
        self.bulletRange = bulletRange
        self.cost = cost
        self.wepType = wepType
        self.isExplosive = isExplosive
        self.explosiveRadius = explosiveRadius
        self.explosiveFalloff = explosiveFalloff
        self.fuse = fuse
        self.critChance = critChance
        self.critMult = critMult
        self.fireMode = fireMode
        self.burstDelay = burstDelay

class explosion:
    def __init__(self, x, y, damage, falloff, radius, colour, smokeColour, fuse):
        self.x, self.y = x, y
        self.damage = damage
        self.falloff = falloff
        self.radius = radius
        self.colour = colour
        self.smokeColour = smokeColour
        self.fuse = fuse

    def detonate(self):
        global enemyList, particleList
        hitByExplosive = [False for i in range(len(enemyList))]
        for i in range(0, 360, 15):
            hitEnvironment  = False
            particleList.append(Particle(screen, self.x, self.y, i, self.radius // 5, (255, random.randint(0, 255), 0),random.randint(2,3), 0, 0, 0, 2, 20, 2))
            particleList.append(Particle(screen, self.x, self.y, i, self.radius // 5, self.smokeColour, random.randint(2,3), 0, 0, 0, 2,20, 2))
            for j in range(0, self.radius, 7):
                checkPoint = (int(self.x + (j * cosd(i))), int(self.y + (j * sind(i))))
                for k in playTile[2]:
                    if k[0].collidepoint(checkPoint):
                        hitEnvironment = True
                        break
                if not hitEnvironment:
                    for k in doorList:
                        if k.hitBox.collidepoint(checkPoint):
                            hitEnvironment = True
                            break
                if not hitEnvironment:
                    for l, m in zip(enemyList, range(len(enemyList))):
                        enemyRect = Rect(l.X, l.Y, l.W, l.H)
                        if enemyRect.collidepoint(checkPoint) and not hitByExplosive[m]:
                            l.damage(max(self.damage - (7 * (j * self.falloff)), 0))
                            if l.X+(l.W//2) > self.x:
                                l.vX = max(self.radius-abs(self.x-(l.X+(l.W//2))),0)
                            elif l.X+(l.W//2) > self.x:
                                l.vX = min(-(self.radius-abs(self.x-(l.X+(l.W//2)))),0)
                            l.vY = -3
                            hitByExplosive[m] = True
                elif hitEnvironment:
                    break
        explosionSfx.play()

class DamageText:
    def __init__(self,x,y,amount,type):
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
def sind(deg):
    return math.sin(math.radians(deg))


def cosd(deg):
    return math.cos(math.radians(deg))
def loadSave(fName):
    global purchasedWeapons
    saveFile = open(fName,'rb')
    saveInfo = pickle.load(saveFile)
    saveFile.close()
    return saveInfo
def saveGame(fName):
    saveFile = open('SAVE'+fName+'.txt','wb')
    pickle.dump([purchasedWeapons,fName], saveFile)
    saveFile.close()
def findSaves():
    global savedGames
    saveList = glob.glob('SAVE*.txt')
    for i in saveList:
        savedGames.append(loadSave(i))
def drawCursor():
    draw.circle(screen, WHITE, (int(mx), int(my)), 3)
    draw.circle(screen, BLACK, (int(mx), int(my)), 2)
    if player.reloading>0:
        reloadPercent = player.reloading/weaponList[currentWeapon].reloadSpeed
        for i in range(-90,int(360*reloadPercent)-90):
            draw.line(screen,WHITE,(mx+(5*sind(i)),my+(5*cosd(i))),(mx+(10*sind(i)),my+(10*cosd(i))))
def flipFrames(frameList):  # Reflects the sprites in a spritelist if they're all facing the wrong direction
    flippedList = []  # output
    for i in range(len(frameList)):
        flippedList.append([])  # Create a new list in the output
        flippedList[-1].append([])  # Create a new list in the new list
        for j in frameList[i][0]:
            flippedList[i][0].append(transform.flip(j, True, False))  # append to the new list the flipped frame
        flippedList[i].append(frameList[i][1])  # Append the rate at which the frames should be played
    return flippedList
def angleBetween(point1,point2):
    return math.degrees(math.atan2(point1[0] - point2[0], point1[1] - point2[1])) - 90

def completeFrames(frameList, ogFrames,
                   flipFrameOrder):  # will return a list of frames that contains the frames and their reflected form for use
    for i in range(len(frameList)):
        # frameList is the actual frames
        # ogFrames is the positions of the old frames
        # flipFrame Order is the positions of the new frames
        addToFrameList = []  # Frames and how fast to play them
        flipFrameList = []  # the flipped frames in the current animation set
        workFrame = ogFrames[i]  # the frame
        for j in range(len(frameList[workFrame][0])):
            flippedFrame = transform.flip(frameList[workFrame][0][j], True, False)
            flipFrameList.append(flippedFrame)
        addToFrameList.append(flipFrameList)  # prepare the flipped frames to output
        addToFrameList.append(frameList[workFrame][1])
        frameList.insert(flipFrameOrder[i], addToFrameList)
    for i in range(len(frameList)):
        for j in range(len(frameList[i][0])):
            workFrame = frameList[i][0][j]
            frameList[i][0][j] = transform.scale(workFrame, (int(workFrame.get_width() * 1.5), int(
                workFrame.get_height() * 1.5))).convert_alpha()  # go through framelist scaling everything up 1.5x
    return frameList


def readyController():
    if joystick.get_count() > 0:
        global controllerMode
        mouse.set_visible(False)
        controllerMode = True
        xb360Cont = joystick.Joystick(0)
        xb360Cont.init()
        print("Controller mode initialised")


def swordHit():  # check for sword hits
    global playerRect
    swingBox = Rect(player.X, player.Y, 40, player.H)  # sword area
    for i in enemyList:
        enemyRect = Rect(i.X, i.Y, i.W, i.H)  # enemy area
        # Swing
        if player.fA:  # if player is facing left
            if enemyRect.colliderect(swingBox.move(-swingBox.w, 0)):  # if enemy is colliding with the sword
                i.damage(50)
                break
        elif not player.fA:  # if player is facing right
            if enemyRect.colliderect(swingBox.move(player.W, 0)):
                i.damage(50)
                break


def drawUpperSprite():  # creates a new surface for when the player is standing around and aiming
    global currentWeapon, upperSurf, lUpperSurf
    upperSurf = Surface((22, 20), SRCALPHA)
    upperSurf.blit(frostUpper, (1, 0))  # regular upper half of body
    upperSurf.blit(eval(currentWeapon), (5, 8))  # weapon
    upperSurf.blit(frostArms, (0, 10))  # arms
    upperSurf = transform.scale(upperSurf, (
        int(upperSurf.get_width() * 1.5), int(upperSurf.get_height() * 1.5)))  # scale it all up
    lUpperSurf = transform.flip(upperSurf, False, True)  # left version


def miniMap():  # draws minimap in top left of hud
    mMapSurf = Surface((200, 100), SRCALPHA)
    mMapSurf.fill(WHITE)  # fill with white
    mMapSurf.blit(minimap, (100 - player.X // 7, 50 - player.Y // 7))  # blit scaled down tile
    mMapSurf = transform.rotate(mMapSurf, -1)  # tilt it so it looks like the warframe minimap

    screen.blit(mMapSurf, (5, 5))


def drawHud():  # Draw hud, credits, health, shields, minimap, ammo
    global currentWeapon, weaponList, largeRoboto, screen
    angledHudSec = Surface((300, 43), SRCALPHA)
    ammoHud = Surface((165, 25), SRCALPHA)
    creditHud = Surface((200, 25), SRCALPHA)
    creditDisplay = smallRoboto.render(str(player.money), True, WHITE)  # render current money
    ammoCounter = smallRoboto.render(
        '%10s: %-3d/ %2d' % (currentWeapon, player.mag, player.reserveAmmo[weaponList[currentWeapon].ammoType]), True,
        WHITE)  # render current ammo / ammo reserve
    healthCounter = largeRoboto.render(str(max(0, player.health)), True, (255, 40, 40))  # render health
    shieldCounter = largeRoboto.render(str(max(0, int(player.shield))), True, (100, 170, 255))  # render shields
    angledHudSec.blit(healthCounter, (300 - healthCounter.get_width(), 10))
    creditHud.blit(hudCredit, (0, 5))
    creditHud.blit(creditDisplay, (20, 0))
    draw.line(angledHudSec, (255, 40, 40), (300 - (math.ceil(45 * (max(0, player.health) / player.maxHealth))), 42),
              (300, 42), 3)  # draw line for player health
    angledHudSec.blit(shieldCounter, (245 - shieldCounter.get_width(), 10))
    if player.shield > 0:  # don't show player shields bar if they're at 0
        draw.line(angledHudSec, (100, 170, 255),
                  (245 - (math.ceil(45 * (max(0, player.shield) / player.maxShield))), 42), (245, 42),
                  3)  # draw line for player shields
    ammoHud.blit(ammoCounter, (0, 0))
    rotatedCreditHud = transform.rotate(creditHud, -2)  # rotate so it looks like warframe hud
    rotatedHud = transform.rotate(angledHudSec, 2)
    rotatedAmmoHud = transform.rotate(ammoHud, -2)
    screen.blit(rotatedHud, (965, 2))
    screen.blit(rotatedCreditHud, (10, 690))
    screen.blit(rotatedAmmoHud, (1270 - rotatedAmmoHud.get_width(), 685))
    miniMap()


def checkBullTrajectory(bullAngle, x, y,checkDist,indexPos = None,weapon = True):  # check trajectory of player shots
    # bullAngle is the angle of the bullet
    # x, y is the position the player is at
    global particleList
    hit = False
    startX, startY = x, y
    endX, endY = x, y
    retVal = None
    while not hit:  # loop while the bullet hasn't reached anything
        if math.hypot(startX - x, startY - y) >= checkDist:  # if bullet has checked 900 pixels distance
            hit = True
            endX, endY = x, y
            break
        for i in playTile[2]:  # if bullet hits environment
            if i[0].collidepoint(x, y) and i[1] != 3:
                hit = True
                endX, endY = x, y
                if weapon:
                    for i in range(5):  # make particles on the environment at the hit location
                        particleList.append(
                            Particle(screen, endX, endY, -bullAngle + 180, 5, weaponList[currentWeapon].bulletColour, 4,
                                     0.2, 0.2, 0.4, 1, 10))
                retVal = None
        for i in doorList:
            if i.hitBox.collidepoint(x,y):
                hit = True
                endX, endY = x, y
                if weapon:
                    for i in range(5):  # make particles on the environment at the hit location
                        particleList.append(
                            Particle(screen, endX, endY, -bullAngle + 180, 5, weaponList[currentWeapon].bulletColour, 4,
                                     0.2, 0.2, 0.4, 1, 10))
        for i in range(len(enemyList)):  # if bullet hits enemy
            eInfo = enemyList[i]
            mobRect = Rect(eInfo.X, eInfo.Y, eInfo.W, eInfo.H)  # enemy hitbox
            if mobRect.collidepoint(x, y) and eInfo.dying == 0:  # if it hits an enemy that isn't dying
                if indexPos == None:
                    hit = True
                    endX, endY = x, y
                    retVal = i
                    for i in range(5):  # add particles for BLOOD
                        particleList.append(Particle(screen, endX, endY, bullAngle + 180, 20, [255, 0, 0], 3, 1, 0.2, 0, 1, 10))
                elif indexPos == i:
                    hit = True
                    endX, endY = x, y
                    retVal = i
        x += 7 * cosd(bullAngle)  # move bullet checking coordinates
        y += 7 * sind(-bullAngle)
    if indexPos == None:
        bulletTrailList.append([startX, startY, endX, endY])  # queue bullet trail for drawing
    return retVal


def calcBullets():  # check if the enemy bullets hit anything
    global regenTimer, playerRect

    for i in range(len(bulletList) - 1, -1, -1):
        nextBullet = False  # will stop checking things if the bullet no longer exists
        for j in playTile[2]:
            if j[0].collidepoint(bulletList[i].x, bulletList[i].y) and j[1] != 3:  # if bullet hit a platform or wall
                if bulletList[i].isExplosive:
                    explosiveList.append(explosion(bulletList[i].x-bulletList[i].vX, bulletList[i].y-bulletList[i].vY, bulletList[i].damage,
                                                   bulletList[i].explosiveFalloff, bulletList[i].explosiveRadius,
                                                   weaponList[currentWeapon].bulletColour, (200, 200, 200), weaponList[currentWeapon].fuse))
                del bulletList[i]
                nextBullet = True
                break
        if not nextBullet:
            for j in doorList:
                if j.hitBox.collidepoint(bulletList[i].x, bulletList[i].y):
                    if bulletList[i].isExplosive:
                        explosiveList.append(
                            explosion(bulletList[i].x - bulletList[i].vX, bulletList[i].y - bulletList[i].vY,
                                      bulletList[i].damage,
                                      bulletList[i].explosiveFalloff, bulletList[i].explosiveRadius,
                                      weaponList[currentWeapon].bulletColour, (200, 200, 200),
                                      weaponList[currentWeapon].fuse))
                    del bulletList[i]
                    nextBullet = True
                    break
        if not nextBullet:
            for j in range(len(enemyList) - 1, -1, -1):  # checking player bullets
                enemyRect = Rect(enemyList[j].X, enemyList[j].Y, enemyList[j].W, enemyList[j].H)
                if enemyRect.collidepoint(bulletList[i].x, bulletList[i].y) and bulletList[i].faction == 1 and \
                                enemyList[j].dying == 0:  # if bullet hits an enemy that's not dying
                    if bulletList[i].isExplosive:
                        explosiveList.append(explosion(bulletList[i].x, bulletList[i].y, bulletList[i].damage,
                                                       bulletList[i].explosiveFalloff, bulletList[i].explosiveRadius,
                                                       weaponList[currentWeapon].bulletColour, (200, 200, 200), 0))
                    else:
                        enemyList[j].damage(bulletList[i].damage,bulletList[i].isCrit)
                    bulletList[i].range = 0
        if not nextBullet:
            if len(bulletList) > 0:
                if playerRect.collidepoint(bulletList[i].x, bulletList[i].y) and bulletList[i].faction == 0 and \
                                bulletList[i].range > 0:  # if bullet is still alive and it hit the player
                    if player.shield != player.maxShield:
                        regenTimer = 200  # begin shield regen
                    if player.shield > 0:  # if the player has shields
                        player.shield -= bulletList[i].damage  # hit shields
                    else:
                        player.health = max(0, player.health - bulletList[i].damage)  # hit health
                    bulletList[i].range = 0
                else:
                    bulletList[i].move()
                if bulletList[i].range <= 0:
                    del bulletList[i]


def drawUpper(playerX, playerY):  # Also includes shooting
    global upperSurf, currentWeapon, particleList, keysIn, canClick, aimAngle,angleIn
    smallestLimit = -180
    largestLimit = 180
    playerWeapon = weaponList[currentWeapon]
    if not player.fA:
        rotUpper = transform.rotate(upperSurf, angleIn)  # rotate upper body
        screen.blit(rotUpper, (playerX - rotUpper.get_width() // 2, playerY - rotUpper.get_height() // 2 - 2))
    else:
        rotUpper = transform.rotate(lUpperSurf, angleIn)  # rotate upper body
        screen.blit(rotUpper, (playerX - 5 - rotUpper.get_width() // 2, playerY - rotUpper.get_height() // 2 - 2))

    if mb[0] and player.shootCooldown == 0 and player.mag > 0 and player.reloading == 0:  # if player can shoot and is trying to shoot
        player.shootCooldown = playerWeapon.firerate  # fire rate timer
        if playerWeapon.fireMode == 0:
            fireWeapon(angleIn)
        elif playerWeapon.fireMode >= 1:
            if canClick:
                if currentWeapon != 'targeter':
                    fireWeapon(angleIn)
                else:
                    for i in range(len(targeterList)):
                        if targeterList[i][1]<=0:
                            queuedShots.append([i*10,180+targeterList[i][2]])
                canClick = False
                for i in range(playerWeapon.burstDelay,playerWeapon.burstDelay*playerWeapon.fireMode,playerWeapon.burstDelay):
                    queuedShots.append([i,angleIn])
    elif mb[0] and not player.mag and not player.reloading:  # if you have no ammo but are trying to shoot
        weaponList[currentWeapon].reloadSound.play()
        player.reloading += 1

    player.fA = -270 < angleIn < -90  # change player direction if they are aiming on the left or right
def fireWeapon(angleIn):
    if player.mag > 0:
        for i in range(10):  # add particles at muzzle of gun
            particleList.append(
                Particle(screen, player.X + (player.W // 2) + 20 * cosd(angleIn), player.Y + 20 - 20 * sind(angleIn),
                         -angleIn, 5, weaponList[currentWeapon].bulletColour, 4, 0.1, 0.1, 7, 2, 20))
        weaponList[currentWeapon].fireSound.stop()
        weaponList[currentWeapon].fireSound.play()
        player.mag -= 1
        for i in range(weaponList[currentWeapon].bulletsPerShot):  # check if the bullet hit an enemy
            angle = angleIn + random.randint(-weaponList[currentWeapon].inaccuracy, weaponList[
                currentWeapon].inaccuracy)  # angle from player's upper body to mouse
            if weaponList[currentWeapon].bulletType == 0:
                enemyHit = playerShoot(weaponList[currentWeapon], angle)
                if type(enemyHit) == int:  # if it hit an enemy
                    if random.randint(0, 100) < weaponList[currentWeapon].critChance:
                        enemyList[enemyHit].damage(weaponList[currentWeapon].damage * weaponList[currentWeapon].critMult, 1)
                    else:
                        enemyList[enemyHit].damage(weaponList[currentWeapon].damage)
            elif weaponList[currentWeapon].bulletType == 1:
                if currentWeapon == 'ignis':
                    if random.randint(0, 100) < weaponList[currentWeapon].critChance:
                        bulletList.append(
                            Bullet2(player.X + player.W // 2, player.Y + 20, -angle,
                                    weaponList[currentWeapon].damage * weaponList[currentWeapon].critMult,
                                    1, weaponList[currentWeapon].bulletRange,
                                    weaponList[currentWeapon].bulletSpeed + random.randint(-2, 2),
                                    (255, random.randint(0, 255), 0), weaponList[currentWeapon].bulletColour,
                                    weaponList[currentWeapon].bulletLength, weaponList[currentWeapon].bulletGravity, 0,
                                    weaponList[currentWeapon].bulletThickness, isCrit=1))
                    else:
                        bulletList.append(
                            Bullet2(player.X + player.W // 2, player.Y + 20, -angle,
                                    weaponList[currentWeapon].damage,
                                    1, weaponList[currentWeapon].bulletRange,
                                    weaponList[currentWeapon].bulletSpeed + random.randint(-2, 2),
                                    (255, random.randint(0, 255), 0), weaponList[currentWeapon].bulletColour,
                                    weaponList[currentWeapon].bulletLength, weaponList[currentWeapon].bulletGravity, 0,
                                    weaponList[currentWeapon].bulletThickness))
                else:
                    if random.randint(0, 100) < weaponList[currentWeapon].critChance:
                        bulletList.append(
                            Bullet2(player.X + player.W // 2, player.Y + 20, -angle,
                                    weaponList[currentWeapon].damage * weaponList[currentWeapon].critMult,
                                    1, weaponList[currentWeapon].bulletRange, weaponList[currentWeapon].bulletSpeed,
                                    weaponList[currentWeapon].bulletColour, weaponList[currentWeapon].bulletColour,
                                    weaponList[currentWeapon].bulletLength, weaponList[currentWeapon].bulletGravity, 0,
                                    weaponList[currentWeapon].bulletThickness, weaponList[currentWeapon].isExplosive,
                                    weaponList[currentWeapon].explosiveRadius, weaponList[currentWeapon].explosiveFalloff,
                                    weaponList[currentWeapon].fuse, isCrit=1))
                    else:
                        bulletList.append(
                            Bullet2(player.X + player.W // 2, player.Y + 20, -angle,
                                    weaponList[currentWeapon].damage,
                                    1, weaponList[currentWeapon].bulletRange, weaponList[currentWeapon].bulletSpeed,
                                    weaponList[currentWeapon].bulletColour, weaponList[currentWeapon].bulletColour,
                                    weaponList[currentWeapon].bulletLength, weaponList[currentWeapon].bulletGravity, 0,
                                    weaponList[currentWeapon].bulletThickness, weaponList[currentWeapon].isExplosive,
                                    weaponList[currentWeapon].explosiveRadius,
                                    weaponList[currentWeapon].explosiveFalloff,
                                    weaponList[currentWeapon].fuse))
def possibleangleIn():
    global angleIn
    if keysIn[K_a]:
        smallestLimit = -225
        largestLimit = -135
    elif keysIn[K_d]:
        smallestLimit = -45
        largestLimit = 45
    else:
        smallestLimit = -270
        largestLimit = 90
    angleIn = min(max(math.degrees(math.atan2(mx - 660, my - 376+(36-pic.get_height()))) - 90, smallestLimit), largestLimit)

def makeTile(tileInfo):  # draw the tile
    global levelAtlas, visualOff
    tileSize = tileInfo.pop(0)
    tileVisual = Surface(tileSize, SRCALPHA)
    for i in tileInfo:
        if i[1] != 2 and i[1] != 3:  # if tile is a platform or a wall and not an invisible platform or spawn box
            draw.rect(tileVisual, (0, 0, 0), i[0])  # draw a black box
            tileVisual.blit(levelAtlas, i[0].topleft, (0, 0, 16, 16))  # draw corner pieces
            tileVisual.blit(levelAtlas, i[0].move(-16, 0).topright, (32, 32, 16, 16))
            tileVisual.blit(levelAtlas, i[0].move(0, -16).bottomleft, (16, 64, 16, 16))
            tileVisual.blit(levelAtlas, i[0].move(-16, -16).bottomright, (80, 32, 16, 16))
            if i[0].width > 32:  # throughout the length of the box, draw the sides and bottom and top textures
                for j in range(16, i[0].width - 16, 16):
                    tileVisual.blit(levelAtlas, (i[0].left + j, i[0].top), (16, 112, 16, 16))
                    tileVisual.blit(levelAtlas, (i[0].left + j, i[0].bottom - 16), (48, 128, 16, 16))
            if i[0].height > 32:
                for j in range(16, i[0].height - 16, 16):
                    tileVisual.blit(levelAtlas, (i[0].left, i[0].top + j), (128, 32, 16, 16))
                    tileVisual.blit(levelAtlas, (i[0].move(-16, 0).right, i[0].top + j), (0, 16, 16, 16))
        elif i[1] == 3:  # if the tile is a spawn box the draw the liset (ship)
            tileVisual.blit(lisetSprite, i[0].move(-50, -20).topleft)
    return (tileSize, tileVisual, tileInfo)


def keysDown(keys):  # check what keys are being held
    global player, canUseSword, currentFrame
    if keys[K_a]:
        player.vX -= player.vAx  # moves left
        player.fA = True  # player is facing left
    if (keys[K_w] or keys[K_SPACE]) and player.oW and (keys[K_a] or keys[K_d]):  # if player is wall running
        player.vY = max(-4, player.vY - 0.5)  # move player up
        if player.fA:  # wall running animation
            player.animation = 9
        elif not player.fA:
            player.animation = 8
    if keys[K_d]:
        player.vX += player.vAx  # moves right
        player.fA = False  # player is facing right
    if keys[K_e] and not keys[K_a] and not keys[K_d]:  # if player is stationary and meleeing
        if player.fA:
            player.animation = 7  # melee animation
        elif not player.fA:
            player.animation = 6
        if (currentFrame == 0 or currentFrame == 2):  # frames that have the sword swipe
            if canUseSword:
                swordHit()  # check if the sword hit anything
                sword1.play()  # make sword swinging sound
                canUseSword = False  # can only hit one target per swing
                # reflecting bullets
            swingBox = Rect(player.X, player.Y, 40, player.H)  # sword area
            for i in bulletList:  # go through list of enemy bullets
                if player.fA:  # if player is facing left
                    if swingBox.move(-swingBox.w, 0).collidepoint(i.x, i.y):  # check if bullet is hitting sword
                        i.angle = 180
                        i.vX, i.vY = i.speed * cosd(i.angle), i.speed * sind(i.angle)
                        i.faction = 1  # change bullet into player's bullet
                        break
                elif not player.fA:
                    if swingBox.move(player.W, 0).collidepoint(i.x,
                                                               i.y):  # i.hitRect.colliderect(swingBox.move(player.W,0)):
                        i.angle = 0
                        i.vX, i.vY = i.speed * cosd(i.angle), i.speed * sind(i.angle)
                        i.faction = 1
                        break
        elif currentFrame == 1 or currentFrame == 3:  # frames that no longer have the sword swipe
            canUseSword = True
    elif player.oG:  # if the player isn't doing anything and is stationary
        if player.fA:
            player.animation = idleLeft
        elif not player.fA:
            player.animation = idleRight

def targeterMech():
    global angleIn
    for i in enemyList:
        if player.fA:
            playerToEnemy = angleBetween((player.X,player.Y+player.H//2),(i.X+i.W//2,i.Y+i.H//2))
        else:
            playerToEnemy = angleBetween((player.X+player.W, player.Y + player.H // 2),
                                         (i.X + i.W // 2, i.Y + i.H // 2))
        aimFromEnemy = int(angleIn-angleBetween((player.X,player.Y),(i.X,i.Y)))
        if checkBullTrajectory(180+playerToEnemy,player.X,player.Y,700,enemyList.index(i),False) == enemyList.index(i) and abs(aimFromEnemy) in range(140,210):
            addToList = True
            for j in targeterList:
                if i in j:
                    addToList = False
            if addToList:
                targeterList.append([i,120,180+playerToEnemy])
        elif checkBullTrajectory(180+playerToEnemy,player.X+player.W,player.Y,700,enemyList.index(i),False) == enemyList.index(i) and abs(aimFromEnemy) in range(140,210):
            addToList = True
            for j in targeterList:
                if i in j:
                    addToList = False
            if addToList:
                targeterList.append([i,120,180+playerToEnemy])
        else:
            for j in targeterList:
                if i in j:
                    del targeterList[targeterList.index(j)]
                    break
    for i in range(len(targeterList)-1,-1,-1):
        mobInfo = targeterList[i]
        if mobInfo[1] > 0:
            if player.fA:
                draw.line(screen,(255,0,0),(640,375),(640-player.X+mobInfo[0].X+(mobInfo[0].W//2),360-player.Y+mobInfo[0].Y+(mobInfo[0].H//2)))
            else:
                draw.line(screen,(255,0,0),(670,375),(640-player.X+mobInfo[0].X+(mobInfo[0].W//2),360-player.Y+mobInfo[0].Y+(mobInfo[0].H//2)))
            targeterList[i][1] -= 1
        elif mobInfo[1]<= 0:
            if player.fA:
                draw.line(screen,(0,255,0),(640,375),(640-player.X+mobInfo[0].X+(mobInfo[0].W//2),360-player.Y+mobInfo[0].Y+(mobInfo[0].H//2)))
            else:
                draw.line(screen,(0,255,0),(670,375),(640-player.X+mobInfo[0].X+(mobInfo[0].W//2),360-player.Y+mobInfo[0].Y+(mobInfo[0].H//2)))
        targeterList[i][2] = angleBetween((player.X+player.W//2,player.Y+player.H//2),(mobInfo[0].X+mobInfo[0].W//2,mobInfo[0].Y+mobInfo[0].H//2))
        if mobInfo[0].health<=0:
            del targeterList[i]

def drawStuff(tileSurf, tileSize, keys):  # render everything
    global player, frames, animation, visualOff, pic, currentFrame, bulletTrailList
    screen.fill((0, 0, 0))
    if keys[K_a] and player.oG:  # conditional animations
        player.animation = left
    elif keys[K_d] and player.oG:
        player.animation = right
    elif player.fA and not player.oG and not player.oW:
        player.animation = jumpLeft
    elif not player.fA and not player.oG and not player.oW:
        player.animation = jumpRight
    elif player.fA and player.oG and player.animation != 7 and player.animation != 8:
        player.animation = idleLeft
    elif not player.fA and player.oG and player.animation != 6 and player.animation != 9:
        player.animation = idleRight

    pic = playerFrames[player.animation][0][player.frame // playerFrames[player.animation][1] % len(
        playerFrames[player.animation][0])]  # current frame to show
    player.frame += 1
    for i in doorList:
        i.draw()
    screen.blit(tileSurf, (640 - player.X, 360 - player.Y))  # blit the level
    moveParticles()
    for i in damagePopoff:
        screen.blit(i.renderedText,(640-player.X+i.x,360-player.Y+i.y))
    for i in bulletList:
        i.draw(screen)
    for i in range(len(pickupList)):
        screen.blit(pickupSprites[pickupList[i].dropType],
                    (640 - player.X + pickupList[i].X, 360 - player.Y + pickupList[i].Y))  # draw the pickups/drops
    for i in range(len(bulletTrailList) - 1, -1, -1):  # draw the bullet trails from the player
        draw.line(screen, weaponList[currentWeapon].bulletColour,
                  (640 - player.X + bulletTrailList[i][0], 360 - player.Y + bulletTrailList[i][1]),
                  (640 - player.X + bulletTrailList[i][2], 360 - player.Y + bulletTrailList[i][3]))
    bulletTrailList = []
    for i in enemyList:

        if i.enemyType == 0:  # draw the enemies based on their type
            enemyPic = crewmanFrames[i.animation][0][
                i.frame // crewmanFrames[i.animation][1] % len(crewmanFrames[i.animation][0])]
        elif i.enemyType == 1:
            enemyPic = moaFrames[i.animation][0][i.frame // moaFrames[i.animation][1] % len(moaFrames[i.animation][0])]
        elif i.enemyType == 2:
            enemyPic = sCrewmanFrames[i.animation][0][
                i.frame // sCrewmanFrames[i.animation][1] % len(sCrewmanFrames[i.animation][0])]
        i.frame += 1
        screen.blit(enemyPic, (640 - player.X + i.X, 379 - player.Y + i.Y + (25 - enemyPic.get_height())))
        draw.line(screen, (255, 40, 40), (640 - player.X + i.X + (30 * max(0, i.health) // i.maxHealth),
                                          360 - player.Y + i.Y + (25 - enemyPic.get_height())),
                  (640 - player.X + i.X, 360 - player.Y + i.Y + (25 - enemyPic.get_height())))
    currentFrame = player.frame // playerFrames[player.animation][1] % len(
        playerFrames[player.animation][0])  # the current frame for use in other functions
    screen.blit(pic, (640 + additionalOffsets[player.animation][
        player.frame // playerFrames[player.animation][1] % len(playerFrames[player.animation][0])],
                      360 + (36 - pic.get_height())))  # blit the player on the center of the screen
    if not (not player.oG or player.animation == 7 or player.animation == 6):  # if the player isn't moving or meleeing
        drawUpper(660, 376 + (36 - pic.get_height()))
    drawHud()


def moveParticles():
    for i in range(len(particleList) - 1, -1, -1):
        particleList[i].moveParticle()
        if not particleList[i].live:  # remove if dead
            del particleList[i]


def spawnEnemies():
    mobSpawnY = player.Y - 500  # height at which the mob should spawn
    if len(enemyList) < 3:  # if there are less than 2 enemies
        for i in range(3):  # spawn 3
            newEnemyType = random.randint(0, 2)  # pick random enemy type
            if newEnemyType == 0:  # refer to mob
                enemyList.append(
                    Mob(player.X + random.choice([-1200, 1200]), mobSpawnY + 50, 30, 45, 0, 0, 3 + random.random(), 0.3,
                        False, 1, weapon='dera', avoidance=50 + random.randint(-5, 60),
                        shootRange=150 + random.randint(-10, 10)))
            elif newEnemyType == 1:
                enemyList.append(
                    Mob(player.X + random.choice([-1200, 1200]), mobSpawnY + 50, 45, 45, 0, 0, 4 + random.random(), 0.3,
                        False, 1, weapon='laser', enemyType=1, avoidance=40 + random.randint(-5, 30), health=150,
                        shootRange=130 + random.randint(-20, 10)))
            elif newEnemyType == 2:
                enemyList.append(
                    Mob(player.X + random.choice([-1200, 1200]), mobSpawnY + 50, 45, 45, 0, 0, 2 + random.random(), 0.3,
                        False, 1, weapon='lanka', enemyType=2, avoidance=430 + random.randint(-5, 40),
                        shootRange=500 + random.randint(0, 100), health=60))


def makeNewLevel(levelLength):  # stitches the rects from different tiles together
    levelOut = []
    tileH = 0
    levelSeq = [0]
    for i in range(levelLength):
        levelSeq.append(random.randint(1, len(drawTiles) - 1))  # add tile to the list of tiles
    xOff, yOff = 0, 0
    checkPlatList = []
    stitchedLevel = []
    rectOuts = []
    for i in range(len(levelSeq)):  # place tiles together
        tileEnter = int(tileIO[levelSeq[i]][0])
        lastTileExit = int(tileIO[levelSeq[i - 1]][1])
        yOff += lastTileExit - tileEnter  # difference in entrance and exit heights
        for plat in tileRects[levelSeq[i]]:
            stitchedLevel.append([plat[0].move(xOff, yOff), plat[1]])
        xOff += tileSizes[levelSeq[i]][0]  # width of tile
        tileH += tileSizes[levelSeq[i]][1]  # height of tiles
        # Placing rects together
    for i in stitchedLevel:
        if i[1] == 0:
            checkPlatList.append(
                [[i[0][1], i[0][0], i[0][2], i[0][3]], i[1]])  # Because adjacent tiles should have same height first
        else:
            levelOut.append(i)  # walls and invisible platforms won't be stitched together
    checkPlatList.sort()
    while len(checkPlatList) > 1:  # begin stitching tiles that are adjacent and are the same height together
        pCheck = [checkPlatList[1][0][1], checkPlatList[1][0][0], checkPlatList[1][0][2],
                  checkPlatList[1][0][3]]  # Change back to original after it's been sorted
        previousPlat = [checkPlatList[0][0][1], checkPlatList[0][0][0], checkPlatList[0][0][2], checkPlatList[0][0][3]]
        if (previousPlat[0] + previousPlat[2] == pCheck[0] or Rect(previousPlat).colliderect(pCheck)) and pCheck[1] == previousPlat[1]:  # if platforms are at the same height and are adjacent or colliding
            unionedRect = Rect(previousPlat).union(Rect(pCheck))  # union the tiles
            checkPlatList.insert(2, [[unionedRect[1], unionedRect[0], unionedRect[2], unionedRect[3]],
                                     0])  # Change back into height prioritized format
            del checkPlatList[0]
            del checkPlatList[0]
        else:
            if [Rect(pCheck), 0] not in levelOut and Rect(pCheck).collidelist(
                    rectOuts) == -1:  # if not able to be unioned
                levelOut.append([Rect(previousPlat), 0])  # add to levelout
                rectOuts.append(Rect(previousPlat))
            del checkPlatList[0]
    levelOut.append(
        [Rect([checkPlatList[0][0][1], checkPlatList[0][0][0], checkPlatList[0][0][2], checkPlatList[0][0][3]]),
         0])  # add last platform
    levelOut.insert(0, (xOff, tileH))  # insert information about tile width and height
    return levelOut


def playerShoot(weapon, angle):  # finds what the player hit
    global pic, movedTileTops, mx, my
    retVal = None
    if player.fA:
        retVal = checkBullTrajectory(angle, player.X, player.Y + 20, weaponList[currentWeapon].bulletRange)
    else:
        retVal = checkBullTrajectory(angle, player.X + player.W , player.Y + 20, weaponList[currentWeapon].bulletRange)
    return retVal


def fixLevel(levelIn):  # Moves the level so that it isn't outside of the bounding box
    global visualOff, mobSpawnY, spawnX, spawnY, movedTileTops
    platHeights = []
    platTypes = []
    movedTileTops = []
    newTile = [levelIn.pop(0)]
    for i in levelIn:
        platHeights.append(i[0].top)  # heights of the platforms
        platTypes.append(i[1])  # types of the platform (wall, platform, invisible platform, etc.)
    visualOff = min(platHeights)  # highest tile
    for i in levelIn:  # move everything so the highest tile still has 1280 pixels above it
        movedRect = i[0].move(0, abs(visualOff) + 1280)
        movedTileTops.append(movedRect.top)
        newTile.append([movedRect, i[1]])
        if i[1] == 3:  # make the player's spawn location the spawn box's coordinates
            spawnX, spawnY = newTile[-1][0].topleft
        if i[1] == 4:
            doorList.append(Door(newTile[-1][0].topleft,4,15,60,80,corpDoor1))
            del newTile[-1]
    newTile.append([Rect(-16, min(movedTileTops) - 720, 20000, 32), 2])  # platform so player can't leave level
    newTile.append([Rect(-16, min(movedTileTops) - 720, 32, newTile[0][1]), 1])  # wall on left
    newTile.append([Rect(newTile[0][0] - 16, min(movedTileTops) - 720, 32, newTile[0][1]), 1])  # wall on right
    return newTile


def pauseMenu():
    global running, animationStatus, menuAnimation, mx, my, mb, gameState, canClick
    options = ['Back To Game', 'Return To Ship', 'Quit']
    for i in range(len(options)):  # draw the options
        optionRect = Rect(500, 70 * i + 160, 340, 60)
        if optionRect.collidepoint((mx, my)):  # if mouse is colliding with an option
            draw.rect(screen, WHITE, optionRect)  # highlight it
            draw.rect(screen, (0, 0, 255), optionRect, 2)
            optionText = largeRoboto.render(options[i], True, BLACK)
            screen.blit(optionText, (670 - optionText.get_width() // 2, 70 * i + 170))
            if mb[0] == 1:
                draw.rect(screen, (255, 0, 0), optionRect, 2)
                option = i
                if option == 0:  # do what the option picked was
                    closeMenu.play()
                    animationStatus = -1
                    menuAnimation = 20
                elif option == 1:
                    canClick = False
                    gameState = 'ship'
                elif option == 2:
                    running = False
        else:  # draw the boxes with regular colouring
            draw.rect(screen, BLACK, optionRect)
            draw.rect(screen, (0, 0, 255), optionRect, 2)
            optionText = largeRoboto.render(options[i], True, WHITE)
            screen.blit(optionText, (670 - optionText.get_width() // 2, 70 * i + 170))


def shipMenu():
    global gameState, playTile, drawnmap, minimap, mb, typeSortedWeapons, purchasedWeapons, weaponCosts, rotPos, selectedStoreProduct, currentWeapon, canClick
    screen.blit(storeBackdrop, (0, 0))
    rifleRect = Rect(190, 190, 70, 70)
    shottyRect = Rect(190, 530, 70, 70)
    sniperRect = Rect(1020, 190, 70, 70)
    heavyRect = Rect(1020, 530, 70, 70)
    rifleWheelRect = Rect(70, 70, 300, 300)
    shottyWheelRect = Rect(70, 410, 300, 300)
    sniperWheelRect = Rect(900, 70, 300, 300)
    heavyWheelRect = Rect(900, 410, 300, 300)
    equipButton = Rect(480, 540, 100, 40)
    startButton = Rect(560, 660, 140, 50)
    buttonRects = (rifleRect, shottyRect, sniperRect, heavyRect)
    wheelRects = (rifleWheelRect, shottyWheelRect, sniperWheelRect, heavyWheelRect)
    buttonColours = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0))
    buttonText = ('Rifles', 'Shotguns', 'Snipers', 'Heavies')
    weaponStatNames = ['Damage', 'Fire Rate', 'Magazine', 'Reload Speed', 'Accuracy', 'Projectiles']
    weaponStatIDs = ['damage', 'firerate', 'magSize', 'reloadSpeed', 'inaccuracy', 'bulletsPerShot']
    weaponSpecialStats = ['isExplosive','critChance','fireMode']
    weaponStatsReq = [0,20,1]
    specStatOffset = 0
    for i, j, k, l, m in zip(buttonRects, buttonText, buttonColours, wheelRects, range(4)):
        buttonCenter = (i.x + (i.width // 2), i.y + (i.height // 2))
        # draw.rect(screen,BLACK,i)
        renderedButtonText = micRoboto.render(j, True, WHITE)
        # draw.rect(screen,k,l)

        if l.collidepoint(mx, my):
            canSpin = True
            draw.circle(screen, (200, 200, 200), buttonCenter, l.width // 3)
            draw.circle(screen, WHITE, buttonCenter, l.width // 3 - 5)
            draw.circle(screen, k, buttonCenter, i.width // 2)
            for n, o in zip(typeSortedWeapons[m], range(len(typeSortedWeapons[m]))):
                bubbleSeperation = 360 // len(typeSortedWeapons[m])
                circlePos = (int((l.width // 3) * cosd(bubbleSeperation * o + rotPos[m]) + buttonCenter[0]),
                             int((l.width // 3) * sind(bubbleSeperation * o + rotPos[m])) + buttonCenter[1])
                weaponIcon = eval(n)
                bubbleBox = Rect(circlePos[0] - 30, circlePos[1] - 30, 60, 60)
                draw.circle(screen, k, circlePos, 15)
                screen.blit(weaponIcon, (
                    circlePos[0] - (weaponIcon.get_width() // 2), circlePos[1] - (weaponIcon.get_height() // 2)))
                if bubbleBox.collidepoint(mx, my):
                    canSpin = False
                    draw.circle(screen, k, circlePos, 30)
                    weaponIcon = transform.scale(weaponIcon, (weaponIcon.get_width() * 2, weaponIcon.get_height() * 2))
                    screen.blit(weaponIcon, (
                        circlePos[0] - (weaponIcon.get_width() // 2), circlePos[1] - (weaponIcon.get_height() // 2)))
                    if mb[0]:
                        selectedStoreProduct = n
                else:
                    draw.circle(screen, k, circlePos, 15)
                    screen.blit(weaponIcon, (
                        circlePos[0] - (weaponIcon.get_width() // 2), circlePos[1] - (weaponIcon.get_height() // 2)))
            if canSpin:
                rotPos[m] += 0.1
        else:
            rotPos[m] = 0
            draw.circle(screen, (200, 200, 200), buttonCenter, l.width // 4)
            draw.circle(screen, WHITE, buttonCenter, l.width // 4 - 5)
            draw.circle(screen, (120, 120, 120), buttonCenter, i.width // 2)
        screen.blit(renderedButtonText, (buttonCenter[0] - (renderedButtonText.get_width() // 2),
                                         buttonCenter[1] - (renderedButtonText.get_height() // 2)))
    # Weapon Stats Card
    draw.rect(screen, (140, 140, 140), (470, 50, 340, 540))
    if not selectedStoreProduct == '':
        draw.rect(screen, (100, 100, 100), (480, 60, 320, 300))
        weaponIcon = eval(selectedStoreProduct)
        weaponIcon = transform.scale(weaponIcon, (weaponIcon.get_width() * 10, weaponIcon.get_height() * 10))
        weaponIcon = transform.rotate(weaponIcon, 45)
        screen.blit(weaponIcon, (640 - (weaponIcon.get_width() // 2), 210 - (weaponIcon.get_height() // 2)))
        weaponNameRender = smallRoboto.render('"%s"' % (selectedStoreProduct.title()), True, (255, 255, 255))
        screen.blit(weaponNameRender, (640 - (weaponNameRender.get_width() // 2), 370))
        for i,j,k in zip(weaponSpecialStats,weaponStatsReq,range(len(weaponSpecialStats))):
            if eval('weaponList[selectedStoreProduct].'+i) > j:
                screen.blit(specialIconList[k],(784-specStatOffset,380))
                specStatOffset+=18
        for i, j, k in zip(weaponStatNames, range(6), weaponStatIDs):
            weaponStatRender = smallRoboto.render(i, True, (255, 255, 255))
            screen.blit(weaponStatRender, (480, 20 * j + 400))
            weaponStatValue = eval('weaponList[selectedStoreProduct].%s' % (k))
            if k == 'reloadSpeed' or k == 'firerate':
                weaponStatValue = round(weaponStatValue / 60, 2)
                if k == 'reloadSpeed':
                    weaponStatValue = str(weaponStatValue) + ' s'
                elif k == 'firerate':
                    weaponStatValue = str(round(1 / weaponStatValue, 1)) + ' /s'
            elif k == 'inaccuracy':
                weaponStatValue = str(int((180 - weaponStatValue) / 1.8)) + '%'
            weaponStatValueRender = smallRoboto.render(str(weaponStatValue), True, (255, 255, 255))
            screen.blit(weaponStatValueRender, (800 - weaponStatValueRender.get_width(), 20 * j + 400))
        # Buy and equip button
        if not purchasedWeapons[weaponNamesList.index(selectedStoreProduct)]:
            weaponCostRender = micRoboto.render('%d/%d' % (weaponList[selectedStoreProduct].cost, player.money), True,
                                                (255, 255, 255))
            buyTextRender = micRoboto.render('Buy', True, (255, 255, 255))
            buyButton = Rect(480, 540, weaponCostRender.get_width() + 30, 40)
            if player.money >= weaponList[selectedStoreProduct].cost:
                if buyButton.collidepoint(mx, my):
                    draw.rect(screen, (100, 255, 100), buyButton)
                    if mb[0] == 1:
                        canClick = False
                        player.money -= weaponList[selectedStoreProduct].cost
                        purchasedWeapons[weaponNamesList.index(selectedStoreProduct)] = True
                else:
                    draw.rect(screen, (0, 200, 0), buyButton)
            else:
                draw.rect(screen, (200, 0, 0), (480, 540, weaponCostRender.get_width() + 30, 40))
            screen.blit(weaponCostRender, (505, 560))
            screen.blit(hudCredit, (490, 563))
            screen.blit(buyTextRender, (490, 543))
        # Equip button
        elif not selectedStoreProduct == currentWeapon:
            equipText = smallRoboto.render('Equip', True, (255, 255, 255))
            if equipButton.collidepoint(mx, my):
                draw.rect(screen, (0, 0, 255), equipButton)
                if mb[0] and canClick:
                    currentWeapon = selectedStoreProduct
            else:
                draw.rect(screen, (100, 100, 180), equipButton)
            screen.blit(equipText, (530 - (equipText.get_width() // 2), 545))
        elif selectedStoreProduct == currentWeapon:
            equipText = smallRoboto.render('Equipped', True, (255, 255, 255))
            draw.rect(screen, (100, 100, 255), equipButton)
            screen.blit(equipText, (530 - (equipText.get_width() // 2), 545))
        # Start Game Button
        startText = midRoboto.render('Start', True, (255, 255, 255))
        if startButton.collidepoint(mx, my):
            draw.rect(screen, (140, 140, 140), startButton)
            if mb[0] and canClick:
                gameState = 'game'
                playTile, drawnmap, minimap = startGame()
        else:
            draw.rect(screen, (100, 100, 100), startButton)
        screen.blit(startText, (630 - (startText.get_width() // 2), 670))


def reloadTime():
    global weaponList
    if player.reloading > 0:
        player.reloading += 1
    if player.reloading == weaponList[currentWeapon].reloadSpeed:
        player.reloading = 0
        player.reserveAmmo[weaponList[currentWeapon].ammoType] += player.mag  # move ammo from mag to reserve
        transferAmmo = min(weaponList[currentWeapon].magSize, player.reserveAmmo[
            weaponList[currentWeapon].ammoType])  # prepare to move one mag worth of ammo back
        player.mag = transferAmmo
        player.reserveAmmo[weaponList[currentWeapon].ammoType] -= transferAmmo


def startGame():  # reset all game related variables
    global spawnX, spawnY, menuAnimation, animationStatus, enemyList, pickupList, regenTimer, bulletList
    playTile = makeTile(fixLevel(makeNewLevel(10)))
    drawnMap = playTile[1]
    minimap = transform.scale(drawnMap, [drawnMap.get_width() // 7, drawnMap.get_height() // 7])
    player.health, player.shield = player.maxHealth, player.maxShield
    player.reserveAmmo = [500, 200, 2500, 60]
    player.X, player.Y = spawnX, spawnY
    enemyList = []
    pickupList = []
    bulletList = []
    regenTimer = 0
    menuAnimation = 0
    player.reloading = 0
    animationStatus = -1
    player.mag = weaponList[currentWeapon].magSize
    drawUpperSprite()
    return playTile, drawnMap, minimap


def mainMenu():
    global mx, my, mb, gameState, running, selectionY, canClick, currentMenuButton, animationStatus, xShift, yShift, currentBackDrop, shiftAmountX, shiftAmountY, startBlitX, startBlitY
    # screen.set_clip((0,0,1280,720))

    if animationStatus % 15 == 0:
        # screen.blit(mainMenuBackDrop,(animationStatus // 4 - 640, animationStatus // 10 - 360))
        screen.blit(mainMenuBackDrops[currentBackDrop], (startBlitX + xShift, startBlitY + yShift))
        # mainMenuBackDrops[currentBackDrop].scroll(shiftAmountX,shiftAmountY)
        xShift += shiftAmountX
        yShift += shiftAmountY
        screen.blit(wfLogo, (180, 10))
        if xShift >= abs(1280 - mainMenuBackDrops[currentBackDrop].get_width()) or yShift >= abs(
                        720 - mainMenuBackDrops[currentBackDrop].get_height()):
            xShift = 0
            yShift = 0
            shiftAmountX *= -1
            shiftAmountY *= -1
            startBlitX = 0
            startBlitY = 0
            currentBackDrop = (currentBackDrop + 1) % 3
        elif xShift <= 1280 - mainMenuBackDrops[currentBackDrop].get_width() or yShift <= 720 - mainMenuBackDrops[
            currentBackDrop].get_height():
            xShift = 0
            yShift = 0
            shiftAmountX *= -1
            shiftAmountY *= -1
            startBlitX = -640
            startBlitY = -360
            currentBackDrop = (currentBackDrop + 1) % 3
    draw.circle(screen, (140, 140, 140), (423, 272), 32)
    draw.circle(screen, (140, 140, 140), (855, 272), 32)
    draw.circle(screen, (140, 140, 140), (423, 608), 32)
    draw.circle(screen, (140, 140, 140), (855, 608), 32)
    draw.rect(screen, (140, 140, 140), (391, 270, 496, 345))
    draw.rect(screen, (100, 100, 100), (416, 240, 446, 400))
    colouredTriangle = selectionTriangle
    flippedColouredTriangle = flippedTriangle
    if my > selectionY:
        selectionY += math.ceil(abs(my - selectionY) / 15)
    elif my < selectionY:
        selectionY -= math.ceil(abs(my - selectionY) / 15)
    darkenedSurf = Surface((426, 250))
    darkenedSurf.set_alpha(140)
    # Controller Stuff
    controllerMenuCoords = [310, 440, 570]
    if controllerMode:
        mx, my = 640, controllerMenuCoords[currentMenuButton]
    # Play Button
    playRect = Rect(426, 250, 426, 120)
    playSurf = Surface((playRect.width, playRect.height))
    playSurf.fill(WHITE)
    if playRect.collidepoint(mx, my):
        if selectionY in range(290, 320):
            colouredTriangle = selectionTriangleB
            flippedColouredTriangle = flippedTriangleB
            selectionY = 310
        if mb[0] and canClick:
            canClick = False
            gameState = 'ship'
        draw.circle(playSurf, (200, 200, 200), (218, 62), 50)
        playSurf.blit(playButton, (163, 10))
    else:
        playSurf.blit(playButtonG, (163, 10))
        playSurf.blit(darkenedSurf, (0, 0))
    screen.blit(playSurf, playRect)
    animationStatus += 1
    # Settings Button
    settingsRect = Rect(426, 380, 426, 120)
    settingsSurf = Surface((settingsRect.width, settingsRect.height))
    settingsSurf.fill(WHITE)
    if settingsRect.collidepoint(mx, my):
        if selectionY in range(430, 450):
            colouredTriangle = selectionTriangleG
            flippedColouredTriangle = flippedTriangleG
            selectionY = 440
        if mb[0] and canClick:
            gameState = 'instructions'
        draw.circle(settingsSurf, (200, 200, 200), (218, 62), 50)
        settingsSurf.blit(settingsGear, (163, 10))
    else:
        settingsSurf.blit(settingsGearG, (163, 10))
        settingsSurf.blit(darkenedSurf, (0, 0))
    screen.blit(settingsSurf, settingsRect)

    # Exit Button
    exitRect = Rect(426, 510, 426, 120)
    exitSurf = Surface((exitRect.width, exitRect.height))
    exitSurf.fill(WHITE)
    if exitRect.collidepoint(mx, my):
        if selectionY in range(560, 590):
            colouredTriangle = selectionTriangleR
            flippedColouredTriangle = flippedTriangleR
            selectionY = 570
        if mb[0] and canClick:
            event.post(event.Event(QUIT))
        draw.circle(exitSurf, (200, 200, 200), (218, 62), 50)
        exitSurf.blit(closeButton, (163, 10))
    else:
        exitSurf.blit(closeButtonG, (163, 10))
        exitSurf.blit(darkenedSurf, (0, 0))
    screen.blit(exitSurf, exitRect)

    # Selection Triangles
    screen.blit(colouredTriangle, (391, min(max(selectionY - (selectionTriangle.get_height() // 2), 250), 510)))
    screen.blit(flippedColouredTriangle, (862, min(max(selectionY - (selectionTriangle.get_height() // 2), 250), 510)))


def instructions():  # draw the instructoins
    global mb, gameState, canClick
    screen.fill(BLACK)
    saveButton = Rect(0,0,300,200)
    loadButton = Rect(310,0,300,200)
    functionLine = 450
    boundKeyLine = functionLine + 120
    boundKeyLine1 = boundKeyLine + 120
    functionRender = Surface((0, 0))
    boundKey = Surface((0, 0))
    boundKey1 = Surface((0, 0))
    startingYOff = 200
    yOff = 0
    for keyFunction, key1, key2 in zip(keyFunctionList, boundKeyList, boundKeyList2):
        functionRender = smallRoboto.render(keyFunction, True, WHITE)
        boundKey = smallRoboto.render(key1, True, WHITE)
        boundKey1 = smallRoboto.render(key2, True, WHITE)
        screen.blit(functionRender, (functionLine, startingYOff + yOff))
        screen.blit(boundKey, (boundKeyLine, startingYOff + yOff))
        screen.blit(boundKey1, (boundKeyLine1, startingYOff + yOff))
        yOff += 20
    functionRender = midRoboto.render('Function', True, WHITE)
    boundKey = midRoboto.render('Key', True, WHITE)
    screen.blit(functionRender, (functionLine, startingYOff - 30))
    screen.blit(boundKey, (boundKeyLine - 7, startingYOff - 30))
    screen.blit(boundKey, (boundKeyLine1 - 7, startingYOff - 30))
    draw.line(screen, WHITE, (boundKeyLine - 5, startingYOff), (boundKeyLine - 5, startingYOff + yOff))
    draw.line(screen, WHITE, (boundKeyLine1 - 5, startingYOff), (boundKeyLine1 - 5, startingYOff + yOff))
    if my > 500:
        if mb[0] == 1:
            canClick = False
            gameState = "menu"
    draw.rect(screen,WHITE,saveButton)
    draw.rect(screen,WHITE,loadButton)
    if mb[0]:
        if saveButton.collidepoint(mx,my):
            saveGame(input('fName'))
        elif loadButton.collidepoint(mx,my):
            loadSave(input('fName'))

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# Main Menu
selectionTriangle = image.load('images/menu/selectionTriangle.png')
flippedTriangle = transform.flip(selectionTriangle, True, False)
selectionTriangleR = image.load('images/menu/selectionTriangleR.png')
flippedTriangleR = transform.flip(selectionTriangleR, True, False)
selectionTriangleG = image.load('images/menu/selectionTriangleG.png')
flippedTriangleG = transform.flip(selectionTriangleG, True, False)
selectionTriangleB = image.load('images/menu/selectionTriangleB.png')
flippedTriangleB = transform.flip(selectionTriangleB, True, False)
wfLogo = image.load('images/menu/wfLogo.png')
settingsGear = image.load('images/menu/gear.png')
settingsGearG = image.load('images/menu/gearG.png')
playButton = image.load('images/menu/playButton.png')
playButtonG = image.load('images/menu/playButtonG.png')
closeButton = image.load('images/menu/closeButton.png')
closeButtonG = image.load('images/menu/closeButtonG.png')
storeBackdrop = image.load('images/menu/storeBackDrop.jpg')
explosiveIcon = image.load('images/menu/explosive.png')
criticalIcon = image.load('images/menu/critical.png')
burstIcon = image.load('images/menu/burst.png')
specialIconList = [explosiveIcon,criticalIcon,burstIcon]
# Adds backdrops to a list for main menu slideshow
mainMenuBackDrops = []
backdropGlob = glob.glob('images/backdrops/backdrop*')
for i in backdropGlob:
    mainMenuBackDrops.append(image.load(i))
random.shuffle(mainMenuBackDrops)
selectionY = 360
# instructions
controls = image.load('images/menu/instructions.png')
controls = transform.scale(controls, (controls.get_width() * 2, controls.get_height() * 2))
keyFunctionList = ['Right', 'Left', 'Jump', 'Shoot', 'Melee', 'Reload']
boundKeyList = ['D', 'A', 'W', 'LMB', 'E', 'R']
boundKeyList2 = ['', '', 'Space', '', '', '']
# Fonts
largeRoboto = font.Font('fonts/Roboto-Light.ttf', 30)
midRoboto = font.Font('fonts/Roboto-Light.ttf', 25)
smallRoboto = font.Font('fonts/Roboto-Light.ttf', 20)
micRoboto = font.Font('fonts/Roboto-Light.ttf', 13)

lisetSprite = image.load('images/levels/liset.png')
lisetSprite = transform.scale(lisetSprite, (int(lisetSprite.get_width() * 1.5), int(lisetSprite.get_height() * 1.5)))
corpDoor1 = image.load('images/levels/corpDoor1.png')
# Sounds
# Music
mixer.music.load('sfx/music/theme.ogg')  # loads music
# Shooting
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
ignisShoot = mixer.Sound('sfx/weapons/grineer/ignisShoot.ogg')
zhugeShoot = mixer.Sound('sfx/weapons/tenno/zhuge.ogg')
supraShoot = mixer.Sound('sfx/weapons/corpus/supraShoot.ogg')
ogrisShoot = mixer.Sound('sfx/weapons/grineer/ogrisShoot.ogg')
somaShoot = mixer.Sound('sfx/weapons/tenno/somaShoot.ogg')
burstonShoot = mixer.Sound('sfx/weapons/tenno/burstonShoot.ogg')
sybarisShoot = mixer.Sound('sfx/weapons/tenno/sybarisShoot.ogg')
detronShoot = mixer.Sound('sfx/weapons/corpus/detronShoot.ogg')
vectisShoot = mixer.Sound('sfx/weapons/tenno/vectisShoot.ogg')
# Reloading
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
ignisReload = mixer.Sound('sfx/weapons/grineer/ignisReload.ogg')
zhugeReload = mixer.Sound('sfx/weapons/tenno/zhugeReload.ogg')
supraReload = mixer.Sound('sfx/weapons/corpus/supraReload.ogg')
ogrisReload = mixer.Sound('sfx/weapons/grineer/ogrisReload.ogg')
somaReload = mixer.Sound('sfx/weapons/tenno/somaReload.ogg')
burstonReload = mixer.Sound('sfx/weapons/tenno/burstonReload.ogg')
sybarisReload = mixer.Sound('sfx/weapons/tenno/sybarisReload.ogg')
detronReload = mixer.Sound('sfx/weapons/corpus/detronReload.ogg')
vectisReload = mixer.Sound('sfx/weapons/tenno/vectisReload.ogg')
# Other
ammoPickup = mixer.Sound('sfx/misc/ammoPickup.ogg')
healthPickup = mixer.Sound('sfx/misc/healthPickup.ogg')
sword1 = mixer.Sound('sfx/weapons/tenno/nikana1.ogg')
sword2 = mixer.Sound('sfx/weapons/tenno/nikana2.ogg')
noSound = mixer.Sound('sfx/misc/none.ogg')
explosionSfx = mixer.Sound('sfx/misc/explosion.ogg')
enemyDeathSounds = [mixer.Sound('sfx/misc/corpusDeath.ogg'), mixer.Sound('sfx/misc/corpusDeath1.ogg')]
# Weapon Info
weaponList = {
    'braton': Weapon(25, 18, 45, 100, bratonShoot, (200, 150, 0), 1, 1, bratonReload, 0, 0, 0, 0, cost=5000, wepType=0),
    'dera': Weapon(15, 13, 30, 80, deraShoot, (50, 170, 255), 1, 1, deraReload, 0, 1, 0, 10, 5, 3, 500, cost=5000,wepType=0),
    'boarP': Weapon(6, 13, 20, 100, boarShoot, (200, 150, 0), 13, 7, boarReload, 1, 0, 0, 0,bulletRange = 300, cost=20000, wepType=1),
    'laser': Weapon(4, 2, 250, 100, laserShoot, (255, 0, 0), 1, 0, laserReload, 2, 0, 0, 0, cost=20000, wepType=3),
    'hek': Weapon(19, 30, 4, 100, hekShoot, (200, 150, 0), 7, 4, hekReload, 1, 0, 0, 0,bulletRange = 500, cost=17500, wepType=1, fireMode = 1),
    'tigris': Weapon(25, 15, 2, 120, tigrisShoot, (200, 150, 0), 5, 6, tigrisReload, 1, 0, 0, 0,bulletRange =400 , cost=17500, wepType=1, fireMode = 1),
    'rubico': Weapon(150, 150, 5, 100, rubicoShoot, WHITE, 1, 0, rubicoReload, 3, 0, 0, 0, cost=20000, wepType=2, fireMode = 1),
    'gorgon': Weapon(20, 10, 90, 180, gorgonShoot, (200, 150, 0), 1, 3, gorgonReload, 0, 0, 0, 0, cost=17500,wepType=3),
    'grakata': Weapon(4, 5, 60, 100, grakataShoot, (200, 150, 0), 1, 8, grakataReload, 0, 0, 0, 0, cost=15000,wepType=0,critChance = 50, critMult = 3),
    'twinviper': Weapon(6, 3, 28, 80, twinviperShoot, WHITE, 1, 7, twinviperReload, 0, 0, 0, 0, cost=5000, wepType=0),
    'vulkar': Weapon(120, 100, 6, 100, vulkarShoot, (200, 150, 0), 1, 0, vulkarReload, 3, 0, 0, 0, cost=15000,wepType=2, fireMode = 1),
    'lanka': Weapon(170, 150, 10, 100, lankaShoot, (0, 255, 0), 1, 1, lankaReload, 3, 1, 0, 15, 10, 4, 700, cost=17500,wepType=2, fireMode = 1),
    'ignis': Weapon(0.7, 3, 150, 100, ignisShoot, (255, 200, 0), 15, 4, ignisReload, 2, 1, 0.1, 7, 5, 5, 80, cost=20000,wepType=3),
    'zhuge': Weapon(60, 23, 20, 100, zhugeShoot, (190, 190, 190), 1, 2, zhugeReload, 0, 1, 0.05, 10, 12, 2, 500,cost=20000, wepType=3),
    'supra': Weapon(11, 5, 180, 180, supraShoot, (0, 255, 0), 1, 2, supraReload, 0, 1, 0, 10, 2, 1, 500, 20000, 3),
    'ogris': Weapon(120, 120, 5, 150, ogrisShoot, (255, 200, 0), 1, 1, ogrisReload, 3, 1, 0, 5, 5, 3, 500, 22500, 3, 1,100, 0, 0 ),
    'soma':Weapon(2.6,5,100,150,somaShoot,WHITE,1,1,somaReload,0,cost = 20000,critChance = 75, critMult = 7),
    'prismagorgon':Weapon(12,8,120,160,gorgonShoot,WHITE,1,3,gorgonReload,0,cost = 21000,wepType = 3,critChance = 35, critMult = 3),
    'burston':Weapon(18,40,45,120,burstonShoot,WHITE,1,1,burstonReload,0,0,cost = 10000,fireMode = 3, burstDelay = 10),
    'sybaris':Weapon(30,30,10,120,sybarisShoot,WHITE,1,1,sybarisReload,0,0,cost = 15000,fireMode = 2,burstDelay = 7,critChance = 25,critMult = 2),
    'detron':Weapon(14.5,18,5,60,detronShoot,WHITE,7,3,detronReload,1,1,0,13,2,1,30,10000,1,fireMode = 1),
    'vectis':Weapon(160,1,1,120,vectisShoot,WHITE,1,0,vectisShoot,3,cost = 20000,wepType = 2,critChance = 25,critMult=2,fireMode = 1),
    'targeter':Weapon(150,100,20,300,vulkarShoot,(50,170,255),1,1,gorgonReload,3,cost = 30000,wepType = 3,fireMode = 1),
    'none': Weapon(0, 0, 0, 10, noSound, BLACK, 0, 0, noSound, 0, 0)}
screen = display.set_mode((1280, 720))
display.set_icon(image.load('images/deco/icon.png'))
idleRight, idleLeft, right, left, jumpRight, jumpLeft = 0, 1, 2, 3, 4, 5
beginShieldRegen = mixer.Sound('sfx/warframes/shield/shieldRegen.ogg')
openMenu = mixer.Sound('sfx/misc/openMenu.ogg')
closeMenu = mixer.Sound('sfx/misc/closeMenu.ogg')
levelAtlas = image.load('images/levels/tileTextures.png')
hudCredit = image.load('images/drops/lifeSupport/hudCredits.png')
# Guns
none = Surface((1, 1), SRCALPHA)
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
ignis = image.load('images/weapons/grineer/ignis.png')
zhuge = image.load('images/weapons/tenno/zhuge.png')
supra = image.load('images/weapons/corpus/supra.png')
ogris = image.load('images/weapons/grineer/ogris.png')
soma = image.load('images/weapons/tenno/soma.png')
prismagorgon = image.load('images/weapons/grineer/gorgonPrisma.png')
burston = image.load('images/weapons/tenno/burston.png')
sybaris = image.load('images/weapons/tenno/sybaris.png')
detron = image.load('images/weapons/corpus/detron.png')
vectis = image.load('images/weapons/tenno/vectis.png')
targeter = image.load('images/weapons/tenno/vectis.png')

frostUpper = image.load('images/warframes/frost/frostUpper.png')
frostArms = image.load('images/warframes/frost/frostArms.png')
frostLower = image.load('images/warframes/frost/frostLower.png')
currentWeapon = 'none'

pic = Surface((20, 30))
pickupSprites = [image.load('images/drops/ammo/rifleAmmo.png'), image.load('images/drops/ammo/shotgunAmmo.png'),
                 image.load('images/drops/ammo/laserAmmo.png'), image.load('images/drops/ammo/sniperAmmo.png'),
                 image.load('images/drops/lifeSupport/health.png'),
                 image.load('images/drops/lifeSupport/credits.png')]  # money is now required to live
pickupList = []
encouragement = ['Go Again', 'Keep Trying', 'Finish the Job', "You're making progress", 'Finish them off',
                 'Finish the job']
encouragementText = ''
# Animations
moaFrames = [[[image.load('images/enemies/moa/Moa001.png')], 1], [
    [image.load('images/enemies/moa/Moa002.png'), image.load('images/enemies/moa/Moa003.png'),
     image.load('images/enemies/moa/Moa004.png'), image.load('images/enemies/moa/Moa005.png'),
     image.load('images/enemies/moa/Moa006.png'), image.load('images/enemies/moa/Moa007.png')], 7],
             [[image.load('images/enemies/moa/Moa008.png'), image.load('images/enemies/moa/Moa009.png')], 7], [
                 [image.load('images/enemies/moa/Moa010.png'), image.load('images/enemies/moa/Moa011.png'),
                  image.load('images/enemies/moa/Moa012.png'), image.load('images/enemies/moa/Moa013.png'),
                  image.load('images/enemies/moa/Moa014.png'), image.load('images/enemies/moa/Moa015.png'),
                  image.load('images/enemies/moa/Moa016.png')], 7]]
crewmanFrames = [[[image.load('images/enemies/crewman/crewman001.png')], 1], [
    [image.load('images/enemies/crewman/crewman002.png'), image.load('images/enemies/crewman/crewman003.png'),
     image.load('images/enemies/crewman/crewman004.png'), image.load('images/enemies/crewman/crewman005.png'),
     image.load('images/enemies/crewman/crewman006.png'), image.load('images/enemies/crewman/crewman007.png'),
     image.load('images/enemies/crewman/crewman008.png'), image.load('images/enemies/crewman/crewman009.png')], 9], [
                     [image.load('images/enemies/crewman/crewman010.png'),
                      image.load('images/enemies/crewman/crewman011.png'),
                      image.load('images/enemies/crewman/crewman012.png'),
                      image.load('images/enemies/crewman/crewman013.png')], 5], [
                     [image.load('images/enemies/crewman/crewman014.png'),
                      image.load('images/enemies/crewman/crewman015.png'),
                      image.load('images/enemies/crewman/crewman016.png'),
                      image.load('images/enemies/crewman/crewman017.png'),
                      image.load('images/enemies/crewman/crewman018.png'),
                      image.load('images/enemies/crewman/crewman019.png'),
                      image.load('images/enemies/crewman/crewman020.png')], 5]]
sCrewmanFrames = [[[image.load('images/enemies/sniperCrewman/sCrewman001.png')], 1], [
    [image.load('images/enemies/sniperCrewman/sCrewman002.png'),
     image.load('images/enemies/sniperCrewman/sCrewman003.png'),
     image.load('images/enemies/sniperCrewman/sCrewman004.png'),
     image.load('images/enemies/sniperCrewman/sCrewman005.png'),
     image.load('images/enemies/sniperCrewman/sCrewman006.png'),
     image.load('images/enemies/sniperCrewman/sCrewman007.png'),
     image.load('images/enemies/sniperCrewman/sCrewman008.png'),
     image.load('images/enemies/sniperCrewman/sCrewman009.png')], 7],
                  [[image.load('images/enemies/sniperCrewman/sCrewman010.png')], 1], [
                      [image.load('images/enemies/sniperCrewman/sCrewman014.png'),
                       image.load('images/enemies/sniperCrewman/sCrewman015.png'),
                       image.load('images/enemies/sniperCrewman/sCrewman016.png'),
                       image.load('images/enemies/sniperCrewman/sCrewman017.png'),
                       image.load('images/enemies/sniperCrewman/sCrewman018.png'),
                       image.load('images/enemies/sniperCrewman/sCrewman019.png'),
                       image.load('images/enemies/sniperCrewman/sCrewman020.png')], 5]]
dCrewmanFrames =[]
playerFrames = [[[image.load("images/warframes/frost/frost001.png")], 1], [
    [image.load("images/warframes/frost/frost003.png"), image.load("images/warframes/frost/frost004.png"),
     image.load("images/warframes/frost/frost005.png"), image.load("images/warframes/frost/frost006.png"),
     image.load("images/warframes/frost/frost007.png"), image.load("images/warframes/frost/frost008.png")], 7], [
                    [image.load("images/warframes/frost/frost015.png"),
                     image.load("images/warframes/frost/frost016.png"),
                     image.load("images/warframes/frost/frost017.png"),
                     image.load("images/warframes/frost/frost018.png"),
                     image.load("images/warframes/frost/frost019.png"),
                     image.load("images/warframes/frost/frost020.png"),
                     image.load("images/warframes/frost/frost021.png")], 5], [
                    [image.load('images/warframes/frost/frostMelee001.png'),
                     image.load('images/warframes/frost/frostMelee002.png'),
                     image.load('images/warframes/frost/frostMelee003.png'),
                     image.load("images/warframes/frost/frostMelee004.png")], 15], [
                    [image.load('images/warframes/frost/frost022.png'),
                     image.load('images/warframes/frost/frost023.png'),
                     image.load('images/warframes/frost/frost024.png'),
                     image.load('images/warframes/frost/frost025.png'),
                     image.load('images/warframes/frost/frost026.png'),
                     image.load('images/warframes/frost/frost027.png')], 7]]
flippedFrame = Surface((0, 0))

# Player frames
playerFrames = completeFrames(playerFrames, [0, 2, 4, 6, 8, 10], [1, 3, 5, 7, 9, 11])
crewmanFrames = completeFrames(crewmanFrames, [0, 2, 4, 6], [1, 3, 5, 7])
moaFrames = flipFrames(completeFrames(moaFrames, [0, 2, 4, 6], [1, 3, 5, 7]))
sCrewmanFrames = completeFrames(sCrewmanFrames, [0, 2, 4, 6], [1, 3, 5, 7])
globalTicks = 0
mobSpawnY = 0
idle = idleRight
jump = jumpRight
additionalOffsets = [[0], [0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                     [-20, -20, 0, 0], [-49, -19, -19, -7], [0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0]]  # used only for melee animations

# Particles
particleList = []

# Physics
friction = 0.2111
airFriction = 0.02111
gravity = 0.25

# Tiles
currentTile = 0
tileSetRects = glob.glob('tileset/plat?.txt')
canClick = True
drawTiles = []
tileRects = []
tileSizes = []
movedTiles = []
tileIO = []
doorList = []
visualOff = 0
movedTileTops = []
# Get information from tileset files
for i in range(len(tileSetRects)):
    tileFile = open(tileSetRects[i]).readlines()  # read tile info
    currentTileSize = [int(i) for i in tileFile[0].split()[0:2]]  # tile size
    tileEntrance = tileFile[0].split()[2]
    tileExit = tileFile[0].split()[3]
    tileIO.append([tileEntrance, tileExit])
    tileSizes.append(currentTileSize)
    tileRects.append([])
    drawTiles.append(Surface(currentTileSize))
    drawTiles[i].fill((255, 255, 255))
    for j in range(1, len(tileFile)):
        platInfo = tileFile[j].split()  # append tile rect, type
        newPlat = [int(platInfo[i]) for i in range(4)]
        draw.rect(drawTiles[i], (0, 0, 0), newPlat)
        tileRects[i].append([Rect(newPlat), int(platInfo[4])])
playTile = ((0, 0), Surface((0, 0)), [[Rect(0, 0, 0, 0)], 0])
minimap = Surface((0, 0))
drawMap = playTile[1]
# Player
player = Mob(400, 300, 33, 36, 0, 0, 4, 0.3, False, 2, health=100, shield=100, money=startingMoney)  # refer to mob
currentFrame = 0

# Store info
weaponNamesList = list(weaponList.keys())
weaponNamesList.sort()
typeSortedWeapons = [[], [], [], []]
for i in range(len(weaponNamesList)):
    weaponName = weaponNamesList[i]
    weaponInfo = weaponList[weaponName]
    if not weaponName == 'none':
        typeSortedWeapons[weaponInfo.wepType].append(weaponName)
purchasedWeapons = [0 for i in range(len(weaponList))]
bulletTrailList = []
counter = 0
shooting = False
paused = False
regenTimer = 0
deathAnimation = 0
canRegenShields = False
selectedWeaponType = 0

# Other
running = True
playerStanding = Surface((player.W, player.H))
playerStanding.fill((255, 0, 0))
gameClock = time.Clock()
controllerMode = False
mx, my = 640, 360
mb = [0, 0, 0]
joyInputX, joyInputY = 0, 0
keysIn = [0 for i in range(323)]
canJump = True
currentMenuButton = 0
canChangeButton = True
currentBackDrop = 0
xShift = 0
yShift = 0
shiftAmountX = 1
shiftAmountY = 1
startBlitX = -640
startBlitY = -360
rotPos = [0, 0, 0, 0]
selectedStoreProduct = 'dera'
typing = False
textOut = []
savedGames = []
findSaves()
print(savedGames)
explosiveList = []
damagePopoff = []
queuedShots = []
targeterList = []

animationStatus = -1  # positive for opening, negative for closing
menuOn = 0
menuAnimation = 0
canUseSword = True
gameState = 'menu'
enemyList = []
bulletList = []
mixer.music.play(-1)  # plays music on repeat
drawUpperSprite()
readyController()
print("Loaded in ", time.get_ticks() - startTime, "ms", sep='')
while running:
    for e in event.get():
        if e.type == QUIT:
            running = False
        if not controllerMode:
            if e.type == KEYDOWN:
                if e.key==K_0:
                    purchasedWeapons = [1 for i in range(len(weaponList))]
                if (e.key == K_w or e.key == K_SPACE) and player.jumps > 0:  # if player can jump
                    player.vY = -7
                    player.jumps -= 1
                if e.key == K_ESCAPE:  # pausing the game
                    if gameState == 'game':
                        animationStatus *= -1
                        if animationStatus > 0:
                            menuAnimation = 0
                            openMenu.play()
                            pauseScreen = screen.copy()
                        elif animationStatus < 0:
                            closeMenu.play()
                            menuAnimation = 20
                if e.key == K_r:  # reload
                    if player.reloading == 0:
                        weaponList[currentWeapon].reloadSound.play()
                        player.reloading += 1
            if e.type == MOUSEBUTTONDOWN:  # shooting
                if e.button == 1:
                    shooting = True
            if e.type == MOUSEBUTTONUP:  # not shooting
                canClick = True
                if e.button == 1:
                    shooting = False
        if controllerMode:
            if e.type == JOYAXISMOTION:
                if e.axis == 0:
                    joyInputX = int(e.value * 10)
                elif e.axis == 1:
                    if gameState != 'menu':
                        joyInputY = int(e.value * 10)
                    elif gameState == 'menu':
                        if e.value > 0.5 and canChangeButton:
                            currentMenuButton = (currentMenuButton + 1) % 3
                            canChangeButton = False
                        elif e.value < -0.5 and canChangeButton:
                            currentMenuButton = (currentMenuButton - 1) % 3
                            canChangeButton = False
                        elif 0.5 > e.value > -0.5:
                            canChangeButton = True
                if abs(math.hypot(joyInputX, joyInputY)) - 1 < 1:
                    joyInputX, joyInputY = 0, 0
                if e.axis == 2:
                    if e.value < -0.3:
                        mb[0] = 1
                        shooting = True
                    elif e.value > -0.3:
                        mb[0] = 0
                        shooting = False
                if e.axis == 4:
                    if abs(e.value) > 0.2:
                        if e.value < 0:
                            keysIn[K_a] = True
                        elif e.value > 0:
                            keysIn[K_d] = True
                    else:
                        keysIn[K_a], keysIn[K_d] = False, False
                if e.axis == 3:
                    if e.value < -0.5 and player.jumps > 0 and canJump:
                        canJump = False
                        keysIn[K_w] = True
                        player.vY = -7
                        player.jumps -= 1
                    elif e.value < -0.5 and player.oW:
                        keysIn[K_w] = True
                    elif 0 > e.value > -0.5:
                        keysIn[K_w] = False
                        canJump = True
            if e.type == JOYBUTTONDOWN:
                if e.button == 0:
                    if gameState != 'game' or menuAnimation > 0:
                        mb[0] = 1
                        shooting = True
                if e.button == 1:
                    if gameState == 'ship':
                        gameState = 'menu'
                if e.button == 2:
                    if player.reloading == 0:
                        weaponList[currentWeapon].reloadSound.play()
                        player.reloading += 1
                if e.button == 4:
                    if gameState == 'ship':
                        selectedWeaponType = (selectedWeaponType - 1) % 4
                if e.button == 5:
                    if gameState == 'game':
                        keysIn[K_e] = True
                    elif gameState == 'ship':
                        selectedWeaponType = (selectedWeaponType + 1) % 4
                if e.button == 6:
                    if gameState == 'game':
                        animationStatus *= -1
                        if animationStatus > 0:
                            menuAnimation = 0
                            openMenu.play()
                            pauseScreen = screen.copy()
                        elif animationStatus < 0:
                            closeMenu.play()
                            menuAnimation = 20
            if e.type == JOYBUTTONUP:
                if e.button == 0:
                    shooting = False
                    mb[0] = 0
                    canClick = True
                if e.button == 5:
                    keysIn[K_e] = False
        if typing:
            if e.type == KEYDOWN:
                if 'a'<=e.unicode<='z' or 'A'<=e.unicode<='Z' or '0'<=e.unicode<='9':
                    textOut.append(e.unicode)
                elif e.key == K_BACKSPACE and len(textOut)>0:
                    del textOut[-1]
    if not controllerMode:
        mb = mouse.get_pressed()
        mx, my = mouse.get_pos()
        keysIn = key.get_pressed()
    elif controllerMode:
        if gameState != 'menu':
            mx = max(min(mx + joyInputX, 1279), 0)
            my = max(min(my + joyInputY, 719), 0)
    playerRect = Rect(player.X, player.Y, player.W, player.H)
    display.set_caption('pyFrame - %d fps' % (int(gameClock.get_fps())))
    if gameState != 'game':
        player.reloading = 0
    if gameState == 'ship':
        shipMenu()
    elif gameState == 'menu':
        mainMenu()
    elif gameState == 'instructions':
        instructions()
    elif gameState == 'game':
        possibleangleIn()
        if menuAnimation <= 0 and player.health > 0:  # go through all game related functions if not in the pause menu and if alive
            spawnEnemies()
            keysDown(keysIn)
            reloadTime()
            player.move()
            player.hitStuff()
            player.applyFriction()
            for i in range(len(queuedShots)-1,-1,-1):
                if queuedShots[i][0] > 0 :
                    queuedShots[i][0] -= 1
                elif queuedShots[i][0] <= 0:
                    fireWeapon(queuedShots[i][1])
                    del queuedShots[i]
            for i in range(len(enemyList)-1,-1,-1):
                enemyList[i].move()
                enemyList[i].enemyLogic()
                enemyList[i].hitStuff()
                enemyList[i].applyFriction()
                if (enemyList[i].health <= 0 and enemyList[i].frame%25 == 0) or enemyList[i].despawn:
                    del enemyList[i]
            for i in range(len(explosiveList) - 1, -1, -1):
                if explosiveList[i].fuse <= 0:
                    explosiveList[i].detonate()
                    del explosiveList[i]
                else:
                    explosiveList[i].fuse -= 1
            for i in range(len(damagePopoff)-1,-1,-1):
                damagePopoff[i].move()
                if damagePopoff[i].life <=0:
                    del damagePopoff[i]
            canRegenShields = player.shield < player.maxShield
            calcBullets()
            # Shield regen and sfx
            if int(player.shield) == 0 and regenTimer == 0:  # play sound only if player has hit 0 health
                beginShieldRegen.play()
            if canRegenShields and regenTimer == 0:
                player.shield += 0.4

            regenTimer = max(0, regenTimer - 1)
            # pickups
            for i in range(len(pickupList) - 1, -1, -1):
                pickupList[i].fallToGround()
                if pickupList[i].checkCollide():
                    del pickupList[i]
            for i in doorList:
                i.moveDoor()
            drawStuff(playTile[1], playTile[0], keysIn)
            if player.shootCooldown > 0:  # fire rate
                player.shootCooldown -= 1
        elif menuAnimation >= 1:  # if paused
            screen.blit(pauseScreen, (0, 0))
            draw.rect(screen, WHITE, (
                670 - min(menuAnimation * 10, 180), 350 - min(menuAnimation * 20, 200),
                2 * min(menuAnimation * 10, 180),
                2 * min(menuAnimation * 10, 110)))
            if menuAnimation >= 20:
                pauseMenu()
        elif player.health <= 0:  # if dead
            if player.health <= 0 and deathAnimation == 0:
                encouragementText = random.choice(encouragement)
            deathAnimation += 1
            if deathAnimation < 350:
                screen.fill((min(200, deathAnimation * 3), 0, 0))
            elif deathAnimation >= 350:
                screen.fill((min(200, max(200 - ((deathAnimation - 350) * 3), 0)), 0, 0))
            if deathAnimation in range(50, 500):
                screen.blit(largeRoboto.render('You Died', True, BLACK), (580, 300))
            if deathAnimation in range(200, 500):
                encouragementRender = largeRoboto.render(encouragementText, True, BLACK)
                screen.blit(encouragementRender, (640 - encouragementRender.get_width() // 2, 350))
            if deathAnimation > 500:
                gameState = 'ship'
                deathAnimation = 0
        if currentWeapon == 'targeter':
            targeterMech()
        menuAnimation += animationStatus
    if not gameState == 'menu':
        drawCursor()
    display.flip()
    gameClock.tick(60)
quit()
print('cya')
