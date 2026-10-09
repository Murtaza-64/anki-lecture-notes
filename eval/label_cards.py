import json
from pathlib import Path

from core.card_text import build_query
from core.index import open_index
from core.sync import sync_folder

NOTES_DIR = Path.home() / "Documents" / "Revision" / "Misc"
DATA_DIR = Path(__file__).parent / "data"
CARDS_PATH = DATA_DIR / "cards.json"
LABELS_PATH = DATA_DIR / "labels.json"
INDEX_PATH = DATA_DIR / "index.db"
RESULTS_SHOWN = 10
PROMPT = 'Correct numbers (e.g. "1 3", add "m" for pages not listed), "n" if no page covers it, "q" to quit: '


def load_labels() -> dict:
    # The saved labels, or {} if labels.json doesn't exist yet
    if not LABELS_PATH.exists():
        return {}
    with open(LABELS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_labels(labels: dict) -> None:
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2, ensure_ascii=False)


def show_results(conn, query: str) -> list[tuple[str, int]]:
    # Print the top results numbered, with a snippet each; return them as (relative path, page)
    rows = conn.execute(
        """
        SELECT path, page, snippet(pages, 2, '[', ']', '…', 16) FROM pages
        WHERE pages MATCH ?
        ORDER BY bm25(pages)
        LIMIT ?
        """,
        (query, RESULTS_SHOWN),
    ).fetchall()

    results = []
    for number, (path, page, snippet) in enumerate(rows, start=1):
        relative = str(Path(path).relative_to(NOTES_DIR))
        print(f"{number:2}. {relative}  p.{page}  {' '.join(snippet.split())}")
        results.append((relative, page))
    return results


def ask_manual() -> list:
    # Pages typed in by hand, for correct pages the search didn't list
    label = []
    while True:
        file = input("  File (empty to finish): ").strip()
        if not file:
            return label
        if not (NOTES_DIR / file).exists():
            print(f"  No file called {file!r} in {NOTES_DIR.name}.")
            continue
        page = input("  Page: ").strip()
        if not page.isdigit():
            print("  The page must be a number.")
            continue
        label.append([file, int(page)])


def ask_label(results: list[tuple[str, int]]) -> list | None:
    # Read the user's answer and return the label, or None if they typed "q"
    while True:
        answer = input(PROMPT).split()
        if answer == ["q"]:
            return None
        if answer == ["n"]:
            return []

        label = []
        valid = bool(answer)
        for token in answer:
            if token == "m":
                continue
            if token.isdigit() and 1 <= int(token) <= len(results):
                label.append(list(results[int(token) - 1]))
            else:
                valid = False
        if not valid:
            print(f"Type result numbers 1-{len(results)}, m, n or q.")
            continue

        if "m" in answer:
            label += ask_manual()
        if label:
            return label
        print('No pages given. Type "n" if no page covers this card.')


def main() -> None:
    # Open and sync the index, then label each card not yet in labels.json,
    # saving after every card
    with open(CARDS_PATH, encoding="utf-8") as f:
        cards = json.load(f)
    labels = load_labels()

    conn = open_index(str(INDEX_PATH))
    sync_folder(conn, NOTES_DIR)

    for number, card in enumerate(cards, start=1):
        key = str(card["note_id"])
        if key in labels:
            continue

        print(f"\n[{number}/{len(cards)}] {card['deck']}")
        print(f"FRONT: {card['front']}")
        print(f"BACK:  {card['back']}\n")
        results = show_results(conn, build_query(card["front"] + " " + card["back"]))

        label = ask_label(results)
        if label is None:
            break
        labels[key] = label
        save_labels(labels)

    conn.close()
    print(f"\n{len(labels)}/{len(cards)} cards labelled.")


if __name__ == "__main__":
    main()
