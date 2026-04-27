# Typical tasks:
# Running kubectl/helm commands
# Running terraform apply/plan
# Interacting with docker CLI
# Executing OS-level commands in CI/CD

import subprocess
import shlex

def run_cmd(command):
    print(f"\n>> {command}")
    
    try:
        # shlex.split allows passing a string safely
        result = subprocess.run(
            shlex.split(command),
            capture_output=True,
            text=True,
            timeout=300  # 5 min safety timeout
        )
    except FileNotFoundError:
        print("ERROR: Command not found")
        return
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("EXIT CODE:", result.returncode)
        print(result.stderr)


# run_cmd("terraform apply --auto-approve")
# run_cmd("kubectl apply -f pod.yml")
# run_cmd("docker ps")
