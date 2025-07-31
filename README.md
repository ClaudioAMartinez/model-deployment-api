# Mock Model Deployment API
This project is a functional Minimum Viable Product (MVP) for a model inference service. It's designed to showcase core API development skills using Python and FastAPI.

The API allows users to upload pickled Python functions as "models" and then run inference by sending data to them.

## Features
- **Model Upload:** Upload Python model files (.pkl) to the service.
- **List Models:** Get a list of all uploaded models.s
- **Direct Inference:** Run predictions by sending data to an uploaded model.

## Tech Stack
- **Backend:** Python, FastAPI
- **Libraries:** Pydantic, Uvicorn

## Setup and Installation
### Prerequisites:

- Python 3.12+

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
  "filename": "is_even.pkl"
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
    "filename": "is_even.pkl"
  }
]
```

**3. Run Inference**

Send data to an uploaded model for a prediction.
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
