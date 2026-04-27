# Read a JSON list of users and print only those with expired passwords (30 days more than todays date).

import json
from datetime import date, datetime
path = "Python Scripts/Scripts/JSON_YAML scripts/2_user_pass.json"
expiration_rule = 30

def get_expired_password(path):
    with open(path,"r") as f:
        data = json.load(f)
    
    user_list = []

    for user in data[0]:
        # convert a string like "2024-06-01" to a date use datetime.strptime(value,formate).date()
        expiry_date = datetime.strptime(
            user["password_expires_at"], "%Y-%m-%d"
        ).date()

        if expiry_date < date.today():
            user_list.append(user["username"])

    for user in data[1]:
        set_date = datetime.strptime(
            user["password_set_at"], "%Y-%m-%d"
        ).date()
        today = date.today()

        days_left = (today - set_date).days
        if days_left < expiration_rule:
            print(f"Hi {user["username"]}, your password will expire in {expiration_rule-days_left} days")
        else:
            print(f"Hi {user["username"]},Your password has expired")
            user_list.append(user["username"])

    return user_list

user_list = get_expired_password(path)
print(f"User list with expired passwords are: {user_list}")