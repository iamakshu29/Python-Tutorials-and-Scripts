# Create a Python CLI with argparse that accepts:
# --file <path>
# --env <dev|prod>
# --verbose

import argparse

parser = argparse.ArgumentParser(description="Example Python CLI")

parser.add_argument("-f","--file",required=True, help="file")
parser.add_argument("-e","--env",required=True,choices=["dev", "prod"], help="environment name")
parser.add_argument("-v", "--verbose",action="store_true",help="Enable verbose output")

arguements = parser.parse_args()

if arguements.verbose:
        print("Verbose mode enabled")

print(f"File: {arguements.file}")
print(f"Environment: {arguements.env}")
