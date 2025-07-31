import pickle
import uuid
import shutil
import docker
import httpx
import time
from pathlib import Path
from typing import Any, List

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel, Field

# --- Pydantic Models ---
class ModelEntryResponse(BaseModel):
    model_id: str
    filename: str
    deployed: bool = False

class InferenceRequest(BaseModel):
    input: Any = Field(
        ...,
        json_schema_extra={"example": {"feature_one": "some_text", "feature_two": 123}}
    )

class InferenceResponse(BaseModel):
    model_id: str
    prediction: Any

class DeployResponse(BaseModel):
    message: str
    model_id: str

class TeardownResponse(BaseModel):
    message: str
    model_id: str

# --- Application Setup ---
app = FastAPI(title="Mock Model Deployment API")

MODEL_DIR = Path("models")
if MODEL_DIR.exists():
    shutil.rmtree(MODEL_DIR)
MODEL_DIR.mkdir()

# An in-memory "database" to track our models.
# In a real app, this would be a proper database.
MODELS = {}
DEPLOYMENTS = {}

# --- API Endpoints ---
@app.get("/models", response_model=List[ModelEntryResponse])
async def get_models():
    """Get a list of all available models and their deployment status."""
    if not MODELS:
        return []
    
    model_list = []
    for model_id in list(DEPLOYMENTS.keys()):
        try:
            container = DEPLOYMENTS[model_id]["container"]
            container.reload()
            if container.status != 'running':
                del DEPLOYMENTS[model_id]
        except docker.errors.NotFound:
            del DEPLOYMENTS[model_id]

    for model_id, info in MODELS.items():
        model_list.append({
            "model_id": model_id,
            "filename": info["filename"],
            "deployed": model_id in DEPLOYMENTS
        })

    return model_list

@app.post("/upload", response_model=ModelEntryResponse)
async def upload_model(file: UploadFile = File(...)):
    """Upload a pickled model file."""
    model_id = str(uuid.uuid4())
    file_path = MODEL_DIR / f"{model_id}.pkl"

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    MODELS[model_id] = {"path": file_path, "filename": file.filename}
    
    return {"model_id": model_id, "filename": file.filename, "deployed": False}

@app.post("/deploy/{model_id}")
async def deploy_model(model_id: str):
    """Deploy a model by building and running its Docker container."""
    if model_id not in MODELS:
        raise HTTPException(status_code=404, detail="Model not found")

    if model_id in DEPLOYMENTS:
        raise HTTPException(status_code=400, detail="Model is already deployed")
    
    try:
        client = docker.from_env()
        model_path = str(MODELS[model_id]["path"])
        image_tag = f"model-image-{model_id}"

        client.images.build(
            path=".", dockerfile="Dockerfile", tag=image_tag,
            buildargs={"MODEL_PATH": model_path}
        )

        # Assign a new port for each deployment.
        port = 8001 + len(DEPLOYMENTS)
        
        container = client.containers.run(
            image_tag, detach=True, ports={'80/tcp': port}
        )
        
        for _ in range(10):
            container.reload()
            
            if container.status == 'exited':
                logs = container.logs().decode('utf-8')
                raise HTTPException(status_code=500, detail=f"Container exited unexpectedly. Logs: {logs}")

            if container.status == 'running':
                try:
                    async with httpx.AsyncClient(timeout=10.0) as health_client:
                        response = await health_client.get(f"http://localhost:{port}/health")
                    if response.status_code == 200:
                        DEPLOYMENTS[model_id] = {"container": container, "port": port}
                        return {"message": "Model deployed successfully", "model_id": model_id}
                except httpx.RequestError:
                    # Container is running but not yet ready for requests.
                    pass
            
            time.sleep(1)

        container.stop()
        container.remove()
        raise HTTPException(status_code=500, detail="Health check timed out. Container failed to become healthy.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to deploy model: {e}")

@app.post("/teardown/{model_id}", response_model=TeardownResponse)
async def teardown_model(model_id: str):
    """Stop and remove a deployed model's container."""
    if model_id not in DEPLOYMENTS:
        raise HTTPException(status_code=404, detail="Model is not deployed")

    try:
        deployment = DEPLOYMENTS[model_id]
        container = deployment["container"]
        container.stop()
        container.remove()
        del DEPLOYMENTS[model_id]
        return {"message": "Model taken down successfully", "model_id": model_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to teardown model: {e}")

@app.post("/infer/{model_id}", response_model=InferenceResponse)
async def infer(model_id: str, request_body: InferenceRequest):
    """Run inference by proxying a request to a deployed model."""
    if model_id not in DEPLOYMENTS:
        raise HTTPException(status_code=404, detail="Model not deployed")

    deployment = DEPLOYMENTS[model_id]
    port = deployment["port"]
    url = f"http://localhost:{port}/predict"
    
    try:
        # Forward the request to the specific model's container.
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"input": request_body.input})
        
        prediction_data = response.json()
        return {"model_id": model_id, "prediction": prediction_data["prediction"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run inference: {e}")
