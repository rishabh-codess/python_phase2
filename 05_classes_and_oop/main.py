"""Classes, inheritance and dataclasses."""

from dataclasses import dataclass


class Animal:
    def __init__(self, name: str) -> None:
        self.name = name

    def speak(self) -> str:
        return f"{self.name} makes a sound"


class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"


class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says Meow!"


@dataclass
class Point:
    x: float
    y: float

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


if __name__ == "__main__":
    for animal in (Animal("Generic"), Dog("Rex"), Cat("Tom")):
        print(animal.speak())

    p1, p2 = Point(0, 0), Point(3, 4)
    print(p1, p2)
    print("Distance:", p1.distance_to(p2))
