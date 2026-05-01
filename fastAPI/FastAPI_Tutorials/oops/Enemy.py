from random import random
import random
class Enemy:
    def __init__(self,type_of_enemy,health_points,attack_damage=3):
        self.__type_of_enemy = type_of_enemy # become private variable using __
        self.health_points = health_points
        self.attack_damage = attack_damage
    
    def start_message(self):
        print("==== Boss Battle Begins ====")
    
    def talk(self):
        print("Enemy Voice")

    def walk_forward(self):
        print(f"{self.__type_of_enemy} moves closer to you")

    def attack(self):
        print(f"ATTACK - {self.__type_of_enemy} attacks for {self.attack_damage} damage")

    def health_remain(self):
        print(f"{self.__type_of_enemy} health is now {self.health_points if self.health_points > 0 else 0}")
        
    def special_attack(self):
        print("Enemy doesnot have an special attack")

# Encapsulating Type of Enemy so that once initiated during object creation, it can't be changed.
    @property
    def type_of_enemy(self):
        return self.__type_of_enemy
    # def set_enemy_type(self, type_of_enemy):
    #     self.__type_of_enemy = type_of_enemy

# give example of type of constructors belo - default/empty, no-arg, params constructor.

# explain the need of encapsulation and their syntax which __
# also tell that they are just for knowing purpose not strict private like in java.

# explain @property decorator, on how the method call act as simply attribute.

# Inheritance
class Zombie(Enemy):
    def __init__(self,health_points,attack_damage):
        super().__init__(type_of_enemy="Zombie",health_points=health_points,attack_damage=attack_damage) # only parent args

# Method Overriding
    def start_message(self):
        print(f"----{self.type_of_enemy} Arriving-------")

    def talk(self):
        print(f"{self.type_of_enemy} *Grumbling...*")

    def cause_damage(self):
        print(f"The {self.type_of_enemy} is trying to spread virus")

    def special_attack(self):
        critical_hit_percentage = random.random() < 0.50
        if critical_hit_percentage:
            self.health_points += 50
            print(f"SPECIAL ATTACK - {self.type_of_enemy} regenerated {self.health_points} HP....HP BOOOST !!!!")
class Ogre(Enemy):
    def __init__(self,health_points,attack_damage):
        super().__init__(type_of_enemy="Ogre",health_points=health_points,attack_damage=attack_damage)

# Method Overriding
    def start_message(self):
        print(f"----{self.type_of_enemy} Arriving-------")

    def enemy_type(self):
        print("Ogre is slamming heads all around")
    
    def talk(self):
        print(f"{self.type_of_enemy} *Roaring...*")
    
    def cause_damage(self):
        print(f"The {self.type_of_enemy} is burning everything")
    
    def special_attack(self):
        critical_hit_percentage = random.random() < 0.20
        if critical_hit_percentage:
            self.attack_damage += 50
            print(f"SPECIAL ATTACK - {self.type_of_enemy} attack has increase by {self.attack_damage} points ..CRITICAL HIT !!!!")
