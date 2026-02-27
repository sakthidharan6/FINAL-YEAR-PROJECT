from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
from backend.data_processor import DataProcessor
from backend.model_service import ModelService
import uvicorn
import os

app = FastAPI(title="INFY Stock Prediction API")

# =========================
# INITIALIZE SERVICES
# =========================
try:
    processor = DataProcessor(ticker="INFY.NS")
    model_service = ModelService(
        model_path=os.path.join(
            "backend", "models", "INFY_CNN_LSTM_model.keras"
        )
    )
except Exception as e:
    print(f"Failed to initialize services: {e}")
    processor = None
    model_service = None

# =========================
# SCHEMAS
# =========================
class PredictionRequest(BaseModel):
    days: int = 1

class PredictionResponse(BaseModel):
    predictions: List[float]
    dates: List[str]

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health_check():
    status = "healthy" if processor and model_service and model_service.model else "unhealthy"
    return {"status": status}

# =========================
# HISTORICAL DATA (ADD MONTH COLUMN)
# =========================
@app.get("/history")
def get_history(period: str = "2y"):
    if not processor:
        raise HTTPException(status_code=503, detail="Data service unavailable")

    try:
        df = processor.fetch_data(period=period)
        df = processor.add_technical_indicators(df)

        # Ensure datetime
        df["Date"] = pd.to_datetime(df["Date"])

        # ✅ Add Month column ONLY
        df["Month"] = df["Date"].dt.to_period("M").astype(str)

        data = df.reset_index(drop=True).to_dict(orient="records")

        # Keep Date unchanged
        for row in data:
            row["Date"] = str(row["Date"])

        return {"data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# PREDICTION ENDPOINT (UNCHANGED)
# =========================
@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    if not processor or not model_service:
        raise HTTPException(status_code=503, detail="Services unavailable")

    try:
        df = processor.fetch_data(period="1y")
        df = processor.add_technical_indicators(df)

        predictions = []
        future_dates = []

        current_sequence, scaler = processor.prepare_input(df)
        last_date = df["Date"].iloc[-1]

        for i in range(request.days):
            pred_scaled = model_service.predict(current_sequence)
            pred_price = processor.inverse_transform_prediction(pred_scaled)

            predictions.append(float(pred_price))

            next_date = last_date + pd.Timedelta(days=i + 1)
            future_dates.append(str(next_date))

            new_step = current_sequence[0, -1, :].copy()
            new_step[0] = pred_scaled

            new_step = np.reshape(new_step, (1, 1, current_sequence.shape[2]))
            current_sequence = np.append(
                current_sequence[:, 1:, :],
                new_step,
                axis=1
            )

        return {
            "predictions": predictions,
            "dates": future_dates
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
