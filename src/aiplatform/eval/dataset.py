"""Golden evaluation dataset loading."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

DEFAULT_GOLDEN_DATASET = Path("labs") / "data" / "eval" / "golden_qa.jsonl"


class GoldenQA(BaseModel):
    """A single golden question-answer record."""

    question: str = Field(min_length=1)
    expected_answer: str = Field(min_length=1)
    context_source: str = Field(min_length=1)


def load_golden_dataset(path: Path = DEFAULT_GOLDEN_DATASET) -> list[GoldenQA]:
    """Load JSONL golden question-answer records.

    Args:
        path: JSONL path containing question, expected_answer, and context_source.

    Returns:
        Validated dataset records in file order.

    Raises:
        FileNotFoundError: If the dataset path does not exist.
        ValueError: If a line is invalid JSON or fails schema validation.
    """
    records: list[GoldenQA] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
                records.append(GoldenQA.model_validate(payload))
            except (json.JSONDecodeError, ValidationError) as exc:
                message = f"Invalid golden dataset record at {path}:{line_number}"
                raise ValueError(message) from exc
    return records
