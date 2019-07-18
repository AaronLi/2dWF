import json
from pygame import image, Color, mixer
from bullet2 import Bullet2

class Weapon:

    class WEAPON_TYPE:
        RIFLE = 0
        SHOTGUN = 1
        SNIPER_RIFLE = 2
        SPECIAL = 3


        @staticmethod
        def string_to_weapon_type(stringIn):
            lowerString = stringIn.lower()
            if lowerString == 'rifle':
                return Weapon.WEAPON_TYPE.RIFLE
            elif lowerString == 'shotgun':
                return Weapon.WEAPON_TYPE.SHOTGUN
            elif lowerString == 'sniper_rifle':
                return Weapon.WEAPON_TYPE.SNIPER_RIFLE
            elif lowerString == 'special':
                return Weapon.WEAPON_TYPE.SPECIAL

    class FIRE_MODE:
        FULL_AUTO = 0
        SEMI_AUTO = 1



    def __init__(self, damage=0, firerate=0, magSize=0, reloadSpeed=0, fireSound=None, bulletColour=(0,0,0), bulletsPerShot=1, inaccuracy=0,
                 reloadSound=None, ammoType=0, bulletType=0, bulletGravity=0, bulletSpeed=0, bulletLength=0, bulletThickness=0,
                 bulletRange=900, cost=0, wepType=0, isExplosive=0, explosiveRadius=0, explosiveFalloff=0, fuse=0,critChance = 5,critMult = 1.5, fireMode = 0, burstDelay = 1):
        self.name=""
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
        self.sprite = None

    def get_stats(self):
        stats_out = {"damage":self.damage,
                     "firerate":self.firerate,
                     "magSize":self.magSize,
                     "reloadSpeed":self.reloadSpeed,
                     "inaccuracy":self.inaccuracy,
                     "bulletsPerShot":self.bulletsPerShot}
        return stats_out

class WeaponFactory:
    def __init__(self):
        pass

    def load_from_file(self, file_path):
        out = Weapon()
        with open(file_path) as f:
            data = json.load(f)
            for label in data:
                dat = data[label]
                if label == "name":
                    out.name = dat
                elif label == "weapon_type":
                    out.wepType = Weapon.WEAPON_TYPE.string_to_weapon_type(dat)

                elif label == "damage":
                    out.damage = dat
                elif label == 'fire_rate':
                    out.firerate = dat
                elif label == 'sprite':
                    out.sprite = image.load(dat).convert_alpha()
                elif label == 'cost':
                    out.cost = dat
                elif label == 'magazine_size':
                    out.magSize = dat
                elif label == 'reload_speed':
                    out.reloadSpeed = dat
                elif label == 'bullet_colour':
                    out.bulletColour = Color(dat)
                elif label == 'bullets_per_shot':
                    out.bulletsPerShot = dat
                elif label == 'inaccuracy':
                    out.inaccuracy = dat
                elif label == 'sounds':
                    for soundtype in dat:
                        soundPath = dat[soundtype]

                        if soundtype == 'reloading':
                            out.reloadSound = mixer.Sound(soundPath)
                        elif soundtype == 'firing':
                            out.fireSound = mixer.Sound(soundPath)
                elif label == 'ammo_type':
                    out.ammoType = Weapon.WEAPON_TYPE.string_to_weapon_type(dat)

                elif label == 'bullet_type':
                    if dat == 'hitscan':
                        out.bulletType = Bullet2.BulletType.HITSCAN
                    elif dat == 'projectile':
                        out.bulletType = Bullet2.BulletType.PROJECTILE
                elif label == 'bullet_speed':
                    out.bulletSpeed = dat
                elif label == 'bullet_length':
                    out.bulletLength = dat
                elif label == "is_explosive":
                    out.isExplosive = dat.lower() == 'true'
                elif label == 'explosive_radius':
                    out.explosiveRadius = dat
                elif label == 'explosive_falloff':
                    out.explosiveFalloff = dat
                elif label == 'fuse':
                    out.fuse = dat
                elif label == 'burst_delay':
                    out.burstDelay = dat
                elif label == 'bullet_gravity':
                    out.bulletGravity = dat
                elif label == 'bullet_thickness':
                    out.bulletThickness = dat
                elif label == 'bullet_range':
                    out.bulletRange = dat
                elif label == 'critical_chance':
                    out.critChance = dat
                elif label == 'critical_multiplier':
                    out.critMult = dat
                elif label == 'fire_mode':
                    if dat == 'auto':
                        out.fireMode = Weapon.FIRE_MODE.FULL_AUTO
                    elif dat == 'semi':
                        out.fireMode = Weapon.FIRE_MODE.SEMI_AUTO
                    else: # numbers larger than one are multi shot bursts
                        out.fireMode = int(dat)
                else:
                    print("Unhandled descriptor: %s"%label)
        return out

    def make_weapon_template(self, filename):
        template= \
            {
            "name":"",
            "weapon_type":"",
            "fire_rate":0,
            "damage":0,
            "sprite":"images/weapons",
            "cost":0,
            "magazine_size":0,
            "reload_speed":0,
            "bullet_colour":"#ffffff",
            "bullets_per_shot":0,
            "inaccuracy":0,
            "sounds":{
                "firing":"sfx/weapons/",
                "reloading":"sfx/weapons/"
            },
            "ammo_type":"",
            "bullet_type":"",
            "bullet_gravity":0,
            "bullet_speed":0,
            "bullet_length":0,
            "bullet_thickness":0,
            "bullet_range":0,
            "is_explosive":"false",
            "explosive_radius":0,
            "explosive_falloff":0,
            "fuse":0,
            "critical_chance":0,
            "critical_multiplier":0.0,
            "fire_mode":"",
            "burst_delay":0
        }
        with open(filename, 'w') as f:
            json.dump(template, f, indent=True)

        print("Saved template to",filename)

if __name__ == "__main__":
    factory = WeaponFactory()
    weapon_name = input("weapon name?\n>>> ")
    factory.make_weapon_template("dat/weapons/%s.json"%weapon_name)