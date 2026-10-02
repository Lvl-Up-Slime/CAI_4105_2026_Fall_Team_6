Where:

Python

```
current_metrics = {
    "rmse": float,
    "r2": float,
    "mae": float
}

```

## 2. Versioned File Naming

Save qualifying runs using: `{project_name}_v1.json`, `{project_name}_v2.json`, etc. The version number must be determined automatically by scanning `output_dir` for files matching `{project_name}_v*.json`. Determine the highest version number numerically (e.g., v10 > v9).

## 3. Previous Saved Iteration Comparison

The current run should be compared against the *immediately previous saved iteration* (the previous version of the notebook/project) to detect changes. Do not compare against the *historically best* run for the purpose of determining whether the current run changed.

## 4. Evaluation Metrics & Formatted Change Tracking

Track exactly these three metrics: **RMSE, R², MAE**.

- **Do NOT track lines of code (LOC) or syntax changes.**
- Track ALL changes in evaluation metrics, regardless of whether the current iteration did better or worse.
- Do NOT use boolean flags (e.g., `changed: true`) to record metric changes.
- Instead, format the changes as human-readable strings using exactly this template: `"Previous {x}: [{float}], Current {x}: [{float}], {x} changed by: [{float}]"` (where {x} is rmse, r2, and mae).

## 5. Save Condition

A new version should be saved ONLY if at least one evaluation metric changed compared to the previous saved iteration.

## 6. Overall Evaluation Score

There should be one overall score used to determine the historically best run. Use these default configurable weights: `{"rmse": 0.60, "r2": 0.25, "mae": 0.15}`

**Important:** The scoring system must account for the optimization directions (RMSE/MAE = lower is better; R² = higher is better). Implement a clearly documented normalization/scoring approach so that better metrics contribute to a better overall score.

## 7. Human-Readable Summaries

The tracker must generate coherent, human-readable narrative strings explaining the variables for both the historical best and the previous iteration comparison.

- **previous_iteration_comparison**: Create a coherent print statement summarizing the score comparison and all the metric changes.
  - **Example:** `"Compared to previous version 3 (Score: 0.89), the current run scored 0.86. Previous rmse: 0.405, Current rmse: 0.412, rmse changed by: 0.007. Previous r2: 0.88, Current r2: 0.87, r2 changed by: -0.01. Previous mae: 0.295, Current mae: 0.301, mae changed by: 0.006."`
- **historical_best**: Create a coherent print statement explaining the historically best model, its version, and its score compared to the current run.
  - **Example:** `"The historical best remains version 2 with an overall score of 0.93. The current version (v4, Score: 0.86) did not beat the historical best."` OR `"The current version is the new historical best, beating version 2's score of 0.91!"`
  use line breaks after each section for clearer readability.

## 8. Saved JSON Structure

The saved JSON must store these human-readable strings directly:

JSON

```
{
    "project_name": "Challenge1",
    "version": 4,
    "timestamp": "2026-10-01T21:30:00",
    "current_metrics": {
        "rmse": 0.412,
        "r2": 0.87,
        "mae": 0.301
    },
    "current_overall_score": 0.86,
    "metric_changes": [
        "Previous rmse: 0.405, Current rmse: 0.412, rmse changed by: 0.007",
        "Previous r2: 0.88, Current r2: 0.87, r2 changed by: -0.01",
        "Previous mae: 0.295, Current mae: 0.301, mae changed by: 0.006"
    ],
    "previous_iteration_comparison": "Compared to previous version 3 (Score: 0.89), the current run scored 0.86. Previous rmse: 0.405, Current rmse: 0.412, rmse changed by: 0.007. Previous r2: 0.88, Current r2: 0.87, r2 changed by: -0.01. Previous mae: 0.295, Current mae: 0.301, mae changed by: 0.006.",
    "historical_best": "The historical best remains version 2 with an overall score of 0.93. The current version (v4, Score: 0.86) did not beat the historical best.",
    "scoring_weights": {
        "rmse": 0.60,
        "r2": 0.25,
        "mae": 0.15
    }
}

```

## 9. Notebook Integration (Console Printing)

When the function runs, it should `print()` the `previous_iteration_comparison` and `historical_best` narrative strings to the console so the user can easily read the outcome of the iteration without opening the JSON file.

## 10. Code Quality Requirements

- Use Python's standard library (`json`, `pathlib`, `datetime`).
- Use type hints, docstrings, and clear variable names.
- Provide the complete Python implementation, notebook integration instructions, and example outputs.