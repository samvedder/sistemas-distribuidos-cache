FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto /proto
RUN python -m grpc_tools.protoc -I/proto --python_out=/app --grpc_python_out=/app /proto/service.proto

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]