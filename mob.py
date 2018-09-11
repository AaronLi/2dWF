import random, pickup, bullet2
from pygame import *

import damage_text
from math_tools import *

dead_body_decay_time = 240 # number of frames before a dead body decays

class Mob:  # Class used for the player and enemies
    def __init__(self, x, y, w, h, vX, vY, vM, vAx, fA, jumps, health=100, shield=100, enemyType=0, animation=0,
                 weapon='braton', avoidance=50, shootRange=200, money=5000):
        self.X, self.Y = x, y
        self.width, self.H = w, h
        self.vX, self.vY = vX, vY
        self.vM, self.vAx = vM, vAx  # max velocity for mob to travel at, acceleration rate to the max
        self.oG, self.oW = False, False  # whether the mob is on the ground/floor, whether the mob is on a wall
        self.facing_left = fA  # (player.fAcing) True for left, False for right
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
        self.decay = 0
        # Companion Related Things
        self.target = -1

    def move(self):
        self.X += int(self.vX)
        self.Y += int(self.vY)

    def enemyLogic(self, player, pickupList, enemyDeathSounds, pickupSprites, playTile, doorList, bulletList, weaponList, playerRect):
        # Logic
        distX = abs(self.X - player.X)  # distance from player
        distY = abs(self.Y - player.Y)
        enemyRect = Rect(self.X, self.Y, self.width, self.H)  # enemy hitbox
        losX = self.X  # line of sight x for checking whether you can shoot or not
        checkLos = True
        # Checking health
        if self.health <= 0:  # start dying if not enough health
            if self.dying == 0:
                if self.facing_left:
                    self.animation = 6
                else:
                    self.animation = 7

            self.dying += 1
            if self.dying == 1:
                self.frame = 1
                if self.enemyType !=1:
                    random.choice(enemyDeathSounds).play()  # find a lovely death sound
            if self.frame % 25 == 0 and self.decay == 0:  # wait until enemy death animation is done
                if random.randint(0, 2) == 0:  # spawn a drop
                    dropType = random.randint(0, len(pickupSprites) - 1)
                    dropAmounts = [20, 10, 50, 10, 'health', 'credits']  # Rifle, shotgun, laser, health, sniper
                    pickupList.append(pickup.Pickup(self.X + self.width // 2,
                                                    self.Y + self.H - pickupSprites[dropType].get_height(),
                                                    dropType,
                                                    dropAmounts[dropType]))
                if self.facing_left:
                    self.animation = 8
                else:
                    self.animation = 9
                self.decay+=1
            elif self.decay > 0:
                self.despawn = self.decay > dead_body_decay_time
                self.decay+=1
        elif distY > 1000 or distX > 1200:  # if enemy is too far away then despawn it
            self.despawn = True
        else:
            # Jumping over obstacles
            if self.oW and self.oG:  # if there's a wall and the enemy is on the ground
                self.jumps -= 1
                self.vY -= 7

            # Jumping across gaps
            if self.facing_left:
                if (not enemyRect.move(int(self.vM), 1).colliderect(
                        self.hP[
                            0])) and self.oG:  # if the moved enemy won't be still on the platform (hP)
                    self.vY -= 7  # jump
            elif not self.facing_left:
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
                            if self.facing_left:  # shooting animation
                                self.animation = 4
                            else:
                                self.animation = 5
                            if self.shootCounter % weaponList[self.weapon].firerate == 0:
                                # different bullet based on different enemy type
                                if self.enemyType == 0:
                                    if self.facing_left:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X, self.Y + 25+random.randint(-1,1), 0,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                    weaponList[self.weapon].bulletColour,
                                                    (255, 0, 0), 7, 0, 0, 2))
                                    else:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X + self.width, self.Y + 25 + random.randint(-1, 1), 180,
                                                            weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                            weaponList[self.weapon].bulletColour, (255, 0, 0), 7,
                                                            0, 0, 2))
                                elif self.enemyType == 1:
                                    if self.facing_left:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X + self.width // 2, self.Y + random.randint(-1, 1), 0,
                                                            weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                            weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                            0, 0, 4))
                                    else:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X + self.width // 2, self.Y, 180,
                                                            weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                            weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                            0, 0, 4))
                                elif self.enemyType == 2:
                                    if self.facing_left:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X + self.width // 2, self.Y + 25 + random.randint(-1, 1), 0,
                                                            weaponList[self.weapon].damage // 2, 0, 400, 7,
                                                            weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                            0, 0, 4))
                                    else:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X + self.width // 2, self.Y + 25 + random.randint(-1, 1), 180,
                                                            weaponList[self.weapon].damage // 2, 0, 400, 7,
                                                            weaponList[self.weapon].bulletColour, (255, 0, 0), 5,
                                                            0, 0, 4))
                                elif self.enemyType == 3:
                                    if self.facing_left:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X, self.Y + 22+random.randint(-1,1), 0,
                                                    weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                    weaponList[self.weapon].bulletColour,
                                                    (255, 0, 0), 7, 0, 0, 2))
                                    else:
                                        bulletList.append(
                                            bullet2.Bullet2(self.X + self.width, self.Y + 22 + random.randint(-1, 1), 180,
                                                            weaponList[self.weapon].damage // 2, 0, 400, 3,
                                                            weaponList[self.weapon].bulletColour, (255, 0, 0), 7,
                                                            0, 0, 2))
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
                    self.facing_left = True
                    if not self.attacking:  # use standing animation if not attacking
                        self.shootCounter = 0
                        self.animation = idleRight
                elif player.X < self.X:  # Face left is player is on left
                    self.facing_left = False
                    if not self.attacking:
                        self.shootCounter = 0
                        self.animation = idleLeft

                if abs(
                                player.X - self.X) > self.shootRange or not self.oG:  # Move towards player if not on ground or if outside of shooting range
                    if player.X > self.X:  # begin walking to the right
                        self.facing_left = True
                        self.vX += self.vAx
                        self.animation = right
                    elif player.X < self.X:  # begin walking to the left
                        self.facing_left = False
                        self.vX -= self.vAx
                        self.animation = left
                    self.shootCounter = 0
                elif abs(
                                player.X - self.X) < self.avoidance or not self.oG:  # Move away from player if not on ground or inside avoidance area
                    if player.X > self.X:  # Move left
                        self.facing_left = False
                        self.vX -= self.vAx
                        self.animation = left
                    elif player.X < self.X:  # Move right
                        self.facing_left = True
                        self.vX += self.vAx
                        self.animation = right
                    self.shootCounter = 0

    def kubrowLogic(self, player, mobList, damagePopoff):
        # Logic
        distX = abs(self.X - player.X)  # distance from player
        distY = abs(self.Y - player.Y)
        kubrowRect = Rect(self.X, self.Y, self.width, self.H)  # enemy hitbox
        if self.target == -1:
            if random.randint(0, 120) == 0:
                enemyDistances = []
                for i in mobList:
                    if i.health > 0:
                        enemyDistances.append(abs(i.X - self.X))
                if len(enemyDistances)>0:
                    self.target = enemyDistances.index(min(enemyDistances))
                else:
                    self.target = -1
        if distY > 1000 or distX > 1200:  # if enemy is too far away then despawn it
            self.X, self.Y = player.X, player.Y
            self.target = -1
        else:
            # Jumping over obstacles
            if self.oW and self.oG:  # if there's a wall and the enemy is on the ground
                self.jumps -= 1
                self.vY -= 7

            # Jumping across gaps
            if self.facing_left:
                if (not kubrowRect.move(int(self.vM), 1).colliderect(
                        self.hP[
                            0])) and self.oG:  # if the moved enemy won't be still on the platform (hP)
                    self.vY -= 7  # jump
            elif not self.facing_left:
                if (not kubrowRect.move(-int(self.vM), 1).colliderect(self.hP[0])) and self.oG:
                    self.vY -= 7
            if self.target != -1:
                # Shooting

                try:
                    if abs(self.X - mobList[self.target].X) in range(0,
                                                                     10):  # if player distance is in between the enemy avoidance and the sooting range
                        if abs(self.Y - mobList[self.target].Y) < 30 and int(
                                self.vX) == 0:  # if player and enemy are both on the same level
                            self.attacking = True
                            mobList[self.target].damage(25, damagePopoff)
                            self.target = -1
                    else:
                        self.attacking = False
                except IndexError:
                    self.target = -1
        # Moving left and right
        if self.target == -1:
            self.attacking = False
            if self.animation != 6:  # Won't work if mob is currently dying
                if player.X > self.X:  # face right if player is on right
                    self.facing_left = True
                    if not self.attacking:  # use standing animation if not attacking
                        self.animation = idleRight
                elif player.X < self.X:  # Face left is player is on left
                    self.facing_left = False
                    if not self.attacking:
                        self.animation = idleLeft

                if abs(
                                player.X - self.X) > 20 or not self.oG:  # Move towards player if not on ground or if outside of shooting range
                    if player.X > self.X:  # begin walking to the right
                        self.facing_left = True
                        self.vX += self.vAx
                        self.animation = right
                    elif player.X < self.X:  # begin walking to the left
                        self.facing_left = False
                        self.vX -= self.vAx
                        self.animation = left
                elif abs(
                                player.X - self.X) < 1 or not self.oG:  # Move away from player if not on ground or inside avoidance area
                    if player.X > self.X:  # Move left
                        self.facing_left = False
                        self.vX -= self.vAx
                        self.animation = left
                    elif player.X < self.X:  # Move right
                        self.facing_left = True
                        self.vX += self.vAx
                        self.animation = right
        else:
            if abs(
                            mobList[
                                self.target].X - self.X) > 10 or not self.oG:  # Move towards mobList[self.target] if not on ground or if outside of shooting range
                if mobList[self.target].X > self.X:  # begin walking to the right
                    self.facing_left = True
                    self.vX += self.vAx
                    self.animation = right
                elif mobList[self.target].X < self.X:  # begin walking to the left
                    self.facing_left = False
                    self.vX -= self.vAx
                    self.animation = left
            elif abs(
                            mobList[
                                self.target].X - self.X) < 1 or not self.oG:  # Move away from mobList[self.target] if not on ground or inside avoidance area
                if mobList[self.target].X > self.X:  # Move left
                    self.facing_left = False
                    self.vX -= self.vAx
                    self.animation = left
                elif mobList[self.target].X < self.X:  # Move right
                    self.facing_left = True
                    self.vX += self.vAx
                    self.animation = right

    def damage(self, amount, damagePopoff, dtype=0):
        self.health -= amount
        damagePopoff.append(
            damage_text.DamageText(self.X + (self.width // 2) + random.randint(-30, 30), self.Y + random.randint(-10, 0), amount,
                                   dtype))

    def applyFriction(self, friction, airFriction):
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

    def hitStuff(self, playTile, gravity):
        mobRect = Rect(self.X, self.Y, self.width, self.H)
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
                    self.X = platTile[0].left - self.width - 1  # move to right
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
