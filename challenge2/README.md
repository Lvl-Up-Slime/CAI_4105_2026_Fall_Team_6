# Challenge 2 

## Overview of data
This project predicts whether an online shopping session ends in a
purchase (`Revenue=True`). 

- F1 is used to measure purchases as it is the minority attribute in training

## Preprocessing and validation

- `Revenue` is used as the target and excludes `ID` from predictions.
  
- Standardized numeric features and one-hot encode categorical features
  is used. During cross-validation, the preprocessor is fitted on the
  training portion of each fold.
  
- 80%/20% split holdout using stratified samples and `random_state=42`.

- Compare baselines and tune our selected models using the five
  stratified folds on the development set. Rank models by mean
  CV F1 for `Revenue=True`.

## Model comparison

| Model | Mean training F1 | Mean CV F1 |
|---|---:|---:|
| Logistic Regression | 0.674 | 0.662 |
| K-Nearest Neighbors | 0.729 | 0.633 |
| Naïve Bayes | 0.563 | 0.558 |
| Linear Support Vector Machine | 0.681 | 0.680 |
| RBF Support Vector Machine | 0.712| 0.672 |
| Decision Tree | ??? | ??? |
| Random Forest | ??? | ??? |
| Gradient Boosting | ??? | ??? |

We used `Grid Search` to tune (list of models)...

## Final Result
We selected the **K-Nearest Neighbors** because it lead to a cv results of **0.633**.

We refit the selected pipeline model and generate the final predictions for the test CSV. 
The submission records each predictions as a `Revenue` value of `True` or `False`.

