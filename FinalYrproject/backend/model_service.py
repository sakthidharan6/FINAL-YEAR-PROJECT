import tensorflow as tf
import numpy as np
import os

class ModelService:
    def __init__(self, model_path="backend/models/INFY_CNN_LSTM_model.keras"):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found at {self.model_path}")
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def predict(self, input_sequence):
        """
        Predicts the next value based on input sequence.
        Input shape should be (1, 60, 11).
        """
        if self.model is None:
            raise RuntimeError("Model is not loaded.")
        
        prediction = self.model.predict(input_sequence)
        return prediction[0][0]
