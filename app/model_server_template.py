import pickle
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any

# This path will be inside the Docker container
MODEL_PATH = "/app/model.pkl" 
    
app = FastAPI()

class InferenceRequest(BaseModel):
    input: Any

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

@app.get("/health")
def health_check():
    """Simple health check to confirm the server is running."""
    return {"status": "ok"}

@app.post("/predict")
def predict(request: InferenceRequest):
    prediction = model(request.input)
    return {"prediction": prediction}
