Gerar arquivos do Protobuf para o Servidor de Pedidos:
* Execute:
* * python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/orders.proto

Instale a dependência:
* pip install -r requirements.txt
