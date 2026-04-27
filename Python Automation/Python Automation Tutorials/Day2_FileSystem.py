# =====================================================================================
# Day 2 — File system ops (os, pathlib, shutil)
# =====================================================================================
# This script covers three core Python modules for filesystem operations:
#   1. os       — Low-level OS interface (directories, env vars, permissions)
#   2. pathlib  — Object-oriented filesystem paths (modern, preferred approach)
#   3. shutil   — High-level file/directory operations (copy, move, archive)
# These are essential for DevOps tasks like deployment automation, log management,
# backup scripts, and configuration management.
# =====================================================================================

import os  # Standard library module for interacting with the operating system

# =====================================================================================
# SECTION 1: DIRECTORY OPERATIONS USING os MODULE
# =====================================================================================

# os.mkdir() — Creates a single directory.
# Raises FileExistsError if the directory already exists.
os.mkdir("example_dir")

# os.mkdirs() — Creates nested (multi-level) directories recursively.
# It creates all intermediate-level directories needed to contain the leaf directory.
# NOTE: The correct function name is os.makedirs(), not os.mkdirs().
os.mkdirs("parent_dir/child_dir")

# os.listdir() — Returns a list of names of entries in the given directory.
# "." refers to the current working directory.
print("Content of directory are ", os.listdir("."))

# os.getcwd() — Returns the current working directory as a string.
# Useful for knowing where your script is executing from.
print("Current Working Directory is ", os.getcwd())

# os.chdir() — Changes the current working directory to the specified path.
# After this call, all relative paths will resolve from "example_dir".
os.chdir("example_dir")

# os.rmdir() — Removes (deletes) a single empty directory.
# Raises OSError if the directory is not empty.
os.rmdir("example_dir")

# os.removedirs() — Removes directories recursively (from leaf to parent).
# It removes child_dir first, then parent_dir — but only if each is empty.
os.removedirs("parent_dir/child_dir")

# DevOps Relevance: Automating directory setup for deployments, cleaning temp directories, and managing logs.

# =====================================================================================
# SECTION 2: ENVIRONMENT VARIABLES USING os.environ
# =====================================================================================
# os.environ is a mapping object (dict-like) representing the process environment.
# It allows reading, setting, and listing all environment variables.
# This is critical in DevOps for managing configs, secrets, and runtime settings.

# os.environ.get() — Safely retrieves an environment variable's value.
# Returns None if the variable doesn't exist (avoids KeyError).
home_dir = os.environ.get("HOME")

# Direct assignment to os.environ — Sets a temporary environment variable.
# This variable only exists for the lifetime of the current process.
os.environ["MY_VAR"] = "123"

# dict(os.environ) — Converts all environment variables to a standard dictionary.
# Useful for inspecting or logging the full environment.
env_vars = dict(os.environ)

# =====================================================================================
# SECTION 3: FILE PERMISSIONS USING os MODULE
# =====================================================================================
# Managing file permissions is essential for security in DevOps — ensuring
# config files, scripts, and secrets have the correct access levels.

# os.chmod() — Changes the file permissions using octal notation.
# 0o644 means: Owner=read+write (6), Group=read (4), Others=read (4) → rw-r--r--
os.chmod("file.txt", 0o644)  # rw-r--r--

# os.stat() — Returns detailed file metadata (size, permissions, timestamps, etc.).
# .st_mode gives the raw permission bits; oct() converts to octal string.
# [-3:] extracts just the permission digits (e.g., '644').
permissions = oct(os.stat("file.txt").st_mode)[-3:]

# os.access() — Checks if the current user has specific permissions on a file.
# os.R_OK = readable, os.W_OK = writable, os.X_OK = executable
# Returns True or False.
is_readable = os.access("file.txt", os.R_OK)
is_writable = os.access("file.txt", os.W_OK)
is_executable = os.access("file.txt", os.X_OK)


# =====================================================================================
# SECTION 4: PATHLIB — OBJECT-ORIENTED FILESYSTEM PATHS
# =====================================================================================
# pathlib is the modern, Pythonic way to handle filesystem paths.
# It provides a Path class that wraps paths as objects with methods,
# making code cleaner and more readable compared to os.path string manipulation.

