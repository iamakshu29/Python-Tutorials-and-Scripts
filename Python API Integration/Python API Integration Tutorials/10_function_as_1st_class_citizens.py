"""
First-Class Function - They are the Foundation of decorators.
"""
"""
Assigning Functions to variables
"""
def greet(name):
    print(f"Hello {name}")

say_hello = greet
# print(say_hello is greet)
# say_hello("Jack")

# go through args and kwargs once, what they pack and unpack
"""
Passing Functions as Arguments 
"""
def apply_operation(operation, *operands):
    print(f"Applying {operation.__name__} function to {operands}")
    return operation(*operands)

def add(*numbers):
    return sum(numbers)

def mul(*numbers):
    result = 1
    for i in numbers:
        result *= i
    return result

# print(apply_operation(add,2,3))
# print(apply_operation(mul,2,3,4))

"""
Returning Functions from Functions
Used for API clients, loggers ...
"""
def create_api_client(auth_token):
    def api_client(endpoint, method):
        return f"Hitting endpoint {endpoint} with method {method} and aut_token {auth_token}"
    return api_client

alice_api_client = create_api_client("alice-token")
bob_api_client = create_api_client("bob-token")

# print(alice_api_client("/name","GET"))
# print(bob_api_client("/products","POST"))

"""
Storing Function in Data Structures
"""
def task_A():
    print("running task A")
def task_B():
    print("running task B")
def task_C():
    print("running task C")

func_list = [task_A,task_B,task_C]

# print(func_list)
# func_list[0]()
# for i in func_list:
#     i()