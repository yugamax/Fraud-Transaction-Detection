from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import pandas as pd
import joblib
import uvicorn
import os
from datetime import datetime
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
df = pd.read_csv("dataset/transaction_recs.csv")

class Trans_data(BaseModel):
    features: list[float]

@app.post("/predict")
async def predict(data: Trans_data):

    if len(data.features) != 18:
        print("Missing features. Expected 18 features.")
        return {"ML error": "Missing features. Expected 18 features."}

    input_data = np.array(data.features).reshape(1, -1)
    prediction = model.predict(input_data)[0]

    if prediction == 1:
        label = "Fraud"
        print(df.shape)
        row_exists = ((df.iloc[:, 2:20] == data.features).all(axis=1)).any()
        if row_exists:
            print("Row is present in the dataset so no changes made.")
        else:
            print("Row is not present in the dataset so updating the csv file.")
            new_row = [len(df)] + [label] + list(data.features) + [datetime.now().strftime("%d-%m-%Y %H:%M:%S")]
            df.loc[len(df)] = new_row
            df.to_csv("dataset/transaction_recs.csv", index=False)

    return {
        "prediction": float(prediction),
        "label": label
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="127.0.0.1", port=port)