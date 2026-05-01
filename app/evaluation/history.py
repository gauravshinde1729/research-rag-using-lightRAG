"""Persistence for per-query evaluation scores.

Each call to :func:`save_score` appends one JSON entry to the history file
(default ``eval_history/scores.json``). All public functions accept a
``history_file`` override so tests can point at ``tmp_path`` instead of the
real directory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DEFAULT_HISTORY_FILE = Path("eval_history/scores.json")
METRIC_KEYS = ("faithfulness", "response_relevancy", "context_precision")
_ANSWER_TRUNCATE = 500


def _resolve(history_file: Path | None) -> Path:
    return Path(history_file) if history_file is not None else DEFAULT_HISTORY_FILE


def save_score(
    question: str,
    answer: str,
    scores: dict,
    contexts: list[str] | None = None,
    history_file: Path | None = None,
) -> None:
    path = _resolve(history_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer[:_ANSWER_TRUNCATE],
        "scores": scores,
        "num_contexts": len(contexts) if contexts else 0,
    }

    history = load_history(history_file=path)
    history.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def load_history(history_file: Path | None = None) -> list[dict]:
    path = _resolve(history_file)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return []
    return json.loads(content)


def get_aggregate_scores(history_file: Path | None = None) -> dict:
    history = load_history(history_file=history_file)
    if not history:
        return {}

    aggregates: dict = {}
    for metric in METRIC_KEYS:
        values = [
            entry["scores"].get(metric)
            for entry in history
            if isinstance(entry.get("scores"), dict)
            and entry["scores"].get(metric) is not None
        ]
        if values:
            aggregates[metric] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values),
            }
    return aggregates


def clear_history(history_file: Path | None = None) -> None:
    path = _resolve(history_file)
    if path.exists():
        path.unlink()
