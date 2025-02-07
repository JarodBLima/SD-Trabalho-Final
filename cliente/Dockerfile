# Imagem base Python
FROM python:3.9-slim-buster

# Diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar os arquivos do projeto
COPY . .

COPY certificados /app/certificados

# Instalar as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copiar os arquivos .proto e gerar o código gRPC
COPY protos /app/protos
RUN python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/orders.proto

# Expor a porta que o Flask vai usar
EXPOSE 8080

# Comando para executar a aplicação
CMD ["python", "app.py"]