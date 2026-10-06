"""Small end-to-end example for the v3 metric-only tracker."""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


from ml_tracking_utility import format_track_run_result, track_run


np.random.seed(42)
features = 2.5 * np.random.rand(100, 1) + 1.5
target = 5 + 3 * features + np.random.randn(100, 1)

X_train, X_test, y_train, y_test = train_test_split(
    features,
    target,
    test_size=0.8,
    random_state=42,
)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
rmse = float(np.sqrt(mse))
r2 = float(r2_score(y_test, y_pred))
mae = float(mean_absolute_error(y_test, y_pred))

print(f"Root Mean Squared Error: {rmse:.4f}")
print(f"Mean Absolute Error: {mae:.4f}")
print(f"R-squared Score: {r2:.4f}")

result = track_run(
    project_name="Challenge1",
    current_metrics={"rmse": rmse, "r2": r2, "mae": mae},
    output_dir="./versions",
)

print(format_track_run_result(result))

plt.scatter(X_test, y_test, color="blue", label="Actual Data")
plt.plot(X_test, y_pred, color="red", linewidth=2, label="Regression Line")
plt.title("Simple Linear Regression")
plt.xlabel("Independent Variable (X)")
plt.ylabel("Dependent Variable (Y)")
plt.legend()
plt.show()
