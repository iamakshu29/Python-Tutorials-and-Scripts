# 00_pre_req.py — Prerequisites: Queue, Lock, and Random Utility

# =============================================
# QUEUE — Sync Queue Concepts
# =============================================
# A Queue is a FIFO data structure — first item in is the first item out.
# Python's queue.Queue is thread-safe internally (uses locks), unlike a plain list.
# Why not use a list? Lists are not thread-safe — concurrent access causes race conditions.

# Methods:
# 1. q.put()    → Adds an item to the back of the queue
# 2. q.get()    → Removes and returns the first item (FIFO)
# 3. q.qsize()  → Returns the current number of items
# 4. q.empty()  → Returns True if the queue has no items
# 5. q.full()   → Returns True if the queue has reached maxsize

# q = Queue(maxsize=5)  → Optional cap; q.put() blocks when full

# Type of Queue:
# Queue        → Standard FIFO
# LifoQueue    → Last in, first out (stack behavior)
# PriorityQueue → Items with lowest priority number come out first
from queue import Queue, LifoQueue, PriorityQueue


# Below are some implementation
q = Queue()

print(q.full())  # False

q.put("task1")
q.put("task2")

print(q.get())  # task1
print(q.empty())  # False
print(q.get())  # task2
print(q.qsize())  # 0

# Why not use a list ?? -> list is not thread-safe:
# If multiple threads access it simultaneously, race conditions can occur.
# Queue internally uses locks to make operations safe.


q = PriorityQueue()

q.put((2, "Low"))
q.put((1, "High"))

print(q.get())  # (1, "High") Lower priority number comes out first.


# # Some other methods
# q.task_done() → “the claimed work finished”. i.e. q.get() is done
# q.join() → “wait until all claimed work has finished”.


# =============================================
# LOCK — Mutual Exclusion (Mutex)
# =============================================
# A Lock enforces mutual exclusion — only one thread can enter the critical section at a time.
# Python's threading.Lock has two core methods: acquire() and release().
# Always prefer the context manager (with lock:) — it auto-releases even if an exception occurs.
from threading import Lock

lock = Lock()

# Two core methods
lock.acquire()   # Grabs the lock — blocks if another thread holds it
lock.release()   # Releases the lock — must always be called, even on error

# ---- Manual acquire/release (error-prone) ----
counter = 0

lock.acquire()
try:
    counter += 1
finally:
    lock.release()  # Must manually release — easy to forget

# ---- Context manager (preferred) ----
# with lock: automatically calls acquire() on entry and release() on exit
with lock:
    counter += 1


# =============================================
# RANDOM — Utility Reference
# =============================================
# Used throughout async experiments to simulate variable I/O wait times.
import random

random.randint(1, 3)    # Integer only → 1, 2, or 3 (inclusive)
random.uniform(1, 3)    # Any float  → e.g. 1.0, 1.47, 2.83, 3.0