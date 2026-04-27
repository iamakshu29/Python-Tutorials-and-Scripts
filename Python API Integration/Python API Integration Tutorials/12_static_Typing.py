"""
 python -m mypy 12_static_Typing.py run this as unable to isntall Pylance.
 if running above command, we get error if we reassing the variable type to a different from mentioned one.

Syntax Below
"""
# Variable Annotation
config_path: str = "/etc/app.conf"
is_enable: bool = True
retry_count: int = 3
servers: list[str] = ["web1","web2"]
settings: dict[str,int | str] = {
    "port": 8080,
    "user": "myuser"
}


# Function Argument and Return Type Annotations.
def get_server_status(hostname: str, port: int) -> str:
    print(f"Checking {hostname}:{port}")
    if port == 80:
        return "Online"
    else:
        return "Offline"

"""
try running the func with
- python 12_static_Typing.py - run fine
- python -m mypy 12_static_Typing.py - will give error (Incompatible Type)

We can add mypy in our CI/CD pipelines for more restriction
"""
def process_id(user_id: int) -> None:
    print(f"Process user ID: {user_id} (type: {type(user_id)})")

process_id("web01")