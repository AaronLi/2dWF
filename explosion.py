import particle, math_tools, random
from pygame import *
init()
explosionSfx = mixer.Sound('sfx/misc/explosion.ogg')
class Explosion:
    def __init__(self, x, y, damage, falloff, radius, colour, smokeColour, fuse):
        self.x, self.y = x, y
        self.damage = damage
        self.falloff = falloff
        self.radius = radius
        self.colour = colour
        self.smokeColour = smokeColour
        self.fuse = fuse

    def detonate(self, playTile, doorList, screen, mobList, particleList, damagePopoff):
        hitByExplosive = [False for i in range(len(mobList))]
        for i in range(0, 360, 15):
            hitEnvironment  = False
            particleList.append(particle.Particle(screen, self.x, self.y, i, self.radius // 5, (255, random.randint(0, 255), 0),random.randint(2,3), 0, 0, 0, 2, 20, 2))
            particleList.append(particle.Particle(screen, self.x, self.y, i, self.radius // 5, self.smokeColour, random.randint(2,3), 0, 0, 0, 2,20, 2))
            for j in range(0, self.radius, 7):
                checkPoint = (int(self.x + (j * math_tools.cosd(i))), int(self.y + (j * math_tools.sind(i))))
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
                    for l, m in zip(mobList, range(len(mobList))):
                        enemyRect = Rect(l.X, l.Y, l.W, l.H)
                        if enemyRect.collidepoint(checkPoint) and not hitByExplosive[m]:
                            l.damage(max(self.damage - (7 * (j * self.falloff)), 0), damagePopoff)
                            if l.X+(l.W//2) > self.x:
                                l.vX = max(self.radius-abs(self.x-(l.X+(l.W//2))), 0)
                            elif l.X+(l.W//2) > self.x:
                                l.vX = min(-(self.radius-abs(self.x-(l.X+(l.W//2)))), 0)
                            l.vY = -3
                            hitByExplosive[m] = True
                elif hitEnvironment:
                    break
        explosionSfx.play()