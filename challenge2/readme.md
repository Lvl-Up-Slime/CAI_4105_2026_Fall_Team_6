# Challenge 2

## Logistic Regression
```python
logistic_pipeline = Pipeline([
    ("prep", preprocessor),
    ("model", LogisticRegression(max_iter=1000)),
])
```
## Naïve Bayes
```python
Bayes_pipe = Pipeline([
    ("prep", preprocessor),
    ("clf", BernoulliNB())
])
```
## K-Nearest Neighbors
```python
knn_pipeline = Pipeline([
    ("prep", preprocessor),
    ("model", KNeighborsClassifier(n_neighbors=5)),
])
```
## Support Vector Machine
```python

svmlinear_pipe = Pipeline([
    ("prep", preprocessor),
    ("model", SVC(kernel="linear", C=1.0, class_weight="balanced"))
])

svmrbf_pipe = Pipeline([
    ("prep", preprocessor),
    ("model", SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale",
        class_weight="balanced"
    ))
])
```
## Decision Tree
```python

```
## Random Forest
```python

```
## Gradient Boosting
```python

```