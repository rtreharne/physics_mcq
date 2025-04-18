import random

ADJECTIVES = [
    "brave", "curious", "calm", "eager", "bold", "happy", "gentle", "silly", "clever", "graceful",
    "zany", "mighty", "tiny", "swift", "wise", "noisy", "quiet", "bright", "sharp", "smooth",
    "shy", "funny", "sneaky", "loyal", "playful", "quirky", "wild", "dreamy", "jolly", "witty",
    "tidy", "messy", "lively", "spooky", "lazy", "cheery", "fancy", "neat", "nifty", "snappy",
    "gentle", "bashful", "glowing", "sticky", "grumpy", "snoozy", "speedy", "soft", "rugged", "rowdy",
    "crafty", "jazzy", "breezy", "zesty", "moody", "cozy", "fierce", "smiley", "dizzy", "weird",
    "goofy", "cranky", "bouncy", "fluffy", "giddy", "hungry", "jumpy", "keen", "lucky", "nutty",
    "quirky", "rusty", "sassy", "spunky", "twinkly", "zippy", "chirpy", "peppy", "plucky", "snazzy",
    "shiny", "stormy", "sunny", "cloudy", "icy", "fiery", "thrifty", "whimsical", "perky", "zesty",
    "mellow", "fuzzy", "pointy", "edgy", "soggy", "bubbly", "glossy", "snappy", "tidy", "vivid"
]

COLOURS = [
    "red", "orange", "yellow", "green", "blue", "indigo", "violet", "pink", "brown", "black",
    "white", "grey", "silver", "gold", "crimson", "teal", "turquoise", "maroon", "lime", "navy",
    "coral", "peach", "ivory", "magenta", "cyan"
]

ANIMALS = [
    "fox", "tiger", "lion", "bear", "wolf", "panther", "leopard", "cheetah", "zebra", "giraffe",
    "elephant", "rhino", "hippo", "panda", "koala", "kangaroo", "monkey", "gorilla", "chimp", "sloth",
    "otter", "badger", "rabbit", "deer", "squirrel", "moose", "raccoon", "hedgehog", "penguin", "owl",
    "eagle", "falcon", "parrot", "dolphin", "whale", "shark", "octopus", "crab", "lobster", "seal"
]

def generate_anonymous_username():
    return f"{random.choice(ADJECTIVES)}-{random.choice(COLOURS)}-{random.choice(ANIMALS)}"
