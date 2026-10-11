"""Provider-agnostic evaluation harness for Contoso AI Assistant."""

from __future__ import annotations

from aiplatform.eval.dataset import GoldenQA, load_golden_dataset
from aiplatform.eval.metrics import JudgeScore, lexical_f1
from aiplatform.eval.runner import EvaluationRunner
from aiplatform.eval.runner_types import EvalReport

__all__ = [
    "EvalReport",
    "EvaluationRunner",
    "GoldenQA",
    "JudgeScore",
    "lexical_f1",
    "load_golden_dataset",
]
