from Enemy import Zombie, Ogre
from Vehicle import Vehicle, Car, LawnMover
import random
import time

Zombie = Zombie(200,40)
Ogre = Ogre(300,30)

def battle(Zombie, Ogre):
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

    while Zombie.health_points > 0 and Ogre.health_points > 0:
    # Damaging each other  
        attack_done = random.choice([Zombie.attack, Ogre.attack])
        if attack_done == Zombie.attack:
            Zombie.attack()
            time.sleep(1)
            Ogre.health_points -= Zombie.attack_damage
            if Ogre.health_points < 0:
                Ogre.health_points = 0
            Ogre.health_remain()
            time.sleep(1)
        else:
            Ogre.attack()
            time.sleep(1)
            Zombie.health_points -= Ogre.attack_damage
            if Zombie.health_points < 0:
                Zombie.health_points = 0
            Zombie.health_remain()
            time.sleep(1)

        if Zombie.health_points > 0 and Ogre.health_points > 0:
            Zombie.special_attack()
            Ogre.special_attack()
            time.sleep(1)

    if Zombie.health_points > 0:
        return Zombie.type_of_enemy
    else:
        return Ogre.type_of_enemy

# winner = battle(Zombie,Ogre)
# print(f"{winner} wins !!!!")


###############################################################

audi = Car(4,"V8","Black","Top")
# audi.car_type()

v = Vehicle(2, "Petrol")
lawnmover = LawnMover("small",v)
lawnmover.advertise()