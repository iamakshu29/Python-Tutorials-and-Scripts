# =====================================================================================
# Day 6 — Date & Time Operations (datetime module)
# =====================================================================================
# The `datetime` module provides classes for working with dates and times in Python.
# Key classes used in this script:
#   datetime  — Combines date and time (year, month, day, hour, minute, second, microsecond)
#   date      — Represents only the date part (year, month, day)
#   timedelta — Represents a duration / difference between two dates or times
#
# DevOps Relevance: Log timestamp parsing, scheduling tasks, calculating uptimes,
# setting expiry dates, and generating time-based reports.
# =====================================================================================


# =====================================================================================
# SECTION 1: GETTING CURRENT DATE & TIME USING datetime
# =====================================================================================

from datetime import datetime  # Import the datetime class from the datetime module

# datetime.now() — Returns the current local date and time as a datetime object.
# Output format: YYYY-MM-DD HH:MM:SS.microseconds (e.g., 2026-04-26 11:50:15.123456)
x = datetime.now()
print(x)

# Accessing individual components of the datetime object using attributes:
#   .year  — Returns the year (e.g., 2026)
#   .month — Returns the month as an integer (1-12)
#   .day   — Returns the day of the month (1-31)
# Other available attributes: .hour, .minute, .second, .microsecond
list = [f"year is {x.year}",f"month is {x.month}",f"day is {x.day}"]
print(list)


# =====================================================================================
# SECTION 2: WORKING WITH date OBJECTS (DATE ONLY, NO TIME)
# =====================================================================================

from datetime import date  # Import the date class (lighter than datetime, no time info)

# date.today() — Returns the current local date (without time).
# Output format: YYYY-MM-DD (e.g., 2026-04-26)
x = date.today()
print(f"Todays date is {x}")

# Same attributes as datetime but only date-related:
#   .year, .month, .day
print(f"Year is {x.year}")
print(f"Month is {x.month}")
print(f"Day is {x.day}")


# =====================================================================================
# SECTION 3: PARSING DATE STRINGS WITH strptime()
# =====================================================================================
# strptime() — Converts a date STRING into a datetime OBJECT.
# "strptime" stands for "string parse time".
# It takes two arguments:
#   1. The date string to parse (e.g., "2024-31-05")
#   2. The format string that describes the string's structure
#
# Common format codes:
#   %Y — 4-digit year (2024)     %m — 2-digit month (05)    %d — 2-digit day (31)
#   %H — Hour (24-hr)            %M — Minute                %S — Second
#
# The opposite operation is strftime() — converts a datetime OBJECT to a STRING.

# Formatting the date objects into readable strings
d = "2024-31-05"

# Here the format "%Y-%d-%m" tells Python: year-day-month (not the usual year-month-day).
# .date() extracts only the date part from the resulting datetime object.
# Result: 2024-05-31 (May 31, 2024)
print(datetime.strptime(d,"%Y-%d-%m").date())


# =====================================================================================
# SECTION 4: TIME ARITHMETIC WITH timedelta
# =====================================================================================
# timedelta — Represents a duration (difference between two points in time).
# You can add or subtract timedelta from datetime objects to calculate future/past dates.
# timedelta supports: days, seconds, microseconds, milliseconds, minutes, hours, weeks

from datetime import datetime, timedelta  # Re-import with timedelta included

# Current date and time
now = datetime.now()
print("Current Time:", now)

# Add 2 years (approx. 730 days)
# NOTE: timedelta does not have a "years" parameter, so 2 years ≈ 730 days.
# For exact year arithmetic, consider the `dateutil.relativedelta` library.
after_2_years = now + timedelta(days=730)
print("After 2 Years:", after_2_years)

# New time after 2 days
# timedelta(days=2) creates a duration of exactly 2 days.
# Adding it to `now` gives the datetime 48 hours from now.
new_time = now + timedelta(days=2)
print("New Time (+2 days):", new_time)

# Time difference — Subtracting two datetime objects returns a timedelta object.
# This shows the exact duration between the two points in time.
# Result: 2 days, 0:00:00
print("Time Difference:", new_time - now)