# Regular expressions: search, findall, named groups, and sub
import re

text = "Contact: alice@example.com, bob.smith@work.org | Phone: 555-123-4567 on 2024-03-15"

emails = re.findall(r"[\w.]+@[\w.]+\.\w+", text)
print("Emails:", emails)

phone = re.search(r"(\d{3})-(\d{3})-(\d{4})", text)
print("Phone groups:", phone.groups())

date = re.search(r"(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})", text)
print("Date:", date.group("day"), date.group("month"), date.group("year"))

masked = re.sub(r"\d{3}-\d{3}-(\d{4})", r"***-***-\1", text)
print(masked)

pattern = re.compile(r"^[A-Z][a-z]+$")
print([w for w in ["Hello", "world", "Python", "PYTHON"] if pattern.match(w)])
