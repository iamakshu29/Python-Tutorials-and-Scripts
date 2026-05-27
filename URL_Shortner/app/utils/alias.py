import hashlib
import string
import random
from datetime import datetime, timedelta

def generate_short_code(length=7):
    chars = string.ascii_letters + string.digits  # a-z, A-Z, 0-9
    return ''.join(random.choices(chars, k=length))