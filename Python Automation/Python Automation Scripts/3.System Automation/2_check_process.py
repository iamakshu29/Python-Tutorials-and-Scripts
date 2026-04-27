# Write a script that checks if a process is running and restarts it if not.

import subprocess
import re
reg = r"Notepad\.exe"
result = subprocess.run(["tasklist"],check=True, capture_output=True, text=True)

try:
    if re.search(reg,result.stdout).group():
        print("Process is running")
except AttributeError:
    print("Process not running, starting it....")
    subprocess.Popen(["notepad.exe"])

# this is for one time check only and if not running it will start it.
# to continuously monitor it, we wse while true:
#  but remember to add timestamp else it will crash the cpu