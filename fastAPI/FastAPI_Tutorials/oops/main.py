from Enemy import Enemy, Zombie, Ogre

# tell what we are doing here
ogre = Enemy("ogre",500,2)
print(f"{ogre.type_of_enemy} has total of {ogre.health_points} health points and can do an attack damage of {ogre.attack_damage} points")

# Abstraction
# explain a bit
zombie = Enemy("Zombie",1000,20)
zombie.start_message()
zombie.talk()
zombie.walk_forward()
zombie.attack()

# Inheritance
megaZombie = Zombie(200,20)
megaZombie.start_message()
megaZombie.talk()
megaZombie.spread_disease()

redOgre = Ogre(300,30)
redOgre.start_message()
redOgre.talk()