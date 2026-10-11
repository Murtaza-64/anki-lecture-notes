import json
import random
from pathlib import Path

from anki.collection import Collection

from core.card_text import clean_card_text

DATA_DIR = Path(__file__).parent / "data"
COLLECTION_PATH = DATA_DIR / "collection.anki2"
OUTPUT_PATH = DATA_DIR / "cards.json"

DECKS = [
    "40007 - Introduction to Databases",
    "40005 - Introduction to Computer Architecture",
    "40018 - Discrete Mathematics, Logic & Reasoning",
    "40016 - Calculus",
]
CARDS_PER_DECK = 15
MIN_FRONT_WORDS = 3
SEED = 2026


def main() -> None:
    rng = random.Random(SEED)
    col = Collection(str(COLLECTION_PATH))
    cards = []
    try:
        for deck in DECKS:
            eligible = []
            for note_id in sorted(col.find_notes(f'deck:"COMP::{deck}"')):
                note = col.get_note(note_id)
                front = clean_card_text(note["Front"])
                if len(front.split()) >= MIN_FRONT_WORDS:
                    back = clean_card_text(note["Back"])
                    eligible.append({
                        "note_id": note_id,
                        "deck": deck,
                        "front": front,
                        "back": back,
                        "front_has_image": "<img" in note["Front"],
                    })
            cards += rng.sample(eligible, CARDS_PER_DECK)
    finally:
        col.close()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(cards, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(cards)} cards to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
