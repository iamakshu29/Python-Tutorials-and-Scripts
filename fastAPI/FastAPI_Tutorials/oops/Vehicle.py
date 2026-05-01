class Vehicle:
    def __init__(self,number_of_wheels,engineType):
        self.number_of_wheels = number_of_wheels
        self.engineType = engineType

    def startEngine(self):
        print(f"{self.engineType} Engine is running")

    def stopEngine(self):
        print(f"{self.engineType} Engine is Off")

# Inherticance - "is-a" relationship 
# car is-a vehicle
class Car(Vehicle):
    def __init__(self,number_of_wheels,engineType,color,model):
        super().__init__(number_of_wheels,engineType)
        self.color = color
        self.model = model
    
    def car_type(self):
        print(f"Car is of {self.model} Model, has {self.number_of_wheels} wheels, {self.color} in color and has {self.engineType} engine")


# Compostion - "has-a" relationship
# LawnMover has-a engine and wheels but LawnMover is not a vehicle
class LawnMover:
    def __init__(self,size,vehicle):
        self.size = size
        self.vehicle = vehicle
    
    def advertise(self):
        print(f"Buy this LawnMover, which has {self.vehicle.engineType} engine, {self.size} in size and has {self.vehicle.number_of_wheels} wheels")

# Composition = passing an object (instance) as a paramter in class Method and storing it
# Inheritance = class A(B)