# 3_errorHandling.py — Exception Handling Best Practices

# =============================================
# EXAMPLE 1: Graceful key handling in loops
# =============================================
# 'user' is optional so .get() is used with a fallback.
# 'event_id' is mandatory — KeyError is caught if missing.
def summarize_logs(log_entries):
    summary = []
    for entry in log_entries:
        try:
            user = entry.get('user', 'system')  # Default to 'system' if key absent
            event_id = entry['event_id']  # Raises KeyError if missing
            summary.append(f"{event_id}:{user}")
        except KeyError:
            summary.append("ERROR:Missing-Data")
        except (TypeError, AttributeError):  # Handles None or non-dict entries
            summary.append("ERROR:Invalid-Entry")
 
    return summary
 
logs = [
    {'event_id': 101, 'user': 'alice'},
    {'event_id': 102},
    None,
    {'user': 'bob'}
]
 
# print(summarize_logs(logs))

# =============================================
# EXAMPLE 2: Raise exceptions over returning None
# =============================================
# Raising exceptions is better than returning None/False —
# it forces the caller to handle errors explicitly.
def process_server(server_list):
    if not isinstance(server_list, list):
        raise TypeError("Input 'server_list' must be a type of list")  # Caller passed wrong type

    if len(server_list) == 0:
        # print is enough here — empty list is a valid edge case, not an error
        print("There are no servers to process")
        return
    
    print(f"Processing {server_list} servers")

# process_server('abc') # will raise TypeError
# process_server([])
# process_server(["nginx","apache"])


# =============================================
# EXAMPLE 3: Combining TypeError and ValueError
# =============================================
# Use TypeError for wrong types, ValueError for out-of-range values — keeps errors specific.
def set_deployment_replicas(count):
    if not isinstance(count,int):
        raise TypeError(f"Replica count must be int, got {type(count).__name__}")
    if count < 0 or count > 100:
        raise ValueError(f"Replica count must be between 0 and 100")

    print(f"Replica set to {count}")

# for val in [5,-2,"three",150]:
#     try:
#         set_deployment_replicas(val)
#     except (TypeError, ValueError) as e:
#         print(f"Caught error: {e}")


# =============================================
# EXAMPLE 4: Context Managers (with statement)
# =============================================
# 'with' guarantees the file is closed even if an exception is raised inside the block —
# no need for a manual try/finally to call f.close().
try:
    with open("my.log.txt","w") as f:
        f.write("first line")
        result = 1/0  # ZeroDivisionError raised here — second write never runs
        f.write("second line")
except:
    print("error is there")
print(f"File closed: {f.closed}")  # Always True — 'with' closed it automatically