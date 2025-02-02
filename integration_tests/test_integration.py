import pytest
import requests
import grpc
import time
from cliente.app import create_app
from cliente.config import Config
import orders_pb2
import orders_pb2_grpc
import json

# Configurações para os testes
BASE_URL_CLIENTE = 'https://localhost:8080'
BASE_URL_SERVIDOR_PEDIDOS = 'https://localhost:50051'  # Usar a porta gRPC segura
BASE_URL_SERVIDOR_NOTIFICACOES = 'https://localhost:6000'

# Certificados (ajustar os caminhos se necessário)
CA_CERT = 'certificados/ca.crt'
CLIENTE_CERT = ('certificados/cliente.crt', 'certificados/cliente.key')
SERVIDOR_PEDIDOS_CERT = ('certificados/servidor-pedidos.crt', 'certificados/servidor-pedidos.key')
SERVIDOR_NOTIFICACOES_CERT = ('certificados/servidor-notificacoes.crt', 'certificados/servidor-notificacoes.key')

@pytest.fixture(scope="module")
def setup():
    # Iniciar a aplicação cliente em uma thread separada
    app = create_app(Config)
    with app.app_context():
        # Aqui você pode criar um usuário de teste, se necessário
        pass
    ctx = app.test_request_context()
    ctx.push()

    yield

    ctx.pop()

def test_fluxo_completo(setup):
    # 1. Login do Cliente
    login_data = {
        'username': 'testuser',
        'password': 'password'
    }
    response = requests.post(f'{BASE_URL_CLIENTE}/auth/login', data=login_data, verify=CA_CERT, cert=CLIENTE_CERT)
    assert response.status_code == 200
    token = response.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Criar um Pedido
    with grpc.secure_channel(f'servidor-pedidos:50051', grpc.ssl_channel_credentials(root_certificates=open(CA_CERT, 'rb').read())) as channel:
        stub = orders_pb2_grpc.OrderServiceStub(channel)
        response = stub.CreateOrder(orders_pb2.OrderRequest(order_id='123', description='Teste', value=10.0))
        assert response.message == f'Pedido 123 criado com sucesso! Status do pagamento: Aprovado'
        assert response.order_id == '123'

    # 3. Consultar Status do Pedido
        response = stub.GetOrderStatus(orders_pb2.OrderStatusRequest(order_id='123'))
        assert response.order_id == '123'
        assert response.status == 'Pagamento Aprovado'

    # 4. Verificar Notificações (pode demorar um pouco)
    time.sleep(15)  # Aguardar as notificações
    response = requests.get(f'{BASE_URL_CLIENTE}/notifications', headers=headers, verify=CA_CERT, cert=CLIENTE_CERT)
    assert response.status_code == 200
    notifications = response.json()
    assert len(notifications) > 0
    assert "Pedido 123 criado" in notifications

def test_servidor_pedidos_indisponivel(setup):
    # 1. Login do Cliente
    login_data = {
        'username': 'testuser',
        'password': 'password'
    }
    response = requests.post(f'{BASE_URL_CLIENTE}/auth/login', data=login_data, verify=CA_CERT, cert=CLIENTE_CERT)
    assert response.status_code == 200
    token = response.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Parar o Servidor de Pedidos (simular indisponibilidade)
    import docker
    client = docker.from_env()
    container = client.containers.get('servidor-pedidos')  # Substitua pelo nome correto do contêiner
    container.stop()

    # 3. Tentar criar um pedido
    with pytest.raises(Exception) as e:
        with grpc.secure_channel(f'servidor-pedidos:50051', grpc.ssl_channel_credentials(root_certificates=open(CA_CERT, 'rb').read())) as channel:
            stub = orders_pb2_grpc.OrderServiceStub(channel)
            response = stub.CreateOrder(orders_pb2.OrderRequest(order_id='123', description='Teste', value=10.0))

    # 4. Reiniciar o Servidor de Pedidos
    container.start()

def test_servidor_notificacoes_indisponivel(setup):
    # 1. Login do Cliente
    login_data = {
        'username': 'testuser',
        'password': 'password'
    }
    response = requests.post(f'{BASE_URL_CLIENTE}/auth/login', data=login_data, verify=CA_CERT, cert=CLIENTE_CERT)
    assert response.status_code == 200
    token = response.json()['token']
    headers = {'Authorization': f'Bearer {token}'}

    # 2. Parar o Servidor de Notificações
    import docker
    client = docker.from_env()
    container = client.containers.get('servidor-notificacoes')  # Substitua pelo nome correto do contêiner
    container.stop()

    # 3. Tentar obter notificações (deve retornar vazio, pois o servidor está indisponível)
    response = requests.get(f'{BASE_URL_CLIENTE}/notifications', headers=headers, verify=CA_CERT, cert=CLIENTE_CERT)
    assert response.status_code == 200
    notifications = response.json()
    assert len(notifications) == 0  # Não deve haver notificações

    # 4. Reiniciar o Servidor de Notificações
    container.start()