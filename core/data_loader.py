import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_json(filename):
    with open(DATA_DIR / filename) as f:
        return json.load(f)

RECIPES = load_json("recipes.json")
FEED_MAP = load_json("feed_map.json")