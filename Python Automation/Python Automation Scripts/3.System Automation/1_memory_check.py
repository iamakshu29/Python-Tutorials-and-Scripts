# Run df -h via Python, parse output, and alert if any partition > 80% usage.
    # can be done with shutil also

# Can use regex but AS the output is column-based so splitting is RECOMMENDED, as it is more reliable and error-free
import subprocess
import re
try:
    result = subprocess.run(["df","-h"],check=True, capture_output=True, text=True)

except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")
    print(e.stderr)
    raise

ans = result.stdout
print(ans)
# usage_regex = r"\b\d{1,3}%"
# mount_regex = r"/[a-z]{0,}"
sol = ans.strip().splitlines()
threshold = 10

alerts = []

for line in sol[1:]:
    parts = line.split() 
    if len(parts) < 6: 
        continue

# using regex
    # use_percent = re.search(usage_regex,line).group()
    # mount_point = re.search(mount_regex,line).group()

# using split()
    use_percent = parts[-2]
    mount_point = parts[-1]

    usage = int(use_percent.rstrip('%'))
    if usage > threshold:
        alerts.append((mount_point, usage))

if alerts:
    for mount, usage in alerts:
        print(f"ALERT: {mount} usage at {usage}%")
else:
    print("All partitions below threshold")

# -----------------------------------------------------------------------
import shutil

mount_point = ["C://","D://","E://"]
for i in mount_point:
    total, used, free = shutil.disk_usage(i)
    usage = used / total * 100
    print(f"{i} usage: {usage:.1f}%")
