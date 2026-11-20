"""Reading and writing text and JSON files using pathlib."""

import json
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    folder = Path(tmp)

    # Text file
    text_file = folder / "notes.txt"
    text_file.write_text("line one\nline two\nline three\n", encoding="utf-8")
    with text_file.open(encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            print(f"{number}: {line.rstrip()}")

    # JSON file
    json_file = folder / "data.json"
    data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]}
    json_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    loaded = json.loads(json_file.read_text(encoding="utf-8"))
    print("Loaded names:", [u["name"] for u in loaded["users"]])
