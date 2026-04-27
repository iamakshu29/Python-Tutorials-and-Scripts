import subprocess
# CAPTURING OUTPUT AND GETTING OUTPUT ON TERMINAL ARE TWO DIFFERENT THINGS.

# text=True is useful where the output is capture in stdout/stderr
    # Converts the command’s input/output from bytes to string automatically.
# check=True tells subprocess.run() to treat a non-zero exit status as an error.

try:
# MOST IMPORTANT IN subprocess -> run() object
# Run command and display result (didn't capture the output) and return a CompletedProcess instance.
    # ans = subprocess.run(["echo", "Hello"])
    # print(ans)
    
# use capture_output=True to capture output
    ans = subprocess.run(["echo", "Hello"], check=True, text=True, capture_output=True)
    # print(ans) # it will return only CompletedProcess instance.
    # print(ans.stdout) # it will return output.
    # print(ans.stderr) # it will return error.
    # print(ans.returncode) # it will return exit code.


# Run command and raise exception if it returns non-zero.
    # ans = subprocess.check_call(["echo", "Namaste"])
    # print(ans)  # return 0 if success

    # ans = subprocess.check_call(["false"])
    # print(ans) # return error so exception block will run.

except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")

# -----------------------------------------------------------------------------------------------------------------

# act as ls | grep index

# Popen is a class in Python’s subprocess module that allows you to start and control external processes.
    #  used when we need pipe (|) related output or to start a process

lsProcess = subprocess.Popen(["ls"], stdout=subprocess.PIPE, text=True)
grepProcess = subprocess.Popen(
    ["grep", "index"], stdin=lsProcess.stdout,
    stdout=subprocess.PIPE, text=True)
output, error = grepProcess.communicate()
# communicate() reads the output and error streams of the process until it finishes.

# print(f"output is {output}")
# print(f"error is {error}")

# stdout=subprocess.PIPE: Captures the standard output of ls to be passed to another process.
# stdin=lsProcess.stdout: Feeds the output of lsProcess into grepProcess as input.
# stdout=subprocess.PIPE: Captures the output of grepProcess.
# RESULT - grepProcess is a Popen object representing the running grep command, with input coming from ls

# -----------------------------------------------------------------------------------------------------------------------------------
# subprocess.call()
    # Executes the command.
    # Returns the exit code of the command.
    # Does not raise an exception if the command fails (non-zero exit code). You have to manually check the return value.
ans = subprocess.call(["python", "--version"])
if ans == 0:
    print("Command executed.")
else:
    print("Command failed.", ans)

# | Function     | Return       | Failure behavior                             |
# | ------------ | ------------ | -------------------------------------------- |
# | `call`       | Exit code    | Returns non-zero code; no exception          |
# | `check_call` | 0 if success | Raises `CalledProcessError` if non-zero exit |


# NOTE
# run() is the new recommended API and gives full control than any other object like call(), check_call()