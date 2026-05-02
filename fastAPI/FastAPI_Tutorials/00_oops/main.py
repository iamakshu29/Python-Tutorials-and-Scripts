# main.py — Putting OOP Together: Objects, Inheritance & Composition in Action

from Enemy import Zombie, Ogre
from Vehicle import Vehicle, Car, LawnMover
import random
import time


# =============================================
# OBJECT CREATION: Instantiating child classes
# =============================================
# Calling Zombie(200, 40) triggers Zombie.__init__ which calls super().__init__
# behind the scenes — so the Enemy constructor runs with type_of_enemy="Zombie".
# These are objects (instances) of the Zombie and Ogre classes.
Zombie = Zombie(200,40)
Ogre = Ogre(300,30)


# =============================================
# BATTLE FUNCTION: Polymorphism in action
# =============================================
# Both Zombie and Ogre are passed as Enemy objects — each has overridden methods
# (start_message, talk, special_attack) that behave differently per class.
# This is POLYMORPHISM — same method name, different behaviour depending on the object.
def battle(Zombie, Ogre):

    # Calling overridden methods — each enemy has its own version of these
    Zombie.start_message()
    Zombie.talk()
    Zombie.talk()
    Zombie.walk_forward()
    Zombie.cause_damage()

    Ogre.start_message()
    Ogre.talk()
    Ogre.talk()
    Ogre.walk_forward()
    Ogre.cause_damage()

    # =============================================
    # GAME LOOP: Battle runs until one enemy dies
    # =============================================
    while Zombie.health_points > 0 and Ogre.health_points > 0:
        # Randomly pick which enemy attacks this turn
        # random.choice() returns one item from the list — here it picks a METHOD (not a call)
        attack_done = random.choice([Zombie.attack, Ogre.attack])

        if attack_done == Zombie.attack:
            Zombie.attack()
            time.sleep(1)
            Ogre.health_points -= Zombie.attack_damage  # reduce Ogre's HP by Zombie's damage
            if Ogre.health_points < 0:
                Ogre.health_points = 0                  # clamp to 0 — no negative HP
            Ogre.health_remain()
            time.sleep(1)
        else:
            Ogre.attack()
            time.sleep(1)
            Zombie.health_points -= Ogre.attack_damage  # reduce Zombie's HP by Ogre's damage
            if Zombie.health_points < 0:
                Zombie.health_points = 0                # clamp to 0 — no negative HP
            Zombie.health_remain()
            time.sleep(1)

        # Both enemies get a chance to use special attacks each round (if both still alive)
        if Zombie.health_points > 0 and Ogre.health_points > 0:
            Zombie.special_attack()
            Ogre.special_attack()
            time.sleep(1)

    # Return the winner's name using the @property getter (type_of_enemy)
    if Zombie.health_points > 0:
        return Zombie.type_of_enemy
    else:
        return Ogre.type_of_enemy

# winner = battle(Zombie,Ogre)
# print(f"{winner} wins !!!!")


###############################################################

# =============================================
# INHERITANCE IN ACTION: Car IS-A Vehicle
# =============================================
# audi is an instance of Car — which inherits Vehicle's attributes automatically.
# We pass 4 args: Car's own (color, model) + Vehicle's (number_of_wheels, engineType).
audi = Car(4,"V8","Black","Top")
# audi.car_type()


# =============================================
# COMPOSITION IN ACTION: LawnMover HAS-A Vehicle
# =============================================
# First we create a standalone Vehicle object (v) with its own attributes.
# Then we PASS that object into LawnMover's constructor as an argument.
# LawnMover stores it as self.vehicle — this is COMPOSITION.
# LawnMover can now access v's attributes through self.vehicle.engineType, etc.
v = Vehicle(2, "Petrol")                # creating a Vehicle object to be composed
lawnmover = LawnMover("small", v)       # passing the Vehicle object INTO LawnMover
lawnmover.advertise()