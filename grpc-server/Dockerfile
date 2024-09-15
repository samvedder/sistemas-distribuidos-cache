FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./proto/ /app/proto/

RUN pip install grpcio-tools

RUN python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/service.proto

COPY . .

CMD ["python", "main.py"]