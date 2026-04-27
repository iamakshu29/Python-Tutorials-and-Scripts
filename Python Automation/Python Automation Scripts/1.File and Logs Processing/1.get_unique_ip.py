# Parse a log file and extract all unique IP addresses.

# workflow 
    # 1. read the file -> with open
    # 2. use regex to extract the path from each line 
    # 3. loop through line and update the matched value to a "set" method to get all unique IP addresses.
    # 4. print the set to get uniques IPs

import re

path = "Python Scripts/Scripts/File and Logs Processing/unique_ip.log"

# to make it raw string literal and \ not be assumed as escape character we use r""
ip_regex = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"

unique_ips = set()

with open(path,'r') as f:
    for line in f:
        get_ip = re.findall(ip_regex,line) # .findall(), for searching multiple occurance in same line
        if not get_ip:
            continue
        unique_ips.update(get_ip) 

print(unique_ips)