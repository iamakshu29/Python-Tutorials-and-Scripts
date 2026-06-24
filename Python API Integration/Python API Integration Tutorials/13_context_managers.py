# Without Using Contnext Manager
# f = None
# try:
#     f = open("my_log.txt", "w")
#     f.write("First Line \n")
#     # creating an error
#     result = 1 / 0
#     f.write("Second Line")
# except ZeroDivisionError as e:
#     print(f"Error has occured, {e}")
# finally:
#     if f:
#         print("Closing file")
#         f.close()
# # checking if file is closed
# print(f"File closed: {f.closed}")

# -------------------------------------------------------------------

# using Context Manager 'with'
# f = None
# try:
#     with open("my.log.txt", "w") as f:
#         f.write("first line")
#         result = 1 / 0
#         f.write("second line")
# except ZeroDivisionError as e:
#     print(f"error is there {e}")
# # file will close by itself
# print(f"File closed: {f.closed}")

# Creating a file in tempdir using contenxt manager.
import tempfile
import os

# with tempfile.TemporaryDirectory() as tempdir:
#     print(f"Created temp dir, {tempdir}")

#     test_file = os.path.join(tempdir,"test.txt")

#     with open("test.txt","w") as f:
#         f.write("Hello from temp directory.")

#     print(f"Files inside tempdir: {os.listdir(tempdir)}")


# ----------------------------------------------------------------------------
# Creating Custom Context Manager using dunder enter and exit methods
class MyContextManager:
    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        print("setup complete")
        return "a simple value"

    def __exit__(
        Self, *args
    ):  # we know we have 3 positional args for the exception i.e. __exit__(self, excecption_type,excecption_val, exception_traceback)
        print("Teardown")

        for arg in args:
            print(arg)

        return False  # This is re raise an exception
        # return True # This will not raise an error. Error Suppressed


# Using the context manager
# with MyContextManager(timeout=30) as cm:
#     print(cm)
#     print("Inside the block")

# Using the context manager with error
# with MyContextManager(timeout=30) as cm:
#     print(cm)
#     print("Inside the block")
#     raise ValueError("Simulated problem")

# -------------------------------------------------------------------------------
# Creating Custom Context Manager with contextmanager decorator
from contextlib import contextmanager


@contextmanager
def change_dir(destination):
    original_dir = os.getcwd()
    try:
        print(f"Changing into {destination}")
        os.makedirs(destination, exist_ok=True)
        os.chdir(destination)
        yield os.getcwd()
    finally:
        print(f"reverting to original dir: {original_dir}")
        os.chdir(original_dir)


print(f"Start: {os.getcwd()}")

# with change_dir("temp_dir") as new_dir:
#     print(f"Inside: {new_dir}")

print(f"End: {os.getcwd()}")
