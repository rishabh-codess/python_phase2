# File handling with JSON: write, read, update, and clean up
import json
import tempfile
from pathlib import Path

data = {
    "users": [
        {"name": "Alice", "age": 30, "skills": ["python", "sql"]},
        {"name": "Bob", "age": 25, "skills": ["java"]},
    ]
}

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "users.json"

    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print("Saved to", path.name)

    with path.open(encoding="utf-8") as file:
        loaded = json.load(file)

    loaded["users"].append({"name": "Carol", "age": 35, "skills": []})
    path.write_text(json.dumps(loaded, indent=2), encoding="utf-8")

    reloaded = json.loads(path.read_text(encoding="utf-8"))
    for user in reloaded["users"]:
        print(f"{user['name']} ({user['age']}): {', '.join(user['skills']) or 'no skills'}")
