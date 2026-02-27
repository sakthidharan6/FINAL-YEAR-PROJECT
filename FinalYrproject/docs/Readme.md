
The proposed model is MARS (Multivariate Adaptive Regression Splines).

Among all tested models (time series, econometric, ML, and deep learning), 
MARS had the lowest RMSE on the test set: 0.0079, 
meaning it was most accurate at predicting Infosys stock prices.

Why MARS?

Handles Nonlinearity: Infosys stock prices exhibit complex, nonlinear patterns due to market fluctuations.

Automatic Feature Selection: MARS identifies important variables (open, high, low, volume) and ignores irrelevant ones.

Robustness: Reduces overfitting through cross-validation and pruning, making it reliable for unseen data.