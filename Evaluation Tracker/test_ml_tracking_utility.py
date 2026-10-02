"""Focused tests for the v3 metric-only tracking utility."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from ml_tracking_utility import (
    calculate_overall_score,
    compare_metrics,
    find_version_files,
    format_track_run_result,
    track_run,
)


class TrackingUtilityV3Tests(unittest.TestCase):
    @staticmethod
    def metrics(rmse: float, r2: float, mae: float) -> dict[str, float]:
        return {"rmse": rmse, "r2": r2, "mae": mae}

    def test_first_run_saves_v1_with_v3_schema(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                result = track_run(
                    "Demo", self.metrics(0.5, 0.9, 0.4), directory
                )

            self.assertTrue(result["saved"])
            self.assertEqual(result["version"], 1)
            self.assertEqual(result["metric_changes"], [])
            self.assertIn("initial historical best", output.getvalue())

            payload = json.loads(Path(result["path"] or "").read_text())
            self.assertEqual(
                set(payload),
                {
                    "project_name",
                    "version",
                    "timestamp",
                    "current_metrics",
                    "current_overall_score",
                    "metric_changes",
                    "previous_iteration_comparison",
                    "historical_best",
                    "scoring_weights",
                },
            )
            self.assertNotIn("loc", payload)
            self.assertNotIn("syntax_hash", payload)

    def test_unchanged_metrics_do_not_save_or_consume_version(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            metrics = self.metrics(0.5, 0.9, 0.4)
            track_run("Demo", metrics, directory)
            output = io.StringIO()
            with redirect_stdout(output):
                result = track_run("Demo", metrics, directory)

            self.assertFalse(result["saved"])
            self.assertIsNone(result["version"])
            self.assertEqual(result["reason"], "No evaluation metrics changed.")
            self.assertEqual(len(list(Path(directory).glob("Demo_v*.json"))), 1)
            self.assertIn("Compared to previous version 1", output.getvalue())

    def test_any_metric_change_saves_and_formats_all_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            track_run("Demo", self.metrics(0.5, 0.9, 0.4), directory)
            result = track_run("Demo", self.metrics(0.6, 0.9, 0.4), directory)

            self.assertTrue(result["saved"])
            self.assertEqual(result["version"], 2)
            self.assertEqual(
                result["metric_changes"],
                [
                    "Previous rmse: [0.50000], Current rmse: [0.60000], rmse changed by: [0.10000]",
                    "Previous r2: [0.90000], Current r2: [0.90000], r2 changed by: [0.00000]",
                    "Previous mae: [0.40000], Current mae: [0.40000], mae changed by: [0.00000]",
                ],
            )

    def test_compare_metrics_returns_all_three_strings(self) -> None:
        previous = self.metrics(0.5, 0.9, 0.4)
        current = self.metrics(0.5, 0.91, 0.3)
        changes = compare_metrics(previous, current)
        self.assertEqual(len(changes), 3)
        self.assertIn("Previous rmse: [0.50000]", changes[0])
        self.assertIn("r2 changed by:", changes[1])
        self.assertIn("mae changed by:", changes[2])

    def test_previous_and_historical_narratives_are_separate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            track_run("Demo", self.metrics(0.5, 0.9, 0.4), directory)
            track_run("Demo", self.metrics(0.8, 0.7, 0.7), directory)
            result = track_run("Demo", self.metrics(0.9, 0.6, 0.8), directory)

            self.assertTrue(result["saved"])
            self.assertIn("previous version 2", result["previous_iteration_comparison"])
            self.assertIn("historical best remains version 1", result["historical_best"])

    def test_historical_best_can_become_current(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            track_run("Demo", self.metrics(0.9, 0.5, 0.8), directory)
            result = track_run("Demo", self.metrics(0.4, 0.95, 0.3), directory)
            self.assertIn("new historical best", result["historical_best"])

    def test_numeric_version_order_and_invalid_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for version in (1, 2, 10):
                payload = {
                    "project_name": "Demo",
                    "version": version,
                    "timestamp": "2026-10-02T00:00:00+00:00",
                    "current_metrics": self.metrics(0.5, 0.9, 0.4),
                    "current_overall_score": 0.8,
                    "metric_changes": [],
                    "previous_iteration_comparison": "none",
                    "historical_best": "best",
                    "scoring_weights": {"rmse": 0.6, "r2": 0.25, "mae": 0.15},
                }
                (path / f"Demo_v{version}.json").write_text(json.dumps(payload))
            (path / "Demo_v99.json").write_text("not json")
            (path / "Demo_v100.json").write_text(json.dumps({"version": 100}))
            files = find_version_files(path, "Demo")
            self.assertEqual(sorted(files), [1, 2, 10])

    def test_invalid_matching_file_is_reserved_but_not_used_as_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Demo_v1.json"
            path.write_text(json.dumps({"old_schema": True}))

            result = track_run("Demo", self.metrics(0.5, 0.9, 0.4), directory)

            self.assertTrue(result["saved"])
            self.assertEqual(result["version"], 2)
            self.assertIn("v2", result["historical_best"])

    def test_score_improves_in_each_metric_direction(self) -> None:
        baseline = calculate_overall_score(0.5, 0.5, 0.5)
        self.assertGreater(calculate_overall_score(0.4, 0.5, 0.5), baseline)
        self.assertGreater(calculate_overall_score(0.5, 0.6, 0.5), baseline)
        self.assertGreater(calculate_overall_score(0.5, 0.5, 0.4), baseline)

    def test_overall_score_is_limited_to_five_significant_figures(self) -> None:
        score = calculate_overall_score(0.5, 0.9, 0.4)
        self.assertEqual(score, 0.74464)

    def test_result_formatter_uses_separate_lines(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = track_run("Demo", self.metrics(0.5, 0.9, 0.4), directory)
            formatted = format_track_run_result(result)

            self.assertIn("Tracking result:\n", formatted)
            self.assertIn("  current_metrics:\n", formatted)
            self.assertIn("    rmse: 0.50000\n", formatted)
            self.assertNotIn("{'saved':", formatted)

    def test_custom_weights_are_normalized(self) -> None:
        score = calculate_overall_score(
            0.5, 0.5, 0.5, {"rmse": 2.0, "r2": 1.0, "mae": 1.0}
        )
        expected = calculate_overall_score(
            0.5, 0.5, 0.5, {"rmse": 0.5, "r2": 0.25, "mae": 0.25}
        )
        self.assertEqual(score, expected)


if __name__ == "__main__":
    unittest.main()
