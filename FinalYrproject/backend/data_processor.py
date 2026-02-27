import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

class DataProcessor:
    def __init__(self, ticker="INFY.NS"):
        self.ticker = ticker
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        # Feature order matches the model training: 
        # ['Close', 'Open', 'High', 'Low', 'Volume', 'MA10', 'MA20', 'EMA10', 'EMA20', 'RSI', 'MACD']
        self.feature_columns = ['Close', 'Open', 'High', 'Low', 'Volume', 
                                'MA10', 'MA20', 'EMA10', 'EMA20', 'RSI', 'MACD']

    def fetch_data(self, period="2y"):
        """Fetches historical data from Yahoo Finance."""
        ticker_obj = yf.Ticker(self.ticker)
        df = ticker_obj.history(period=period)
        if df.empty:
            raise ValueError(f"No data found for ticker {self.ticker}")
        df = df.reset_index()
        # Ensure we have date but keep it for plotting, model needs values only
        return df

    def add_technical_indicators(self, df):
        """Calculates MA, EMA, RSI, MACD."""
        df = df.copy()
        
        # Simple Moving Averages
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        
        # Exponential Moving Averages
        df['EMA10'] = df['Close'].ewm(span=10, adjust=False).mean()
        df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        
        # Drop NaN values created by indicators
        df.dropna(inplace=True)
        return df

    def prepare_input(self, df, sequence_length=60):
        """
        Scales the data and prepares the last sequence for prediction.
        Returns the scaled sequence and the scaler (inverse transform needed later).
        """
        # Select only the required feature columns
        data = df[self.feature_columns].values
        
        # Fit scaler on the available data (in production, we should ideally use a pretrained scaler, 
        # but fitting on recent history is a common approximation if distribution is similar)
        # Note: If the model was trained on a specific scaler state, this might introduce skew. 
        # Assuming dynamic scaling based on input window is acceptable for this demo.
        scaled_data = self.scaler.fit_transform(data)
        
        # Get the last sequence
        if len(scaled_data) < sequence_length:
            raise ValueError(f"Not enough data points. Need at least {sequence_length}")
            
        last_sequence = scaled_data[-sequence_length:]
        # Reshape to (1, 60, 11)
        last_sequence = np.expand_dims(last_sequence, axis=0)
        
        return last_sequence, self.scaler

    def scale_value(self, value, feature_index=0):
        """Helper to inverse scale a single value (prediction)."""
        # Create a dummy array to inverse transform
        # We only care about the target column (usually Close, index 0 in our list if consistent?)
        # Wait, Close is index 0 in feature_columns.
        
        # Create a placeholder array with same shape as features
        dummy = np.zeros((1, len(self.feature_columns)))
        dummy[0, feature_index] = value
        
        # We can't easily inverse just one with standard MinMaxScaler if it expects all features.
        # However, min_ and scale_ attributes allow direct calculation.
        # X_std = (X - X.min) / (X.max - X.min)
        # X_scaled = X_std * (max - min) + min
        
        # Inverse: X = X_scaled * scale_ + min_
        
        return value * self.scaler.data_range_[feature_index] + self.scaler.data_min_[feature_index]

    def inverse_transform_prediction(self, prediction_value):
        """
        Inverse transform the predicted value. 
        Assumes prediction corresponds to 'Close' price which is at index 0 of feature_columns.
        """
        # prediction_value is scalar or shape (1,1)
        # Close is at index 0
        min_val = self.scaler.data_min_[0]
        range_val = self.scaler.data_range_[0]
        return prediction_value * range_val + min_val
