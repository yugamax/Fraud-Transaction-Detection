from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
import uvicorn
import os
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load(r"model/xgb_model.joblib")

class Trans_data(BaseModel):
    features: list[float]

@app.post("/predict")
async def predict(data: Trans_data):

    if len(data.features) != 18:
        return {"ML error": "Missing features. Expected 18 features."}

    input_data = np.array(data.features).reshape(1, -1)
    prediction = model.predict(input_data)[0]

    
    label = "Fraud" if prediction == 1 else "Non - Fraud"
    print(f"Prediction: {prediction}, Label: {label}")
    return {
        "prediction": float(prediction),
        "label": label
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)