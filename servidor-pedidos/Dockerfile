FROM python:3.9-slim-buster
WORKDIR /app
COPY protos /app/protos
COPY requirements.txt /app
COPY certificados /app/certificados
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py /app
RUN python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/orders.proto
EXPOSE 50051
CMD ["python", "app.py"]