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

| Model	| Mean training F1 | Mean CV F1 | Holdout Validation F1 |
|---|---:|---:|----:|
| Logistic Regression | 0.694 |	0.693 | 0.646 |
| Naïve Bayes | 0.648 | 0.650 | 0.611 |
| K-Nearest Neighbors | 1.000 | 0.688 | 0.629 |
| Support Vector Machine | 0.777 | 0.704 | 0.652 |
| Decision Tree	| 0.716	| 0.695	| 0.644 |
| Random Forest	| 0.754	| 0.710	| 0.660 |
| Gradient Boost | 0.777 | 0.705 | 0.668 |

- We used `GridSearchCV()` to tune all the individual models which showed a marginal
increase without regression for all of our models. 


## Final Result

We selected the **Gradient Boost** because it lead to a F1 score results of **0.668** when using holdout to validate. Gradient boosting had superior performace as is representative of most tree-based models. Therefore
it is no surprise that **Random Forest** scored very similarly to Gradients boost and could be interchangeable.
**Support Vector Machine** deserves acknoledgement given that our metrics showed a mean training F1 score of 
**0.777**, This showed promising performance compared to all other models at training but with holdout validation scores it proved to be inconsistent. Particulat discoveries worth highlight is our **K-Nearest Neighbors** model actually had a perfect score in training but had a significant drop at holdout **0.629**. This is probably expected behavior with KNN since the model predicted rows are available as neighbors at distance zero. The validation steps shows a more accurate representation of the models performance. 


We refit the selected pipeline model and generate the final predictions for the test CSV. 
The submission records each predictions as a `Revenue` value of `True` or `False`.