from pathlib import Path  # Import the Path class from pathlib module

# Path.mkdir() — Creates a single directory (similar to os.mkdir).
Path("example_dir2").mkdir()

# Path.mkdir(parents=True, exist_ok=True) — Creates nested directories.
# parents=True  → Creates all intermediate parent directories if they don't exist.
# exist_ok=True → Does NOT raise an error if the directory already exists.
Path("parent_dir2/child_dir2").mkdir(parents=True, exist_ok=True)

# Path.rmdir() — Removes an empty directory (similar to os.rmdir).
Path("example_dir2").rmdir()

# Path.read_text() — Reads the entire contents of a file as a string.
# Equivalent to: open("config.txt").read()
content = Path("config.txt").read_text()

# Path.write_text() — Writes a string to a file, creating it if it doesn't exist.
# Overwrites existing content. Equivalent to: open("output.txt", "w").write("hello")
Path("output.txt").write_text("hello")

# =====================================================================================
# SECTION 5: DIRECTORY ITERATION & FILE SEARCHING WITH PATHLIB
# =====================================================================================

# Path.iterdir() — Iterates over all entries (files and subdirectories) in a directory.
# Returns Path objects for each item. Does NOT recurse into subdirectories.
for file in Path("/var/log").iterdir():
    print(file)

# Path.glob(pattern) — Finds files matching a pattern in the CURRENT directory only.
# "*.log" matches all files ending with .log (e.g., syslog.log, error.log).
for file in Path("/var/log").glob("*.log"):
    print(file)

# Path.rglob(pattern) — Recursive glob; searches the directory AND all subdirectories.
# Equivalent to glob("**/*.log"). Useful for finding all log files in a directory tree.
for file in Path("/var/log").rglob("*.log"):
    print(file)


# =====================================================================================
# SECTION 6: SHUTIL — HIGH-LEVEL FILE & DIRECTORY OPERATIONS
# =====================================================================================
# shutil provides high-level operations for copying, moving, and archiving files.
# Unlike os, shutil can copy file contents, metadata, and entire directory trees.

import shutil  # Import shutil for high-level file operations

# shutil.copy(src, dst) — Copies a file's content and permissions to a new location.
# Does NOT preserve metadata like timestamps. Creates dst if it doesn't exist.
shutil.copy("source.txt", "destination.txt")

# shutil.copy2(src, dst) — Same as copy(), but ALSO preserves file metadata
# (timestamps, permissions, etc.). Preferred when you need an exact replica.
shutil.copy2("source.txt", "destination.txt")

# shutil.copytree(src, dst) — Recursively copies an entire directory tree.
# The destination directory must NOT already exist (it will be created).
shutil.copytree("source_dir", "destination_dir")

# shutil.move(src, dst) — Moves a file or directory to a new location.
# Can also be used to rename files/directories. Works across filesystems.
shutil.move("old_name.txt", "new_name.txt")

# os.rename(src, dst) — Renames a file or directory.
# Unlike shutil.move(), this does NOT work across different filesystems.
os.rename("old_name.txt", "new_name.txt")

# shutil.disk_usage(path) — Returns disk usage statistics as a named tuple
# with attributes: total, used, and free (all in bytes).
# // (1024**3) converts bytes to gigabytes using integer division.
usage = shutil.disk_usage('.')
print(f'Total space: {usage.total // (1024**3)} GB')
print(f'Free space: {usage.free // (1024**3)} GB')

# shutil.make_archive() — Creates an archive file (e.g., .tar.gz, .zip).
# Parameters: base_name (output filename without extension),
#             format ("gztar", "zip", "tar", "bztar", "xztar"),
#             root_dir (directory to archive).
shutil.make_archive(base_name="backup", format="gztar", root_dir="src") # (output_filename, format, dir_to_archive)
shutil.make_archive("backup", "zip", root_dir="src")

# shutil.unpack_archive() — Extracts an archive to a specified directory.
# Automatically detects format based on file extension (.zip, .tar.gz, etc.).
shutil.unpack_archive(filename="backup.zip",extract_dir="restored")

# DevOps Relevance: Backup scripts, deployment scripts, moving log files, and versioned configuration management.