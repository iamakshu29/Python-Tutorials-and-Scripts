# =====================================================================================
# Day 5 — Regular Expressions (re module)
# =====================================================================================
# The `re` module provides support for regular expressions in Python.
# Regex is a powerful pattern-matching language used for searching, extracting,
# and validating text data.
#
# Key functions used in this script:
#   re.search(pattern, text)  — Scans the ENTIRE string for the first match.
#   re.match(pattern, text)   — Matches only at the BEGINNING of the string.
#   re.findall(pattern, text) — Returns a LIST of ALL non-overlapping matches.
#
# Common regex syntax used below:
#   \b       — Word boundary (ensures match isn't part of a larger word)
#   \d       — Any digit [0-9]
#   {n,m}    — Quantifier: match between n and m times
#   (?:...)  — Non-capturing group (groups pattern without creating a capture group)
#   +        — One or more occurrences
#   ?        — Zero or one occurrence
#   [...]    — Character class (match any single character inside brackets)
#   ^        — Start of string anchor
#   $        — End of string anchor
#
# DevOps Relevance: Parsing logs, extracting IPs/timestamps, validating configs,
# and processing command output.
# =====================================================================================

import re  # Standard library module for regular expression operations

# =====================================================================================
# PATTERN 1: EXTRACT IP ADDRESS
# =====================================================================================
# Regex: \b(?:\d{1,3}\.){3}\d{1,3}\b
# Breakdown:
#   \b              — Word boundary to avoid partial matches
#   (?:\d{1,3}\.){3} — Non-capturing group: 1-3 digits followed by a dot, repeated 3 times
#                       Matches "192." "168." "1."
#   \d{1,3}         — Final octet: 1-3 digits (e.g., "42")
#   \b              — Closing word boundary
# Result: Matches IPv4 addresses like 192.168.1.42
text = "Server error from 192.168.1.42 at 10:32"
ip_regex = re.search(r"\b(?:\d{1,3}\.){3}\d{1,3}\b",text) # => \b( number. ){3}number\b, number = [0-9]{1,3}
print(ip_regex.group())


# =====================================================================================
# PATTERN 2: EXTRACT EMAIL ADDRESS
# =====================================================================================
# Regex: \b[A-Za-z0-9.-]+@[a-z]+\.[a-z]{2,}\b
# Breakdown:
#   [A-Za-z0-9.-]+  — Local part: one or more alphanumeric chars, dots, or hyphens
#   @               — Literal @ symbol
#   [a-z]+          — Domain name: one or more lowercase letters (e.g., "gmail")
#   \.              — Literal dot separator
#   [a-z]{2,}       — Top-level domain: at least 2 lowercase letters (e.g., "com")
# Result: Matches emails like Iam123@gmail.com
text = "my mail id is Iam123@gmail.com yes it is"
mail_regex = re.search(r"\b[A-Za-z0-9.-]+@[a-z]+\.[a-z]{2,}\b",text)
print(mail_regex.group())


# =====================================================================================
# PATTERN 3: EXTRACT ISO 8601 TIMESTAMP
# =====================================================================================
# Regex: \b\d{4}(?:-\d{2}){2}T(?:\d{2}:){2}\d{2}\.\d{3}Z
# Breakdown:
#   \d{4}           — Year: exactly 4 digits (e.g., "2025")
#   (?:-\d{2}){2}   — Month and Day: dash + 2 digits, repeated 2 times ("-12-12")
#   T               — Literal 'T' separator between date and time
#   (?:\d{2}:){2}   — Hours and Minutes: 2 digits + colon, repeated 2 times ("10:15:")
#   \d{2}           — Seconds: exactly 2 digits ("23")
#   \.\d{3}         — Milliseconds: dot + 3 digits (".120")
#   Z               — UTC timezone indicator
# Result: Matches timestamps like 2025-12-12T10:15:23.120Z
# NOTE: re.match() is used here because the timestamp is at the START of the string.
text = "2025-12-12T10:15:23.120Z INFO  GET  /api/users"
time_regex = re.match(r"\b\d{4}(?:-\d{2}){2}T(?:\d{2}:){2}\d{2}\.\d{3}Z",text)
print(time_regex.group())


