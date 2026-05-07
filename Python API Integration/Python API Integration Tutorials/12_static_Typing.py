"""
 python -m mypy 12_static_Typing.py run this as unable to isntall Pylance.
 if running above command, we get error if we reassing the variable type to a different from mentioned one.

Syntax Below
"""
# Variable Annotation

config_path: str = "/etc/app.conf"
is_enable: bool = True
retry_count: int = 3
identifier: str | int = "abcd-123"
servers: list[str] = ["web1","web2"]
settings: dict[str, int | str] = {
    "port": 8080,
    "user": "myuser"
}

# Optional for values that can be None
from typing import Optional, Any
# give an example using Optional static type

# Type Any
item: Any = 123
# print(item)

def print_anything(item: Any) -> None:
    print(f"Item {item} has type {type(item)}")
# print_anything(123)
# print_anything("123")




# Function Argument and Return Type Annotations.
def get_server_status(hostname: str, port: int) -> str:
    print(f"Checking {hostname}:{port}")
    if port == 80:
        return "Online"
    else:
        return "Offline"
# found = get_server_status("ubuntu",80)
# print(found)

"""
try running the func with
- python 12_static_Typing.py - run fine
- python -m mypy 12_static_Typing.py - will give error (Incompatible Type)

We can add mypy in our CI/CD pipelines for more restriction
"""
def process_id(user_id: int) -> None:
    print(f"Process user ID: {user_id} (type: {type(user_id)})")

# process_id("web01")


# TypeDict
# explain it and why we are using it when we have a static type for dict -> user: dict[str, int | str] = {"id":123,"name":"Alice"}
# They help us specify the specific keys that we want a certain dictionary to contain

from typing import TypedDict, NotRequired

# Inherit the TypedDict like its a Parent class
class User(TypedDict):
    id: int
    name: str
    emai: str
    phone: NotRequired[str] # explain

user: User = {
    "id": 123,
    "name": "Alice",
    "email": "alice@gmail.com",
    "phone": "1311124141"
}


# Typing Classes
class Server:
    def __init__(self,host: str, ip_address: str, os_type: str = "Linux"):
        self.host: str = host
        self.ip_address: str = ip_address
        self.os_type:str = os_type
        self.is_online: bool = False
    
    def connect(self) -> str:
        print(f"Connection to {self.host} with IP_address: {self.ip_address}")
        self.is_online = True
        print(f"{self.host} is Online.")

    def get_status(self) -> str:
        return "Online" if self.is_online else "Offline"

linux = Server("ec2-user","192.168.1.10","ubuntu")
linux.connect()
print(linux.get_status())


# if annotation also a static type, give its example too