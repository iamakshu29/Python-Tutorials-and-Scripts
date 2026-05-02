# Enemy.py — OOP Concepts: Encapsulation, Constructors, @property, Inheritance & Method Overriding

from random import random
import random


# =============================================
# BASE CLASS: Enemy
# =============================================
# Enemy is the parent class — defines the template for all enemy types.
#
# TYPES OF CONSTRUCTORS (for reference):
#   1. Default / Empty constructor  — __init__(self)  — no params, Python provides one if missing
#   2. No-arg constructor           — __init__(self)  — explicitly defined but takes no extra args
#   3. Parameterised constructor    — __init__(self, x, y) — takes arguments to set attributes
#
# Here we use a PARAMETERISED constructor — attack_damage=3 is a DEFAULT argument,
# meaning if the caller doesn't pass it, it automatically gets 3.
class Enemy:
    def __init__(self,type_of_enemy,health_points,attack_damage=3):
        self.__type_of_enemy = type_of_enemy  # ENCAPSULATED — private variable using __ (name mangling)
        self.health_points = health_points
        self.attack_damage = attack_damage    # default value = 3 if not provided by caller
    
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


    # =============================================
    # ENCAPSULATION: Private variable with __
    # =============================================
    # self.__type_of_enemy uses name mangling — Python renames it to _Enemy__type_of_enemy internally.
    # This means it CANNOT be accessed directly as obj.__type_of_enemy from outside the class.
    # NOTE: Unlike Java, this is NOT strictly private — it's a convention to signal "don't touch this".
    # You CAN still access it as obj._Enemy__type_of_enemy, but you shouldn't.
    # Goal: prevent type_of_enemy from being changed after the object is created.

    # =============================================
    # @property DECORATOR: Read-only access
    # =============================================
    # @property turns a method into a read-only attribute.
    # After this, you call enemy.type_of_enemy (no parentheses) — it looks like an attribute,
    # but behind the scenes it runs this getter method.
    # This gives controlled READ access to the private __type_of_enemy without allowing writes.
    # The commented-out setter below shows how you WOULD allow writes — left out intentionally
    # to keep type_of_enemy read-only (encapsulation goal).
    @property
    def type_of_enemy(self):
        return self.__type_of_enemy
    # def set_enemy_type(self, type_of_enemy):   # <-- setter — would allow changing the value
    #     self.__type_of_enemy = type_of_enemy   # <-- commented out to enforce read-only


# =============================================
# INHERITANCE: Zombie IS-A Enemy
# =============================================
# Zombie extends Enemy — it inherits all of Enemy's methods and attributes.
# super().__init__() calls Enemy's constructor with the required args.
# type_of_enemy is hardcoded to "Zombie" here — the caller only passes health & damage.
class Zombie(Enemy):
    def __init__(self,health_points,attack_damage):
        super().__init__(type_of_enemy="Zombie",health_points=health_points,attack_damage=attack_damage)


    # =============================================
    # METHOD OVERRIDING: Zombie's custom behaviour
    # =============================================
    # When a child class defines a method with the SAME name as the parent,
    # it OVERRIDES the parent's version — Python calls the child's version instead.
    # This allows each enemy type to have its own unique behaviour.
    def start_message(self):
        print(f"----{self.type_of_enemy} Arriving-------")

    def talk(self):
        print(f"{self.type_of_enemy} *Grumbling...*")

    def cause_damage(self):
        print(f"The {self.type_of_enemy} is trying to spread virus")

    # random.random() returns a float between 0.0 and 1.0
    # < 0.50 means there's a 50% chance the special attack triggers
    def special_attack(self):
        critical_hit_percentage = random.random() < 0.50
        if critical_hit_percentage:
            self.health_points += 50
            print(f"SPECIAL ATTACK - {self.type_of_enemy} regenerated {self.health_points} HP....HP BOOOST !!!!")


class Ogre(Enemy):
    def __init__(self,health_points,attack_damage):
        super().__init__(type_of_enemy="Ogre",health_points=health_points,attack_damage=attack_damage)

    def start_message(self):
        print(f"----{self.type_of_enemy} Arriving-------")

    def enemy_type(self):
        print("Ogre is slamming heads all around")
    
    def talk(self):
        print(f"{self.type_of_enemy} *Roaring...*")
    
    def cause_damage(self):
        print(f"The {self.type_of_enemy} is burning everything")
    
    # Only 20% chance — Ogre's special attack is rarer but boosts attack damage (not HP)
    def special_attack(self):
        critical_hit_percentage = random.random() < 0.20
        if critical_hit_percentage:
            self.attack_damage += 50
            print(f"SPECIAL ATTACK - {self.type_of_enemy} attack has increase by {self.attack_damage} points ..CRITICAL HIT !!!!")
