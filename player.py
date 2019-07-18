import mob
class Player(mob.Mob):

    def __init__(self, x, y, w, h, vX, vY, vM, vAx, fA, jumps, health=100, shield=100, enemyType=0, animation=0,
                 weapon='braton', avoidance=50, shootRange=200, money=5000):
        super().__init__(x, y, w, h, vX, vY, vM, vAx, fA, jumps, health, shield, enemyType, animation, weapon,
                         avoidance, shootRange, money)

        self.reserveAmmo = [500, 200, 60, 2500]
        self.reloading = 0  # Reload timer