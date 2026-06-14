# Queue - we know it as DB...simple

# Methods
# 1. q.put() -> Adds an item to the queue.
# 2. q.get() -> Removes and returns the first item (FIFO).
# 3. qsize() -> Check size
# 4. q.empty() -> Check isEmpty
# 5. q.full() -> Check isFull

# can configured a max size
# q = Queue(maxsize=5)

# Type of Queue
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


# ---------------------------------------------------
### What a Lock is conceptually (mutual exclusion — only one thing at a time)
# A Lock is the simplest synchronization primitive used to enforce mutual exclusion (mutex)
# At any moment, only one thread is allowed inside a critical section of code.

from threading import Lock

lock = Lock()

# We have 2 method basically
lock.acquire()
lock.release()

# But we dont have to manually release it as we have a "context manager" already

# Instead of
counter = 0

lock.acquire()

try:
    counter += 1
finally:
    lock.release()

# We use

with lock:
    counter += 1

# ---------------------------------------------------
random.randint(1, 3)   # only whole numbers → 1, 2, or 3
random.uniform(1, 3)   # any float → 1.0, 1.23, 2.77, 3.0