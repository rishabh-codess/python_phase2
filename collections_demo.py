# collections: Counter, defaultdict, deque, namedtuple
from collections import Counter, defaultdict, deque, namedtuple

text = "the quick brown fox jumps over the lazy dog the end"
word_counts = Counter(text.split())
print(word_counts.most_common(2))

groups = defaultdict(list)
for word in text.split():
    groups[len(word)].append(word)
print(dict(groups))

recent = deque(maxlen=3)
for n in range(1, 6):
    recent.append(n)
print(recent)

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p, p.x + p.y)
print(p._replace(x=10))
