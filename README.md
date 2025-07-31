# Mock Model Deployment API
This project is a simple simulation of an MLOps pipeline, designed to showcase skills in API development, containerization with Docker, state management, and testing. It's meant to demonstrate the infrastructure required to deploy machine learning models as independent, containerized services.

## Features
- **Model Upload:** Upload Python model files (.pkl) to the service.
- **Dynamic Deployment:** Deploy any uploaded model as its own containerized API endpoint.
- **Health Checks:** The deployment process includes a health check to ensure containers are running successfully before reporting success.
- **State Synchronization:** The API is self-healing, actively checking the status of running containers and updating its state.
- **Inference:** Run predictions by sending data to deployed models.
- **Lifecycle Management:** Tear down and clean up deployed model containers.

## Tech Stack
- **Backend:** Python, FastAPI
- **Containerization:** Docker
- **Testing:** Pytest
- **Libraries:** Pydantic, Uvicorn, HTTPX

## Setup and Installation
### Prerequisites:

- Python 3.12+
- Docker Desktop must be running.

### Steps:

**1. Clone the repository:**

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

**2. Create and activate a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install the dependencies:**
```bash
pip install -r requirements.txt
```

**4. Generate the sample models:**

This project uses placeholder models. Generate them by running:

```bash
python3 create_models.py
```

## Running the Application
To start the main API server, run the following command from the project's root directory:

```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`. Interactive documentation can be found at `http://127.0.0.1:8000/docs`.

## API Usage
**1. Upload a Model**

Upload one of the generated model files (`is_even.pkl` or `text_reverser.pkl`).

- **Endpoint:** `POST /upload`
- **Example** `curl`:
```bash
curl -X POST -F "file=@is_even.pkl" http://127.0.0.1:8000/upload
```
- **Success Response:**
```json
{
  "model_id": "some-unique-uuid",
  "filename": "is_even.pkl",
  "deployed": false
}
```

**2. List Available Models**

Check the status of all uploaded models.
- **Endpoint:** `GET /models`
- **Example** `curl`:

```bash
curl -X GET http://127.0.0.1:8000/models
```
- **Success Response:**
```json
[
  {
    "model_id": "some-unique-uuid",
    "filename": "is_even.pkl",
    "deployed": false
  }
]
```

**3. Deploy a Model**

Deploy an uploaded model. This will build and run a new Docker container. (This may take a minute)
- **Endpoint:** `POST /deploy/{model_id}`
- **Example** `curl`:

```bash
curl -X POST http://127.0.0.1:8000/deploy/some-unique-uuid
```
- **Success Response:**
```json
{
  "message": "Model deployed successfully",
  "model_id": "some-unique-uuid"
}
```
**4. Run Inference**

Send data to a deployed model for a prediction.
- **Endpoint:** `POST /infer/{model_id}`
- **Example** `curl`:

```bash
curl -X POST -H "Content-Type: application/json" -d '{"input": 10}' http://127.0.0.1:8000/infer/some-unique-uuid
```
- **Success Response:**
```json
{
  "model_id": "some-unique-uuid",
  "prediction": true
}
```
**5. Tear down a Model**

Stop and remove a deployed model's container.
- **Endpoint:** `POST /teardown/{model_id}`
- **Example** `curl`:

```bash
curl -X POST http://127.0.0.1:8000/teardown/some-unique-uuid
```
- **Success Response:**
```json
{
  "message": "Model taken down successfully",
  "model_id": "some-unique-uuid"
}
```

## Running the Tests
The test suite includes integration tests that interact with the Docker engine.
> Prerequisite: Docker Desktop must be running.

To run the tests, execute the following command from the project's root directory:
```bash
pytest
```
