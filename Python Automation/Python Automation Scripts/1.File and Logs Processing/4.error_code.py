# Count how many times each error code (400/403/404/500) appears.

import re

status_regex = r"status=(\d+)"
path = "Python Scripts/Scripts/File and Logs Processing/error_code.log"
error_code = {400,403,404,500}
code_count = {}

# line = "2025-12-12T10:15:23.120Z INFO  GET  /api/users        status=200 duration=45ms"
# print(re.search(status_regex,line).group(1))

with open(path) as f:
    for line in f:
        search_code = re.search(status_regex,line)
        if not search_code:
            continue

        code = int(search_code.group(1)) # get the code value

        if code in error_code: # search in error_code list, only add in dict, if present
            code_count[code] = code_count.get(code, 0) + 1 # add in dict.

print(code_count)