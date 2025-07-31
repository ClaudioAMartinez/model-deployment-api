import io
import pickle
import pytest
from fastapi.testclient import TestClient
from app.main import app, MODELS, DEPLOYMENTS
from app.models import is_even

# --- Test Setup ---
client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_state_between_tests():
    """A fixture to reset the in-memory 'databases' before each test."""
    MODELS.clear()
    DEPLOYMENTS.clear()

# --- Helper Functions ---
def create_dummy_pickle(obj):
    """Creates an in-memory pickle file for uploading."""
    file_stream = io.BytesIO()
    pickle.dump(obj, file_stream)
    file_stream.seek(0)
    return file_stream

def dummy_func_for_testing(x):
        return x

# --- Tests ---
def test_get_models_empty():
    """Test that fetching models returns an empty list initially."""
    response = client.get("/models")
    assert response.status_code == 200
    assert response.json() == []

def test_upload_and_get_models():
    """Test uploading a model and then fetching the list of models."""
    dummy_pkl_file = create_dummy_pickle(dummy_func_for_testing)
    
    response = client.post(
        "/upload",
        files={"file": ("dummy_model.pkl", dummy_pkl_file, "application/octet-stream")}
    )
    assert response.status_code == 200
    upload_data = response.json()

    response = client.get("/models")
    assert response.status_code == 200
    models_list = response.json()
    assert len(models_list) == 1
    assert models_list[0]["model_id"] == upload_data["model_id"]

def test_infer_model_not_found():
    """Test that inference fails with a 404 for a non-existent model ID."""
    response = client.post("/infer/fake-id", json={"input": 10})
    assert response.status_code == 404

def test_successful_inference():
    """Test the full workflow: upload, deploy, and then successfully infer."""
    is_even_pkl = create_dummy_pickle(is_even)
    upload_response = client.post(
        "/upload",
        files={"file": ("is_even.pkl", is_even_pkl, "application/octet-stream")}
    )
    assert upload_response.status_code == 200
    model_id = upload_response.json()["model_id"]

    try:
        deploy_response = client.post(f"/deploy/{model_id}")
        assert deploy_response.status_code == 200, deploy_response.json().get("detail")

        inference_response = client.post(f"/infer/{model_id}", json={"input": 10})
        assert inference_response.status_code == 200
        assert inference_response.json()["prediction"] == True
    finally:
        client.post(f"/teardown/{model_id}")
