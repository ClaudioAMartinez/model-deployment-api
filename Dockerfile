FROM python:3.12-slim

WORKDIR /
COPY ./app /app

COPY ./requirements.txt /
RUN pip install -r requirements.txt

ARG MODEL_PATH
COPY ${MODEL_PATH} /app/model.pkl

CMD ["uvicorn", "app.model_server_template:app", "--host", "0.0.0.0", "--port", "80"]
