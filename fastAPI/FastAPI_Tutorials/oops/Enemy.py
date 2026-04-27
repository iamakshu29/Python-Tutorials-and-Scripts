class Enemy:
    def __init__(self,type_of_enemy,health_points,attack_damage=3):
        self.__type_of_enemy = type_of_enemy # become private variable using __
        self.health_points = health_points
        self.attack_damage = attack_damage
    
    def start_message(self):
        print("==== Boss Battle Begins ====")

    def talk(self):
        print(f"I am a {self.__type_of_enemy}")

    def walk_forward(self):
        print(f"{self.__type_of_enemy} moves closer to you")

    def attack(self):
        print(f"{self.__type_of_enemy} attacks for {self.attack_damage} damage")

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
        super().__init__(type_of_enemy="Zombie",health_points=health_points,attack_damage=attack_damage)

# Method Overriding
    def start_message(self):
        print("----Zombies Arriving-------")

    def talk(self):
        print("*Grumbling...*")

    def spread_disease(self):
        print("The Zombie is trying to spread virus")

class Ogre(Enemy):
    def __init__(self,health_points,attack_damage):
        super().__init__(type_of_enemy="Ogre",health_points=health_points,attack_damage=attack_damage)

# Method Overriding
    def start_message(self):
        print("----Ogres Arriving-------")

    def talk(self):
        print("Ogre is slamming heads all around")
