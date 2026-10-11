# Challenge 1

### Randomized Grid Search
  - We ran a randomized grid search across all our models.
  - We noticed a performance regression when compiling our Python notebook with grid search.
  - So we decided to take the optimized parameters and hard-code them into our models. 
### Parameter Tuning
  We tested a variety of parameters for our models sequentially and tested for the best performer.
  
#### Decisions Tree
``` python
"Decision Tree": Pipeline([
    ("prep", preprocessor),
    ("model", DecisionTreeRegressor(max_depth=14, 
                                    ccp_alpha=0.2, 
                                    max_features=None, 
                                    max_leaf_nodes=None,
                                    min_samples_split=18,
                                    min_samples_leaf=7,  
                                    splitter="best", 
                                    criterion="squared_error", 
                                    random_state=42)),
]),
```
#### Random Forest
``` python
"Random Forest": Pipeline([
    ("prep", preprocessor),
    ("model", RandomForestRegressor(n_estimators=350, 
                                    max_depth=30,
                                    min_samples_split=3,
                                    min_samples_leaf=1,
                                    max_features='sqrt',
                                    bootstrap=True,
                                    random_state=42))
]),
```
#### XGBoost
``` python
"XGBoost": Pipeline([
    ("prep", preprocessor),
    ("model", XGBRegressor(random_state=42))
])
```

### Feature Engineering
  - We attempted feature engineering, but got insignificant results with some models, even regressing in performance.
  - Our first instinct was to take a direct approach to feature engineering by using the most obvious features that influence apartment prices, such as the number of bedrooms and square feet. It did not provide any significant improvement.
  - We created a correlation heat matrix to isolate the features that had the most impact on the model. We discovered that the longitude feature was actually creating a negative impact.
  - Using the k-means approach, we created a new categorical feature called neighborhood clusters, combining longitude and latitude. This resulted in a worse RMSE.
### Filtering Outliers
  - We used the interquartile range method to filter extreme statistical outliers from our target. Still, this led to a worse RMSE score.
### Model Ensembling
  - Using the results of our best-performing models, **XGBoost (RMSE: 425.412)** and **Random Forest (RMSE: 458.849)**, we created our final model using an ensembling technique. This resulted in a lower overall RMSE than the initial Random Forest and XGBoost results.
### Our test results show that XGBoost and Random Forest significantly outperformed the other models.
``` text
Linear Regression - RMSE: 556.753
Decision Tree - RMSE: 513.564
Random Forest - RMSE: 458.849
XGBoost - RMSE: 425.412
```
### Results of our final stacking model

```text
Stacking Model - RMSE: 427.949
```
