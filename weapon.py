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
