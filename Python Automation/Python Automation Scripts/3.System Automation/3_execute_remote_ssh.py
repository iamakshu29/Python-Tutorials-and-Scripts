# Execute a remote SSH command using Python and capture stdout.

import subprocess

remote_command = "cd Docker && ls"
ssh_host = "ubuntu@ec2-54-85-136-219.compute-1.amazonaws.com"
ssh_key = "c:/Users/Lenovo/Downloads/jenkins.pem"

result = subprocess.run(["ssh","-i",ssh_key,ssh_host,remote_command],check=True,capture_output=True,text=True)
try:
    result = subprocess.run(
        ["ssh", "-i", ssh_key, ssh_host, remote_command],
        capture_output=True,
        text=True,
        check=True
    )
    print(result.stdout)

except subprocess.CalledProcessError as e:
    print("Command failed with return code", e.returncode)
    print("Error output:\n", e.stderr)