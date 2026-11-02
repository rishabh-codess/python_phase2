# Dataclasses: defaults, ordering, frozen instances, and __post_init__
from dataclasses import dataclass, field, asdict


@dataclass(order=True)
class Student:
    grade: float
    name: str = field(compare=False)
    subjects: list = field(default_factory=list, compare=False)

    def __post_init__(self):
        self.name = self.name.title()


@dataclass(frozen=True)
class Point:
    x: int
    y: int


students = [
    Student(88.5, "alice", ["math", "physics"]),
    Student(92.0, "bob"),
    Student(79.0, "charlie", ["art"]),
]

print(sorted(students))
print(max(students).name)
print(asdict(students[0]))

p = Point(1, 2)
print(p)
try:
    p.x = 10
except Exception as error:
    print(type(error).__name__, "- Point is frozen")
