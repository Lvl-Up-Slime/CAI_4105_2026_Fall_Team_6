# ML Tracker v3 Guide

## What it does

The tracker compares the current RMSE, R2, and MAE values with the latest saved run.

A new JSON version is created when at least one metric changes.

LOC and syntax are not tracked in v3.

The runnable integration example is [test_tracking_capabilities_v3.py](test_tracking_capabilities_v3.py).

## 1. Import the tracker

Keep `ml_tracking_utility.py` beside the script or notebook.

```python
from ml_tracking_utility import format_track_run_result, track_run
```

The utility uses only the Python standard library.

## 2. Train and evaluate the model

Calculate the three required metrics:

```python
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = float(np.sqrt(mse))
r2 = float(r2_score(y_test, y_pred))
mae = float(mean_absolute_error(y_test, y_pred))
```

The metric names must be exactly `rmse`, `r2`, and `mae`.

RMSE and MAE must be non-negative finite numbers.

## 3. Track the run

Call the tracker after evaluation:

```python
result = track_run(
    project_name="Challenge1",
    current_metrics={
        "rmse": rmse,
        "r2": r2,
        "mae": mae,
    },
    output_dir="./versions",
)

print(format_track_run_result(result))
```

The tracker creates `./versions` when needed.

## 4. Understand the result

The returned result includes:

- `saved: bool` - whether a JSON file was created.
- `version: int | None` - the new version number, if saved.
- `path: str | None` - the saved JSON path, if saved.
- `reason: str | None` - why an unchanged run was rejected.
- `current_overall_score: float` - the weighted score for this run.
- `metric_changes: list[str]` - formatted comparisons for RMSE, R2, and MAE.
- `previous_iteration_comparison: str` - comparison with the latest saved run.
- `historical_best: str` - comparison with the best saved run.

The same comparison messages are printed to the console.

## 5. Understand version behavior

The first run saves as `Challenge1_v1.json`.

A later run saves as v2, v3, and so on only when at least one metric changes.

An unchanged run does not create a file or consume a version number.

The previous iteration is always the latest saved version.

The historical best is selected from all saved versions.

## 6. Read the change messages

Each changed-run JSON contains one string for every metric:

```text
Previous rmse: [0.5], Current rmse: [0.6], rmse changed by: [0.1]
Previous r2: [0.9], Current r2: [0.88], r2 changed by: [-0.02]
Previous mae: [0.4], Current mae: [0.45], mae changed by: [0.05]
```

The strings are stored in `metric_changes`.

They are also included in `previous_iteration_comparison`.

## 7. Customize the score

The default weights are:

```python
{"rmse": 0.60, "r2": 0.25, "mae": 0.15}
```

Supply custom weights when needed:

```python
result = track_run(
    project_name="Challenge1",
    current_metrics={"rmse": rmse, "r2": r2, "mae": mae},
    output_dir="./versions",
    scoring_weights={"rmse": 0.50, "r2": 0.30, "mae": 0.20},
)
```

Weights are normalized automatically.

RMSE and MAE are better when lower.

R2 is better when higher.

## 8. Example sequence

**Run 1**

No previous file exists.

The tracker saves `Challenge1_v1.json`.

**Run 2**

The metrics are unchanged.

The tracker prints the comparison but does not save a new file.

**Run 3**

RMSE changes from `0.50` to `0.48`.

The tracker saves `Challenge1_v2.json` and records all three formatted metric strings.

**Run 4**

The current score is lower than v2, but v1 remains the historical best.

The JSON keeps both facts in separate narrative fields.
