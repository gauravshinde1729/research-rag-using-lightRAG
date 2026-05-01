"""Tests for app.evaluation.history. All tests use tmp_path — never the real eval_history/."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.history import (
    clear_history,
    get_aggregate_scores,
    load_history,
    save_score,
)


def test_save_and_load_single(tmp_path: Path) -> None:
    history_file = tmp_path / "scores.json"

    save_score(
        question="What is RAG?",
        answer="Retrieval-Augmented Generation.",
        scores={"faithfulness": 0.9, "response_relevancy": 0.8, "context_precision": 0.7},
        contexts=["context one", "context two"],
        history_file=history_file,
    )

    history = load_history(history_file=history_file)
    assert len(history) == 1
    entry = history[0]
    assert entry["question"] == "What is RAG?"
    assert entry["answer"] == "Retrieval-Augmented Generation."
    assert entry["scores"]["faithfulness"] == 0.9
    assert entry["num_contexts"] == 2
    assert "timestamp" in entry


def test_save_multiple_and_load(tmp_path: Path) -> None:
    history_file = tmp_path / "scores.json"

    for i in range(3):
        save_score(
            question=f"Q{i}",
            answer=f"A{i}",
            scores={"faithfulness": 0.5 + i * 0.1},
            contexts=[f"ctx{i}"],
            history_file=history_file,
        )

    history = load_history(history_file=history_file)
    assert len(history) == 3
    assert [e["question"] for e in history] == ["Q0", "Q1", "Q2"]


def test_aggregate_scores(tmp_path: Path) -> None:
    history_file = tmp_path / "scores.json"

    triples = [
        {"faithfulness": 0.6, "response_relevancy": 0.7, "context_precision": 0.5},
        {"faithfulness": 0.8, "response_relevancy": 0.9, "context_precision": 0.6},
        {"faithfulness": 1.0, "response_relevancy": 0.8, "context_precision": 0.7},
    ]
    for i, scores in enumerate(triples):
        save_score(
            question=f"Q{i}",
            answer=f"A{i}",
            scores=scores,
            contexts=[],
            history_file=history_file,
        )

    aggregates = get_aggregate_scores(history_file=history_file)

    assert aggregates["faithfulness"]["count"] == 3
    assert aggregates["faithfulness"]["min"] == 0.6
    assert aggregates["faithfulness"]["max"] == 1.0
    assert abs(aggregates["faithfulness"]["mean"] - (0.6 + 0.8 + 1.0) / 3) < 1e-9

    assert aggregates["response_relevancy"]["min"] == 0.7
    assert aggregates["response_relevancy"]["max"] == 0.9
    assert abs(aggregates["response_relevancy"]["mean"] - (0.7 + 0.9 + 0.8) / 3) < 1e-9

    assert aggregates["context_precision"]["min"] == 0.5
    assert aggregates["context_precision"]["max"] == 0.7


def test_aggregate_skips_none(tmp_path: Path) -> None:
    history_file = tmp_path / "scores.json"

    save_score(
        question="Q1",
        answer="A1",
        scores={"faithfulness": 0.8, "response_relevancy": None, "context_precision": 0.5},
        contexts=[],
        history_file=history_file,
    )
    save_score(
        question="Q2",
        answer="A2",
        scores={"faithfulness": None, "response_relevancy": 0.9, "context_precision": 0.7},
        contexts=[],
        history_file=history_file,
    )
    save_score(
        question="Q3",
        answer="A3",
        scores={"faithfulness": 0.6, "response_relevancy": 0.7, "context_precision": None},
        contexts=[],
        history_file=history_file,
    )

    aggregates = get_aggregate_scores(history_file=history_file)

    assert aggregates["faithfulness"]["count"] == 2
    assert abs(aggregates["faithfulness"]["mean"] - (0.8 + 0.6) / 2) < 1e-9

    assert aggregates["response_relevancy"]["count"] == 2
    assert abs(aggregates["response_relevancy"]["mean"] - (0.9 + 0.7) / 2) < 1e-9

    assert aggregates["context_precision"]["count"] == 2
    assert abs(aggregates["context_precision"]["mean"] - (0.5 + 0.7) / 2) < 1e-9


def test_load_empty(tmp_path: Path) -> None:
    history_file = tmp_path / "does_not_exist.json"
    assert load_history(history_file=history_file) == []
    assert get_aggregate_scores(history_file=history_file) == {}


def test_clear_history(tmp_path: Path) -> None:
    history_file = tmp_path / "scores.json"

    save_score(
        question="Q1",
        answer="A1",
        scores={"faithfulness": 0.9},
        contexts=[],
        history_file=history_file,
    )
    assert history_file.exists()

    clear_history(history_file=history_file)

    assert not history_file.exists()
    assert load_history(history_file=history_file) == []

    # clear on a nonexistent file should be a no-op, not raise
    clear_history(history_file=history_file)
