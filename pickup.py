from pygame import *
import random
class Pickup:  # Class for ammo, health, and credit drops
    def __init__(self, x, y, dropType, amount):
        self.X = x
        self.Y = y
        self.vY = 0
        self.dropType = dropType  # an int that describes what kind of ammo the drop is
        self.amount = amount  # int for ammo amount, string if credits or health

    def fallToGround(self, pickupSprites, playTile):
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

    def checkCollide(self, player, ammoPickup, healthPickup):  # Checks if player is colliding with the pickup
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