Right now you’re only halfway doing secrets management. Using os.getenv() is correct—but without a proper .env workflow, it’s incomplete.



# ✅ What you should actually do (complete setup)

## 1. Create a `.env` file

In your project root:


GITHUB_TOKEN=your_github_token_here
OPENWEATHER_API_KEY=your_weather_key_here


## 2. Install `python-dotenv`


pip install python-dotenv


## 3. Load `.env` in your code

At the **top of your script (important)**:

from dotenv import load_dotenv
load_dotenv()


## 4. Read variables (you already do this part)

import os

token = os.getenv("GITHUB_TOKEN")
api_key = os.getenv("OPENWEATHER_API_KEY")


## 5. Add validation (you are missing this)


if not token or not api_key:
    raise ValueError("Missing API credentials. Check your .env file.")


# 🔐 6. Add `.env` to `.gitignore` (CRITICAL)

Create/edit .gitignore:


.env


## ❗ Why this matters

Without this:

* You WILL accidentally push secrets to GitHub
* Tokens get revoked
* Account can get flagged


# 🧠 What `.env` actually does

It’s just a **local key-value store**.

load_dotenv() loads it into:


os.environ

So:


os.getenv("GITHUB_TOKEN")


works exactly like real environment variables.



# ⚠️ Alternative (Production / Servers)

Instead of .env, real systems use:


export GITHUB_TOKEN=...
export OPENWEATHER_API_KEY=...


or Docker / CI secrets.


# 🔥 Common Mistakes (you were close to these)

### ❌ Hardcoding


token = "abc123"


### ❌ Forgetting `load_dotenv()`

→ os.getenv() returns None

### ❌ Not adding `.env` to `.gitignore`

→ security leak



# ✅ Minimal Final Setup (Clean Version)


from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("GITHUB_TOKEN")
api_key = os.getenv("OPENWEATHER_API_KEY")

if not token or not api_key:
    raise ValueError("Missing API credentials")