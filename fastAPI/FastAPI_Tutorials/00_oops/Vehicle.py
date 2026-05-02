# Vehicle.py — OOP Concepts: Classes, Inheritance & Composition

# =============================================
# BASE CLASS: Vehicle
# =============================================
# A base class (also called parent class) defines shared attributes
# and behaviours that child classes can inherit.
# __init__ is the constructor — it runs automatically when an object is created.
class Vehicle:
    def __init__(self,number_of_wheels,engineType):
        self.number_of_wheels = number_of_wheels  # instance attribute — unique to each object
        self.engineType = engineType               # instance attribute — unique to each object

    def startEngine(self):
        print(f"{self.engineType} Engine is running")

    def stopEngine(self):
        print(f"{self.engineType} Engine is Off")


# =============================================
# INHERITANCE: "is-a" Relationship
# =============================================
# Syntax: class Child(Parent)
# Car IS-A Vehicle — so Car inherits Vehicle's attributes and methods.
# Use super().__init__() to call the parent constructor and pass shared args up.
# Car adds its own extra attributes (color, model) on top of what Vehicle already has.
class Car(Vehicle):
    def __init__(self,number_of_wheels,engineType,color,model):
        super().__init__(number_of_wheels,engineType)  # passes number_of_wheels & engineType to Vehicle.__init__
        self.color = color
        self.model = model
    
    def car_type(self):
        print(f"Car is of {self.model} Model, has {self.number_of_wheels} wheels, {self.color} in color and has {self.engineType} engine")


# =============================================
# COMPOSITION: "has-a" Relationship
# =============================================
# LawnMover HAS-A engine and HAS-A set of wheels — but it is NOT a Vehicle.
# Instead of inheriting Vehicle, we pass a Vehicle object INTO LawnMover.
# This is Composition: one object contains another object as an attribute.
# When to use Composition over Inheritance:
#   - Use Inheritance when the child truly IS a specialised version of the parent.
#   - Use Composition when an object simply USES or CONTAINS another object.
class LawnMover:
    def __init__(self,size,vehicle):
        self.size = size
        self.vehicle = vehicle  # storing the Vehicle object — this IS composition
    
    def advertise(self):
        # Accessing the composed Vehicle object's attributes via self.vehicle
        print(f"Buy this LawnMover, which has {self.vehicle.engineType} engine, {self.size} in size and has {self.vehicle.number_of_wheels} wheels")


# =============================================
# QUICK RECAP
# =============================================
# Composition  = passing an object (instance) as a parameter and storing it as an attribute
# Inheritance  = class Child(Parent) — child directly extends the parent class