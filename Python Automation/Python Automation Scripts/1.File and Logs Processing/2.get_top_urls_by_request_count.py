# From an Nginx access log, print the top 2 URLs by request count.

# workflow 
    # 1. read the file -> with open
    # 2. use regex to extract the path from each line 
    # 3. we create a "dict" where key is the path and everytime there is path which already present as key, we increase its value by 1. 
    # 4. we sort the dict based on value and get the top n keys by count.

import re
import json

path = "Python Scripts/Scripts/File and Logs Processing/nginx_access.log"
urls = r'[A-Z]+\s(/[^\s]*)\sHTTP/[0-9\.]+'
path_dict = {}

with open(path,'r') as f:
    for line in f:
        path = re.search(urls,line)
        if not path:
            continue
        # print(path)
        key = path.group(1)
        # print(key)
        if key not in path_dict:
            path_dict.update({key:1})
        else:
            path_dict[key] += 1

# sort in descending and get the values from 0 to 2 (2 excluded)
sorted_path = dict(sorted(path_dict.items(), key=lambda item: item[1], reverse=True)[:2])  

print(sorted_path)
# print(path_dict)

# pretty prints dict by convert it to JSON
    # print(json.dumps(path_dict, indent=1))

# NOTE
    # re.search() returns an object not a string
    # to convert into string we do re.search().group()
    # group() is a method of a match object returned by re.search() or re.match(). 
    # It extracts the part of the string that matched your regex.
    # uncomment print(path) and print(key) to see the matched object and the matched string 