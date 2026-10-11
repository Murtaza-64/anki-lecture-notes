# Search evaluation results

Run with `PYTHONPATH=lecture_notes .venv/bin/python eval/evaluate.py`. Cards: 60 sampled with `eval/export_cards.py`
(15 each from Databases, Computer Architecture, Discrete Maths/Logic/Reasoning, Calculus), labelled with
`eval/label_cards.py`. Index: `~/Documents/Revision/Misc`.

| Change | n | hit@1 | hit@5 | hit@10 | MRR |
|---|---|---|---|---|---|
| Baseline (BM25, front + back) | 55 | 0.51 | 0.75 | 0.80 | 0.60 |
| Leave out cards with an image on the front | 51 | 0.53 | 0.78 | 0.82 | 0.62 |
| Index notes only (no exercises, quizzes, exam papers or duplicates) | 51 | 0.51 | 0.78 | 0.86 | 0.62 |
| Stemming (porter tokenizer) | 51 | 0.57 | 0.82 | 0.88 | 0.67 |

The second row changes which cards are measured, not the search, so only rows from there on are comparable
with each other.