# =====================================================================================
# PATTERN 4: EXTRACT LOG LEVEL (SINGLE MATCH)
# =====================================================================================
# Regex: \[[A-Za-z]{4,}\]
# Breakdown:
#   \[              — Literal opening bracket (escaped because [ is special in regex)
#   [A-Za-z]{4,}    — 4 or more alphabetic characters (matches ERROR, WARNING, INFO etc.)
#   \]              — Literal closing bracket
# NOTE: re.match() checks only at the beginning of the string.
# Result: Matches "[ERROR]"
text = "[ERROR] Service started"
level_regex = re.match(r"\[[A-Za-z]{4,}\]",text)
print(level_regex.group())


# =====================================================================================
# PATTERN 5: EXTRACT ALL LOG LEVELS (MULTIPLE MATCHES)
# =====================================================================================
# Regex: \[(INFO|ERROR|WARNING)\]
# Breakdown:
#   \[                      — Literal opening bracket
#   (INFO|ERROR|WARNING)    — Capturing group with alternation (matches any of the three)
#   \]                      — Literal closing bracket
# re.findall() returns ALL matches as a list. Since there's a capturing group,
# it returns the captured group content (not the full match with brackets).
# Result: ['INFO', 'ERROR', 'WARNING']
text = "[INFO] Service started [ERROR] Failed to connect to DB [WARNING] Disk space low"
level_regex = re.findall(r"\[(INFO|ERROR|WARNING)\]",text)
print(level_regex)


# =====================================================================================
# PATTERN 6: EXTRACT UNIX FILE PATH
# =====================================================================================
# Regex: /(?:[a-z]{3,}/){3}[a-z]{4,}\.[a-z]{2,}
# Breakdown:
#   /                  — Leading slash (root directory)
#   (?:[a-z]{3,}/){3}  — Three directory levels: 3+ lowercase chars + slash, repeated 3 times
#                        Matches "var/log/nginx/"
#   [a-z]{4,}          — Filename: 4+ lowercase letters (e.g., "access")
#   \.                 — Literal dot separator
#   [a-z]{2,}          — File extension: 2+ lowercase letters (e.g., "log")
# Result: Matches paths like /var/log/nginx/access.log
text = "/var/log/nginx/access.log"
# text = "/etc/systemd/system/myservice.service"
# text = "/home/user/scripts/deploy.sh"
path_regex = r"/(?:[a-z]{3,}/){3}[a-z]{4,}\.[a-z]{2,}"
match = re.search(path_regex,text)
print(match.group())


# =====================================================================================
# PATTERN 7: EXTRACT VERSION NUMBER (Semantic Versioning)
# =====================================================================================
# Regex: \b(?:[0-9]+\.){2}[0-9]+\b
# Breakdown:
#   \b               — Word boundary
#   (?:[0-9]+\.){2}  — Major and Minor versions: one or more digits + dot, repeated 2 times
#                      Matches "11." "21."
#   [0-9]+           — Patch version: one or more digits (e.g., "62")
#   \b               — Closing word boundary
# Result: Matches version strings like 11.21.62
text = "nginx version: 11.21.62"
version_regex = r"\b(?:[0-9]+\.){2}[0-9]+\b"
match = re.search(version_regex,text)
print(match.group())


# =====================================================================================
# PATTERN 8: EXTRACT URL
# =====================================================================================
# Regex: \bhttps?://[^\s]+\b
# Breakdown:
#   \b          — Word boundary
#   http        — Literal "http"
#   s?          — Optional 's' (matches both "http" and "https")
#   ://         — Literal "://"
#   [^\s]+      — One or more non-whitespace characters (captures the rest of the URL)
#   \b          — Closing word boundary
# Result: Matches URLs like https://internal-server.local/logs
text = "Check logs at https://internal-server.local/logs"
url_regex = r"\bhttps?://[^\s]+\b" # https? -> means s can occur 0 or 1 times (for http and https)
match = re.search(url_regex,text)
print(match.group())


# =====================================================================================
# PATTERN 9: VALIDATE HOSTNAME
# =====================================================================================
# Regex: ^[a-zA-Z-.0-9]+$
# Breakdown:
#   ^              — Start of string anchor (ensures match begins at the start)
#   [a-zA-Z-.0-9]+ — One or more of: letters, hyphens, dots, or digits
#   $              — End of string anchor (ensures match goes to the end)
# Together, ^ and $ ensure the ENTIRE string is a valid hostname (full string validation).
# Result: Matches hostnames like "server1.local" or "web-server-02"
text = "server1.local"
# text = "web-server-02"
hostname_regex = r"^[a-zA-Z-.0-9]+$"
match = re.search(hostname_regex,text)
print(match.group())