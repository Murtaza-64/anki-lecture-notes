import json
from collections import defaultdict
from pathlib import Path

from core.card_text import build_query
from core.index import open_index, search
from core.sync import sync_folder
from label_cards import CARDS_PATH, INDEX_PATH, NOTES_DIR, load_labels

RESULTS_CHECKED = 10


def first_hit_rank(results: list[tuple[str, int]], correct: set[tuple[str, int]]) -> int | None:
    # Position (starting at 1) of the first result that is in correct, or None
    for rank, result in enumerate(results, start=1):
        if result in correct:
            return rank
    return None


def summarise(ranks: list[int | None]) -> dict[str, float]:
    # hit@1, hit@5, hit@10 and MRR for a list of ranks
    found = [rank for rank in ranks if rank is not None]
    return {
        "hit@1": sum(rank <= 1 for rank in found) / len(ranks),
        "hit@5": sum(rank <= 5 for rank in found) / len(ranks),
        "hit@10": sum(rank <= 10 for rank in found) / len(ranks),
        "MRR": sum(1 / rank for rank in found) / len(ranks),
    }


def print_row(name: str, ranks: list[int | None]) -> None:
    scores = "  ".join(f"{metric} {value:.2f}" for metric, value in summarise(ranks).items())
    print(f"{name:48} n={len(ranks):<3} {scores}")


def main() -> None:
    # Open and sync the index; rank every card that has a non-empty label;
    # print the overall results, results per module, and the misses
    with open(CARDS_PATH, encoding="utf-8") as f:
        cards = json.load(f)
    labels = load_labels()

    conn = open_index(str(INDEX_PATH))
    sync_folder(conn, NOTES_DIR)

    ranks_by_deck = defaultdict(list)
    misses = []
    without_page = 0
    with_image = 0
    for card in cards:
        if card["front_has_image"]:
            with_image += 1
            continue

        correct = {tuple(pair) for pair in labels[str(card["note_id"])]}
        if not correct:
            without_page += 1
            continue

        query = build_query(card["front"] + " " + card["back"])
        results = [
            (str(Path(path).relative_to(NOTES_DIR)), page)
            for path, page in search(conn, query, limit=RESULTS_CHECKED)
        ]
        rank = first_hit_rank(results, correct)
        ranks_by_deck[card["deck"]].append(rank)
        if rank is None or rank > 5:
            misses.append((card, correct, results, rank))
    conn.close()

    all_ranks = [rank for ranks in ranks_by_deck.values() for rank in ranks]
    print(
        f"Cards evaluated: {len(all_ranks)} "
        f"(left out: {without_page} without a correct page, {with_image} with an image on the front)\n"
    )
    print_row("All", all_ranks)
    for deck, ranks in ranks_by_deck.items():
        print_row(deck, ranks)

    print(f"\nMisses (no correct page in the top 5): {len(misses)}")
    for card, correct, results, rank in misses:
        top = f"{results[0][0]} p.{results[0][1]}" if results else "no results"
        wanted = ", ".join(f"{file} p.{page}" for file, page in sorted(correct))
        print(f"\n- {card['front'][:90]}")
        print(f"  first correct at: {rank or 'not in top 10'}   search's #1: {top}")
        print(f"  correct: {wanted}")


if __name__ == "__main__":
    main()
