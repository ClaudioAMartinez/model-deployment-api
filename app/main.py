import pickle
import uuid
from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

class ModelEntryResponse(BaseModel):
    model_id: str
    filename: str

class InferenceRequest(BaseModel):
    input: Any = Field(
        ...,
        example={"feature_one": "some_text", "feature_two": 123}
    )

class InferenceResponse(BaseModel):
    model_id: str
    prediction: Any

app = FastAPI(title="Mock Model Deployment API")

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

# In-memory "database" to track our models
# In a real app, this would be a proper database.
MODELS = {}

@app.get("/models", response_model=List[ModelEntryResponse])
async def get_models():
    """Get a list of all available models."""
    if not MODELS:
        return []
    
    # Create a list of model details from the in-memory store
    model_list = [
        {"model_id": model_id, "filename": info["filename"]}
        for model_id, info in MODELS.items()
    ]
    
    return model_list

@app.post("/upload", response_model=ModelEntryResponse)
async def upload_model(file: UploadFile = File(...)):
    """Upload a pickled model file."""
    # Generate a unique ID for the model
    model_id = str(uuid.uuid4())
    file_path = MODEL_DIR / f"{model_id}.pkl"

    # Save the uploaded file
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Store model info
    MODELS[model_id] = {"path": file_path, "filename": file.filename}
    
    return {"model_id": model_id, "filename": file.filename}

@app.post("/infer/{model_id}", response_model=InferenceResponse)
async def infer(model_id: str, request_body: InferenceRequest):
    """Run inference using a specified model."""
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    model_path = MODELS[model_id]["path"]
    
    try:
        # Load the model from the file
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        
        # Get the input data for the model
        input_data = request_body.input
        if input_data is None:
            raise HTTPException(status_code=400, detail="No 'input' field in data")

        # Run inference
        prediction = model(input_data)
        
        return {"model_id": model_id, "prediction": prediction}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run inference: {e}")
