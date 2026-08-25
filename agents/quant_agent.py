import lightgbm as lgb
import numpy as np
import pandas as pd
import optuna
from typing import Callable, Tuple, Optional, Dict, Any
from sklearn.model_selection import TimeSeriesSplit

def mse_objective(preds: np.ndarray, train_data: lgb.Dataset) -> Tuple[np.ndarray, np.ndarray]:
    """Standard Mean Squared Error objective function."""
    labels = train_data.get_label()
    grad = preds - labels
    hess = np.ones_like(preds)
    return grad, hess

class PurgedTimeSeriesSplit(TimeSeriesSplit):
    """
    Time Series cross-validator with a gap (purged).
    Prevents lookahead bias by ensuring the gap between train and test sets
    is at least the horizon of the target variable (21 days for 21-day RV).
    """
    def __init__(self, n_splits: int = 5, gap: int = 21, test_size: Optional[int] = None):
        super().__init__(n_splits=n_splits, gap=gap, test_size=test_size)

class QuantAgent:
    def __init__(self, objective: Optional[Callable] = mse_objective):
        """
        Initialize the QuantAgent for predicting 21-day Realized Volatility.
        :param objective: Custom objective function. Defaults to standard MSE.
        """
        self.objective = objective
        self.model = None
        self.best_params = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, 
              X_val: Optional[pd.DataFrame] = None, y_val: Optional[pd.Series] = None, 
              params: Optional[Dict[str, Any]] = None):
        if params is None:
            params = self.best_params or {
                'learning_rate': 0.05,
                'num_leaves': 31,
                'verbose': -1
            }
        
        train_data = lgb.Dataset(X_train, label=y_train)
        valid_sets = [train_data]
        if X_val is not None and y_val is not None:
            val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)
            valid_sets.append(val_data)
            
        if self.objective:
            params['objective'] = self.objective
            
        self.model = lgb.train(
            params,
            train_data,
            valid_sets=valid_sets
        )

    def optimize(self, X: pd.DataFrame, y: pd.Series, n_trials: int = 20) -> Dict[str, Any]:
        """
        Optimize hyperparameters using Optuna with Purged Time-Series Split.
        """
        # Set gap to 21 to strictly avoid overlap between training targets (which look forward 21 days) and validation inputs
        cv = PurgedTimeSeriesSplit(n_splits=3, gap=21)
        
        def objective(trial):
            params = {
                'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.1, log=True),
                'num_leaves': trial.suggest_int('num_leaves', 10, 100),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'min_child_samples': trial.suggest_int('min_child_samples', 5, 50),
                'verbose': -1
            }
            
            scores = []
            for train_idx, val_idx in cv.split(X):
                X_train_cv, y_train_cv = X.iloc[train_idx], y.iloc[train_idx]
                X_val_cv, y_val_cv = X.iloc[val_idx], y.iloc[val_idx]
                
                # Check for overlap to guarantee zero lookahead bias
                if val_idx.min() - train_idx.max() <= 21:
                    raise ValueError("Lookahead bias detected! Train and Validation sets overlap.")

                train_data = lgb.Dataset(X_train_cv, label=y_train_cv)
                val_data = lgb.Dataset(X_val_cv, label=y_val_cv, reference=train_data)
                
                if self.objective:
                    params['objective'] = self.objective
                    
                model = lgb.train(
                    params,
                    train_data,
                    valid_sets=[val_data]
                )
                
                preds = model.predict(X_val_cv)
                mse = np.mean((y_val_cv - preds) ** 2)
                scores.append(mse)
                
            return np.mean(scores)

        optuna.logging.set_verbosity(optuna.logging.WARNING)
        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=n_trials)
        
        self.best_params = study.best_params
        self.best_params['verbose'] = -1
        return self.best_params

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict 21-day Realized Volatility."""
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        return self.model.predict(X)

if __name__ == "__main__":
    # Test on sample data payload
    agent = QuantAgent()
    X_sample = pd.DataFrame(np.random.rand(200, 5), columns=[f'feat_{i}' for i in range(5)])
    y_sample = pd.Series(np.random.rand(200))
    
    # Test optimization
    print("Testing optimization...")
    best_params = agent.optimize(X_sample, y_sample, n_trials=2)
    print("Optimization successful. Best params:", best_params)
    
    # Test training and prediction
    agent.train(X_sample, y_sample)
    preds = agent.predict(X_sample)
    print("QuantAgent test successful. Predictions:", preds[:5])
