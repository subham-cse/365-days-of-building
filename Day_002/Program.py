print("A small program that prints a random motivational message using random module.")

import random

quotes = [
    "Consistency beats motivation.",
    "Small steps every day matter.",
    "Learning compounds over time.",
    "Progress > perfection.",
    "Show up, even on low days."
]

print("Today's Motivation:")
print(random.choice(quotes))
