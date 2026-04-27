# Tasks:
# Create a directory structure logs/backup/YYYY-MM-DD.
# Copy all .log files from one directory to another.

from datetime import date
from pathlib import Path
import shutil

# Create a directory structure logs/backup/YYYY-MM-DD.

#  create dir structure
curr_date = date.today().isoformat()
dest_dir = Path("/scripts/log/backup") / curr_date

#  create dest_dir
dest_dir.mkdir(parents=True, exist_ok=True)

base_dir = Path("/scripts/log/backup/prev_day")

# Copy all .log files from base_dir to dest_dir.
for log_file in base_dir.glob("*.log"):
    shutil.copy(log_file,dest_dir)