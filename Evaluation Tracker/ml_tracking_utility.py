"""Metric-only version tracking for machine-learning runs."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
from typing import Mapping, Optional, Sequence, TypedDict, cast


# Typed records define the public input and JSON output contracts.
class Metrics(TypedDict):
    """The three metrics tracked by the utility."""

    rmse: float
    r2: float
    mae: float


class Weights(TypedDict):
    """Weights for the normalized metric components."""

    rmse: float
    r2: float
    mae: float


class SavedRun(TypedDict):
    project_name: str
    version: int
    timestamp: str
    current_metrics: Metrics
    current_overall_score: float
    metric_changes: list[str]
    previous_iteration_comparison: str
    historical_best: str
    scoring_weights: Weights


class TrackRunResult(TypedDict):
    saved: bool
    version: Optional[int]
    path: Optional[str]
    reason: Optional[str]
    current_metrics: Metrics
    current_overall_score: float
    metric_changes: list[str]
    previous_iteration_comparison: str
    historical_best: str


DEFAULT_WEIGHTS: Weights = {"rmse": 0.60, "r2": 0.25, "mae": 0.15}
_METRIC_NAMES = frozenset(DEFAULT_WEIGHTS)


# Input validation keeps invalid metrics and weights out of saved history.
def _validate_metrics(metrics: Mapping[str, float]) -> Metrics:
    if set(metrics) != _METRIC_NAMES:
        raise ValueError("current_metrics must contain exactly rmse, r2, and mae")

    validated: Metrics = {
        "rmse": metrics["rmse"],
        "r2": metrics["r2"],
        "mae": metrics["mae"],
    }
    for name, value in validated.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a real number")
        if not math.isfinite(float(value)):
            raise ValueError(f"{name} must be finite")
        if name in {"rmse", "mae"} and value < 0:
            raise ValueError(f"{name} cannot be negative")
        validated[name] = float(value)
    return validated


def _normalise_weights(weights: Mapping[str, float] | None) -> Weights:
    supplied = DEFAULT_WEIGHTS if weights is None else weights
    if set(supplied) != _METRIC_NAMES:
        raise ValueError("scoring_weights must contain exactly rmse, r2, and mae")

    values = {name: float(supplied[name]) for name in _METRIC_NAMES}
    if any(not math.isfinite(value) or value < 0 for value in values.values()):
        raise ValueError("scoring weights must be finite and non-negative")
    total = sum(values.values())
    if total <= 0:
        raise ValueError("scoring weights must have a positive total")
    return {
        "rmse": values["rmse"] / total,
        "r2": values["r2"] / total,
        "mae": values["mae"] / total,
    }


def _round_to_significant_figures(value: float, significant_figures: int) -> float:
    """Round a finite number to the requested number of significant figures."""
    if value == 0:
        return 0.0
    decimal_places = significant_figures - 1 - math.floor(math.log10(abs(value)))
    return round(value, decimal_places)


# Scoring normalizes metric direction and combines the three weighted components.
def calculate_overall_score(
    rmse: float,
    r2: float,
    mae: float,
    weights: Mapping[str, float] | None = None,
) -> float:
    """Return a higher-is-better score from the three evaluation metrics.

    RMSE and MAE are inverted because lower errors are better. R2 is shifted
    into a bounded higher-is-better range before applying the weights.
    """
    metrics = _validate_metrics({"rmse": rmse, "r2": r2, "mae": mae})
    effective_weights = _normalise_weights(weights)
    rmse_component = 1.0 / (1.0 + metrics["rmse"])
    mae_component = 1.0 / (1.0 + metrics["mae"])
    r2_component = min(1.0, max(0.0, (metrics["r2"] + 1.0) / 2.0))
    score = (
        effective_weights["rmse"] * rmse_component
        + effective_weights["r2"] * r2_component
        + effective_weights["mae"] * mae_component
    )
    return _round_to_significant_figures(score, 5)


# Metric comparison produces the human-readable strings required by v3.
def _format_metric_change(name: str, previous: float, current: float) -> str:
    delta = current - previous
    return (
        f"Previous {name}: [{previous:.5f}], Current {name}: [{current:.5f}], "
        f"{name} changed by: [{delta:.5f}]"
    )


def compare_metrics(
    previous_metrics: Metrics | None,
    current_metrics: Metrics,
) -> list[str]:
    """Return one formatted change string for each metric after the first run."""
    if previous_metrics is None:
        return []
    return [
        _format_metric_change(name, previous_metrics[name], current_metrics[name])
        for name in ("rmse", "r2", "mae")
    ]


def metrics_changed(previous_metrics: Metrics | None, current_metrics: Metrics) -> bool:
    """Return whether any metric differs exactly from the previous run."""
    if previous_metrics is None:
        return True
    return any(
        current_metrics[name] != previous_metrics[name]
        for name in ("rmse", "r2", "mae")
    )


# Version discovery reads only valid v3 JSON files and preserves numeric ordering.
def _version_pattern(project_name: str) -> re.Pattern[str]:
    return re.compile(rf"^{re.escape(project_name)}_v(\d+)\.json$")


def _is_saved_run(
    value: object,
    expected_version: int,
    expected_project_name: str,
) -> bool:
    if not isinstance(value, dict):
        return False
    metrics = value.get("current_metrics")
    weights = value.get("scoring_weights")
    score = value.get("current_overall_score")
    return (
        value.get("project_name") == expected_project_name
        and value.get("version") == expected_version
        and isinstance(value.get("timestamp"), str)
        and isinstance(metrics, dict)
        and set(metrics) == _METRIC_NAMES
        and all(
            isinstance(metric, (int, float))
            and not isinstance(metric, bool)
            and math.isfinite(float(metric))
            for metric in metrics.values()
        )
        and float(metrics["rmse"]) >= 0
        and float(metrics["mae"]) >= 0
        and isinstance(score, (int, float))
        and not isinstance(score, bool)
        and math.isfinite(float(score))
        and isinstance(value.get("metric_changes"), list)
        and all(isinstance(change, str) for change in value["metric_changes"])
        and isinstance(value.get("previous_iteration_comparison"), str)
        and isinstance(value.get("historical_best"), str)
        and isinstance(weights, dict)
        and set(weights) == _METRIC_NAMES
        and all(
            isinstance(weight, (int, float))
            and not isinstance(weight, bool)
            and math.isfinite(float(weight))
            and float(weight) >= 0
            for weight in weights.values()
        )
    )


def find_version_files(output_dir: Path, project_name: str) -> dict[int, Path]:
    """Find valid v3 JSON files for a project, keyed by numeric version."""
    if not output_dir.exists():
        return {}
    versions: dict[int, Path] = {}
    pattern = _version_pattern(project_name)
    for path in output_dir.iterdir():
        match = pattern.fullmatch(path.name)
        if match is None or not path.is_file():
            continue
        version = int(match.group(1))
        try:
            with path.open("r", encoding="utf-8") as stream:
                payload: object = json.load(stream)
        except (OSError, json.JSONDecodeError):
            continue
        if _is_saved_run(payload, version, project_name):
            versions[version] = path
    return versions


def _find_existing_version_numbers(output_dir: Path, project_name: str) -> set[int]:
    """Find every matching filename so invalid files are never overwritten."""
    if not output_dir.exists():
        return set()
    pattern = _version_pattern(project_name)
    return {
        int(match.group(1))
        for path in output_dir.iterdir()
        if path.is_file()
        for match in [pattern.fullmatch(path.name)]
        if match is not None
    }


def get_next_version(version_files: Mapping[int, Path]) -> int:
    """Return the next numeric version without relying on filename order."""
    return max(version_files, default=0) + 1


# Loading helpers separate previous-iteration data from historical-best data.
def _load_saved_run(path: Path) -> SavedRun | None:
    try:
        with path.open("r", encoding="utf-8") as stream:
            value: object = json.load(stream)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(value, dict):
        return None
    version = value.get("version")
    project_name = value.get("project_name")
    if not isinstance(version, int) or not isinstance(project_name, str):
        return None
    if not _is_saved_run(value, version, project_name):
        return None
    return cast(SavedRun, value)


def _previous_metrics(payload: SavedRun | None) -> Metrics | None:
    return None if payload is None else payload["current_metrics"]


def _previous_version(payload: SavedRun | None) -> int | None:
    return None if payload is None else payload["version"]


def _previous_score(payload: SavedRun | None) -> float | None:
    return None if payload is None else payload["current_overall_score"]


# Historical-best selection scans every valid saved version.
def _find_historical_best(
    version_files: Mapping[int, Path],
) -> tuple[int, float] | None:
    candidates: list[tuple[int, float]] = []
    for version, path in version_files.items():
        payload = _load_saved_run(path)
        if payload is not None:
            candidates.append((version, payload["current_overall_score"]))
    if not candidates:
        return None
    return min(candidates, key=lambda item: (-item[1], item[0]))


# Narrative builders keep console output and saved summaries readable.
def build_previous_iteration_comparison(
    previous_version: int | None,
    previous_score: float | None,
    current_score: float,
    metric_changes: Sequence[str],
) -> str:
    """Create the human-readable previous-iteration comparison."""
    if previous_version is None or previous_score is None:
        return (
            "Previous iteration comparison:\n"
            f"No previous saved iteration exists. Current run score: {current_score}."
        )
    changes_text = "\n".join(metric_changes)
    return (
        "Previous iteration comparison:\n"
        f"Compared to previous version {previous_version} (Score: {previous_score}), "
        f"the current run scored {current_score}.\n\n"
        f"Metric changes:\n{changes_text}"
    )


def build_historical_best_summary(
    candidate_version: int,
    candidate_score: float,
    historical_best: tuple[int, float] | None,
) -> str:
    """Create the human-readable historical-best comparison."""
    if historical_best is None:
        return (
            "Historical best:\n"
            f"The current version (v{candidate_version}, Score: {candidate_score}) "
            "is the initial historical best."
        )
    best_version, best_score = historical_best
    if candidate_score > best_score:
        return (
            "Historical best:\n"
            f"The current version is the new historical best, beating version "
            f"{best_version}'s score of {best_score}!"
        )
    return (
        "Historical best:\n"
        f"The historical best remains version {best_version} with an overall score "
        f"of {best_score}.\nThe current version (v{candidate_version}, Score: "
        f"{candidate_score}) did not beat the historical best."
    )


def format_track_run_result(result: TrackRunResult) -> str:
    """Format a tracking result as a readable multi-line console summary."""
    lines = [
        "Tracking result:",
        f"  saved: {result['saved']}",
        f"  version: {result['version']}",
        f"  path: {result['path']}",
        f"  reason: {result['reason']}",
        "  current_metrics:",
        f"    rmse: {result['current_metrics']['rmse']:.5f}",
        f"    r2: {result['current_metrics']['r2']:.5f}",
        f"    mae: {result['current_metrics']['mae']:.5f}",
        f"  current_overall_score: {result['current_overall_score']:.5f}",
        "  metric_changes:",
    ]
    if result["metric_changes"]:
        lines.extend(f"    - {change}" for change in result["metric_changes"])
    else:
        lines.append("    - None")
    return "\n".join(lines)


# Exclusive writes prevent an existing version file from being overwritten.
def _write_exclusively(
    output_dir: Path,
    project_name: str,
    payload: SavedRun,
    starting_version: int,
) -> tuple[int, Path]:
    version = starting_version
    while True:
        path = output_dir / f"{project_name}_v{version}.json"
        payload["version"] = version
        try:
            with path.open("x", encoding="utf-8") as stream:
                json.dump(payload, stream, indent=4)
                stream.write("\n")
            return version, path
        except FileExistsError:
            version += 1


# Main workflow: validate, compare, print summaries, and optionally save a run.
def track_run(
    project_name: str,
    current_metrics: Mapping[str, float],
    output_dir: str | Path = ".",
    scoring_weights: Mapping[str, float] | None = None,
) -> TrackRunResult:
    """Compare, optionally save, and print the result of one metric run."""
    if not project_name:
        raise ValueError("project_name cannot be empty")
    metrics = _validate_metrics(current_metrics)
    weights = _normalise_weights(scoring_weights)
    current_score = calculate_overall_score(
        metrics["rmse"], metrics["r2"], metrics["mae"], weights
    )

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    version_files = find_version_files(destination, project_name)
    existing_version_numbers = _find_existing_version_numbers(destination, project_name)
    previous_version = max(version_files, default=None)
    previous_payload = (
        None if previous_version is None else _load_saved_run(version_files[previous_version])
    )
    previous_metrics = _previous_metrics(previous_payload)
    metric_changes = compare_metrics(previous_metrics, metrics)
    next_version = max(existing_version_numbers, default=0) + 1
    previous_comparison = build_previous_iteration_comparison(
        _previous_version(previous_payload),
        _previous_score(previous_payload),
        current_score,
        metric_changes,
    )
    historical_best = _find_historical_best(version_files)
    historical_summary = build_historical_best_summary(
        next_version, current_score, historical_best
    )

    print(previous_comparison)
    print()
    print(historical_summary)

    should_save = previous_payload is None or metrics_changed(previous_metrics, metrics)
    if not should_save:
        return {
            "saved": False,
            "version": None,
            "path": None,
            "reason": "No evaluation metrics changed.",
            "current_metrics": metrics,
            "current_overall_score": current_score,
            "metric_changes": metric_changes,
            "previous_iteration_comparison": previous_comparison,
            "historical_best": historical_summary,
        }

    payload: SavedRun = {
        "project_name": project_name,
        "version": next_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_metrics": metrics,
        "current_overall_score": current_score,
        "metric_changes": metric_changes,
        "previous_iteration_comparison": previous_comparison,
        "historical_best": historical_summary,
        "scoring_weights": weights,
    }
    version, path = _write_exclusively(
        destination, project_name, payload, next_version
    )
    return {
        "saved": True,
        "version": version,
        "path": str(path),
        "reason": None,
        "current_metrics": metrics,
        "current_overall_score": current_score,
        "metric_changes": metric_changes,
        "previous_iteration_comparison": previous_comparison,
        "historical_best": historical_summary,
    }


__all__ = [
    "DEFAULT_WEIGHTS",
    "Metrics",
    "SavedRun",
    "TrackRunResult",
    "Weights",
    "build_historical_best_summary",
    "build_previous_iteration_comparison",
    "calculate_overall_score",
    "compare_metrics",
    "find_version_files",
    "format_track_run_result",
    "get_next_version",
    "metrics_changed",
    "track_run",
]
