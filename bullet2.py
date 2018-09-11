from pygame import *
import math_tools
import math as pmath
class Bullet2:
    def __init__(self, x, y, angle, damage, faction, range, speed, colour, hitColour, length, gravity, slowdown,
                 thickness, isExplosive=0, explosiveRadius=0, explosiveFalloff=0,
                 fuse=0,isCrit = 0):  # Gravity reduces vY, slowdown decreases vX
        self.x, self.y = x, y
        self.angle = angle
        self.vX, self.vY = speed * math_tools.cosd(angle), speed * math_tools.sind(angle)
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

    def draw(self, surface, player):
        surface.set_at((int(self.x), int(self.y)), self.colour)
        angle = pmath.degrees(pmath.atan2(self.vY, self.vX))
        draw.line(surface, self.colour, (self.x + 640 - player.X, self.y + 360 - player.Y), (
            int((self.length * math_tools.cosd(angle)) + self.x + (640 - player.X)),
            int((self.length * math_tools.sind(angle)) + self.y + (360 - player.Y))), self.thickness)

