# Challenge 2 

## Overview of data
This project predicts whether an online shopping session ends in a
purchase (`Revenue=True`). 

- F1 is used to measure purchases as it is the minority attribute in training

## Preprocessing and validation

- `Revenue` is used as the target and excludes `ID` from predictions.

- We used the Yeo–Johnson power transform to reduce skewness in numerical
  features, then standardized them to a common scale.

- Before one-hot encoding, we grouped categories that appeared in fewer than
  1% of training sessions into an infrequent category for each feature. This
  helps the models avoid learning overly specific patterns from rare browsers
  or traffic sources. During cross-validation, preprocessing was fitted only
  on the training portion of each fold.
  
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

We selected **Gradient Boosting** because it achieved the highest holdout F1 for `Revenue=True`. We used five-fold cross-validation on the development set to tune the purchase probability cutoff from **50%** to **39.9%**. On the holdout set, this raised F1 from **0.662** to **0.668**, ahead of Random Forest (**0.660**). **Support Vector Machine** deserves acknoledgement given that our metrics showed a mean training F1 score of **0.777**, This showed promising performance compared to all other models at training but with holdout validation scores it proved to be inconsistent. Particulat discoveries worth highlight is our **K-Nearest Neighbors** model actually had a perfect score in training but had a significant drop at holdout **0.629**. This is probably expected behavior with KNN since the model predicted rows are available as neighbors at distance zero. The validation steps shows a more accurate representation of the models performance. 


We refit the selected pipeline model and generate the final predictions for the test CSV. 
The submission records each predictions as a `Revenue` value of `True` or `False`.

