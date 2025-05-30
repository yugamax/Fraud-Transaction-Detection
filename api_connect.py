from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Union
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

pack = joblib.load(os.path.join("model", "models.joblib"))
model = pack['model']
enc1 = pack['enc1']
enc2 = pack['enc2']

class Transaction_data(BaseModel):
    acc_holder: str
    features: list[Union[float , str]]

def encoding(encoder, val):
    try:
        if pd.isna(val) or val == "":
            val = "missing"
        return encoder.transform([val])[0]
    except ValueError:
        return encoder.transform(['missing'])[0]

@app.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    await asyncio.sleep(0.1)
    return {"message": "server is running"}

@app.post("/predict")
async def predict(data: Transaction_data):
    acc_holder = data.acc_holder
    data1 = data.features
    data1 = ["missing" if pd.isna(x) else x for x in data1]
    data2 = data1.copy()
    if len(data2) != 18:
        print("Missing features. Expected 18 features.")
        return {"ML error": "Missing features. Expected 18 features."}

    data2[-2] = encoding(enc1, data2[-2])
    data2[-1] = encoding(enc2, data2[-1])

    input_data = np.array(data2).reshape(1, -1)
    prediction = model.predict(input_data)[0]
    confidence = model.predict_proba(input_data)[0][prediction]

    if prediction == 1 and confidence > 0.8:
        label = "Fraud"
        fr_type = "Unsafe Transaction"

    elif confidence > 0.6 and confidence < 0.8:
        label = "Non - Fraud"
        fr_type = "Mildly Unsafe Transaction"
        df2 = pd.read_csv(os.path.join("dataset", "mildly_unsafe_transactions.csv"))
        if acc_holder in df2["IDs"].values:
            label = "Fraud"
            fr_type = "Unsafe Transaction"
        else:
            print("Putting the mildly unsafe transaction into monitoring dataset.")
            new_row2 = [len(df2)] + [acc_holder] + [datetime.now().strftime("%d-%m-%Y %H:%M:%S")]
            df2.loc[len(df2)] = new_row2
            df2.to_csv(os.path.join("dataset", "mildly_unsafe_transactions.csv"), index=False)
    else:
        label = "Non - Fraud"
        fr_type = "Safe Transaction"
    
    print(f"Confidence: {confidence*100:.2f}%")

    return {
        "prediction": label,
        "Type": fr_type,
        "confidence": f"{confidence*100:.2f}%"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)