# itertools: combinations, permutations, groupby, chain, and accumulate
from itertools import accumulate, chain, combinations, groupby, permutations

print(list(combinations("ABC", 2)))
print(list(permutations([1, 2, 3], 2)))

print(list(chain([1, 2], (3, 4), "56")))
print(list(accumulate([1, 2, 3, 4, 5])))

people = [("Math", "Alice"), ("Math", "Bob"), ("Art", "Carol"), ("Art", "Dave"), ("Music", "Eve")]
for subject, group in groupby(sorted(people), key=lambda item: item[0]):
    print(subject, [name for _, name in group])
