# 9_generators.py — Generators and the yield Keyword

# =============================================
# HOW yield WORKS
# =============================================
# yield produces a value and pauses execution — the function's local state is frozen.
# yield does not print anything by itself — it only returns a value to the caller.
# yield from delegates iteration to another iterable/generator.

print("-------------------------------")

# =============================================
# EXAMPLE 1: yield inside a while loop
# =============================================
# Each next() call resumes from right after the last yield.
def count(val):
    i = 0
    while(i <= val):
        print(f"value before {i}")
        i += 1
        yield i
        print(f"value after {i}")

calling_func = count(3)
# for i in calling_func:
#     print(i)

print("-------------------------------")

# =============================================
# EXAMPLE 2: Basic multiple yields
# =============================================
def g():
    yield 1
    yield 2

gen = g()
# for i in gen:
#     print(i)

print("-------------------------------")

# =============================================
# EXAMPLE 3: Execution order with yield
# =============================================
# Code between yields runs only when next() is called — not all at once.
def g():
    print("A")
    yield 1
    print("B")
    yield 2
    print("C")

gen = g()
# for i in g():
#     print(i)

print("-----------")

# =============================================
# KEY POINT: gen vs g() inside next()
# =============================================
# gen = g()       → one generator object, state is preserved between next() calls
# next(g())       → creates a fresh generator every time, execution always restarts from top

# print(next(gen)) → preserves state
# print(next(g())) → always restarts, always yields 1
# they are not equivalent — gen is a single generator object, while g() creates a new one each time it's called.


print("-------------------------------")

gen = g()

# next(gen)
# next(gen)
# next(gen)  # raises StopIteration — for loops handle this automatically

# =============================================
# STEP-BY-STEP: What next(gen) does
# =============================================
# First call:  print("A") → hits yield 1 → returns 1 and pauses
# Second call: resumes → print("B") → hits yield 2 → returns 2 and pauses
# Third call:  resumes → print("C") → function ends → raises StopIteration
# Note: return values 1 and 2 are produced but not printed unless you print(next(gen))


def read_logs():
    lines = ["abc","def","ghi"]
    for l in lines:
        print(f"producing {l}")
        yield l

# for l in read_logs():
#     print(f"consuming {l}")

print("-------------------------------")

# =============================================
# GENERATOR EXHAUSTION — reusing the same object
# =============================================
# A generator can only be iterated once — it does not reset.
# Reusing the same generator object (count_num) means the inner loop
# picks up where the outer loop left off, not from the start.


def count_fun(limit):
    print("Genrators function Started...")
    n = 1
    while(n <= limit):
        print(f"Yielding {n}")
        yield n
        print(f"Resumed after yielding {n}")
        n += 1
    print("Generator function finished")

count_num = count_fun(4)
for n in count_num:
    for m in count_num:
        print(f"- {n}:{m}")

print("***********")

# =============================================
# FRESH GENERATOR PER CALL
# =============================================
# count_fun(4) creates a brand new generator each time it is called.
# So both the outer and inner loops get independent generators that start from 1.
for n in count_fun(4):
    for m in count_fun(4):
        print(f"- {n}:{m}")