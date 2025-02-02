Gerar arquivos do Protobuf para o Servidor de Pedidos:
* Execute:
* * python -m grpc_tools.protoc -I protos --python_out=. --grpc_python_out=. protos/orders.proto

Instale as dependências:
* pip install -r requirements.txt

Execute a aplicação:
* python app.py

Acesse no navegador:
* http://localhost:8080/login (para fazer login)
* http://localhost:8080/ (página inicial)
* http://localhost:8080/create_order (para criar pedidos)
* http://localhost:8080/users (para listar usuários)
* http://localhost:8080/users/create (para criar um usuário)

