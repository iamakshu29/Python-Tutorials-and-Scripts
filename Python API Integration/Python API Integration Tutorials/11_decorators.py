# 11_decorators.py — Decorators: wrapping functions to add behaviour without modifying them

from datetime import datetime, timedelta
import time

# =============================================
# BASIC DECORATOR
# =============================================
# A decorator is a function that takes another function and returns an enhanced version of it.
# *args/**kwargs lets the wrapper forward any arguments to the original function unchanged.
def check_runtime(base_func):
    def enhanced_func(*args, **kwargs):
        start = time.time()
        result = base_func(*args, **kwargs)  # call the original function
        end = time.time()
        print(f"Total Time is {end-start:.5f}")
        return result
    return enhanced_func  # return the wrapper, not the result

# @check_runtime is syntactic sugar for: make_tea = check_runtime(make_tea)
@check_runtime
def make_tea(teaType):
    print(f"Making {teaType}")
    time.sleep(1)
    print(f"{teaType} is ready")    

@check_runtime
def make_matcha():
    print("Making Matcha")
    time.sleep(1)
    print("Matcha is ready")
    return f"Drink Matcha by {datetime.now() + timedelta(minutes=30)}"
    
# Below examples are just result that the above function can be used with/with argument and with/without result
# print("Using pos argument without return")
# make_tea("Green")
# print("--------------")
# print("Using keyword argument without return")
# make_tea(teaType = "Chai")
# print("--------------")
# print("Without using any argument, without return")
# make_matcha()
# print("--------------")
# print("Without using any argument, with return statement")
# output = make_matcha()
# print(output)
# print("----------------------------------------------------------------------")

# =============================================
# DECORATOR WITH ARGUMENTS (3 levels of nesting)
# =============================================
# retry(max_attempts) — outermost: accepts config and returns the actual decorator
# decorator(func)     — middle:    receives the function being decorated
# wrapper(*args)      — innermost: runs on every call, contains the retry logic
import random

def retry(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts+1):
                try:
                    print(f"Attempt {attempt}/{max_attempts}")
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Error: {e}")
                    if attempt == max_attempts:
                        raise  # re-raise after final attempt so the error is not swallowed
        return wrapper
    return decorator

@retry(4)
def sometimes_fails():
    if random.random() < 0.7:
        raise RuntimeError("Flaky Failure")
    return "Success !!"

# print(f"Result: {sometimes_fails()}")

# =============================================
# PRESERVING METADATA WITH @wraps
# =============================================
# Without @wraps, the wrapped function loses its __name__ and __doc__.
# @wraps(func) copies the original function's metadata onto the wrapper.
from functools import wraps

def correct_decorator(func):
	@wraps(func)  # always use this — keeps __name__, __doc__, __module__ intact
	def wrapper(*args, **kwargs):
		return func(*args, **kwargs)
	return wrapper
	
@correct_decorator
def mul(a,b):
	"""Return product of 2 numbers"""
	return a*b

# print("with @wraps")
# print(f" __name__: {mul.__name__}")
# print(f" __doc__: {mul.__doc__}")

# =============================================
# STACKING DECORATORS
# =============================================
# Order matters — decorators are applied bottom-up, but execute top-down.
# @dec_a applied last — outermost wrapper, runs first
# @dec_b applied first — innermost wrapper, runs second
# Execution order: A before → B before → foobar → B after → A after
def dec_a(fun):
	def wrapper(*args, **kwargs):
		print("A before")
		result = fun(*args, **kwargs)
		print("A after")
		return result
	return wrapper
	
def dec_b(fun):
	def wrapper(*args, **kwargs):
		print("B before")
		result = fun(*args, **kwargs)
		print("B after")
		return result
	return wrapper
	
@dec_a
@dec_b
def foobar():
	print("testing stack decorators")

# foobar()


# =============================================
# ROUTE-STYLE DECORATOR — how FastAPI's @app.get("/") works under the hood
# =============================================
# FastAPI's @app.get("/users") is just a decorator with arguments.
# The router object stores a mapping of path → handler function.
# When a request comes in, FastAPI looks up the path and calls the stored function.

class MockApp:
    def __init__(self):
        self.routes = {}  # stores path → function mappings

    def get(self, path):
        # outer function receives the path config
        def decorator(func):
            self.routes[path] = func  # register the function against the path
            return func               # return the original function unchanged
        return decorator

app = MockApp()

@app.get("/")
def home():
    return "Welcome to the home page"

@app.get("/users")
def get_users():
    return "List of users"

# Simulating what FastAPI does when a request hits a path
# print(app.routes["/"]())       # → "Welcome to the home page"
# print(app.routes["/users"]())  # → "List of users"