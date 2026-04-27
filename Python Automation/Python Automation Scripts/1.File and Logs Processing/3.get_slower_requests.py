# Given a log file, find all requests slower than 200 ms.

#  workflow
# 1. get the duration and request either by regex or split()
# 2. then add the request to set so that only unique values came as result.

import re

req_regex = r"\b(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\b"
duration_regex = r"duration=(\d+)ms"
path = "Python Scripts/Scripts/File and Logs Processing/slow_request.log"

def slow_req(path):
    slow_req = set()

    with open(path,'r') as f:
        for line in f:
            duration_match = re.search(duration_regex,line) # getting the duration value
            if not duration_match:
                continue

            duration = int(duration_match.group(1))
            if duration <= 200:
                continue

            request = re.search(req_regex,line)
            if not request:
                continue
            slow_req.add(request.group().strip()) # update that request 

    return slow_req

print(slow_req(path))


def slow_req_using_split(path):
    slow_req_list = set()

    with open(path,"r") as f:
        for line in f:
            log = line.strip().split()
            request = log[2]

            duration = log[-1]
            duration_ms = int(duration.split("=")[1].rstrip("ms"))
            if duration_ms <= 200:
                continue

            slow_req_list.add(request)

    return slow_req_list

print(slow_req_using_split(path))