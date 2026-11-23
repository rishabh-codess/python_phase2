"""Dates, time deltas and random utilities."""

import random
import secrets
from datetime import date, datetime, timedelta

today = date.today()
print("Today:", today.isoformat())
print("In 30 days:", today + timedelta(days=30))

birthday = date(2000, 1, 1)
print("Days since 2000-01-01:", (today - birthday).days)

now = datetime.now()
print("Formatted:", now.strftime("%A, %d %B %Y %H:%M"))
print("Parsed:", datetime.strptime("2024-03-15 14:30", "%Y-%m-%d %H:%M"))

random.seed(42)  # reproducible output
print("Random int:", random.randint(1, 100))
print("Choice:", random.choice(["red", "green", "blue"]))
deck = list(range(1, 6))
random.shuffle(deck)
print("Shuffled:", deck)
print("Secure token:", secrets.token_hex(8))
