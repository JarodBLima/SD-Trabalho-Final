import grpc
from concurrent import futures
import time
import logging

# Importações geradas pelo Protobuf
import orders_pb2
import orders_pb2_grpc

# Importa a função de enviar notificação do servidor de notificações
from notification_client import enviar_notificacao_para_servidor
import os

# Importações para o cliente RMI
import Pyro4
import Pyro4.naming

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configuração do Flask e SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pedidos.db'
db = SQLAlchemy(app)

# Modelo de Pedido
class Pedido(db.Model):
    id = db.Column(db.String, primary_key=True)
    descricao = db.Column(db.String)
    valor = db.Column(db.Float)
    status = db.Column(db.String)

# Configuração de Logging
logging.basicConfig(filename='servidor-pedidos.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuração do cliente RMI
PAGAMENTO_SERVICE_NAME = "PagamentoService"
PYRO_NS_HOST = "servidor-pagamentos"  # Nome do serviço do servidor de nomes Pyro4 no docker-compose
PYRO_NS_PORT = 9090  # Porta padrão do servidor de nomes Pyro4

def carregar_certificados():
    # Caminhos para os certificados e a chave privada
    cert_path = 'certificados/servidor-pedidos.crt'
    key_path = 'certificados/servidor-pedidos.key'
    ca_cert_path = 'certificados/ca.crt'

    # Verificar se os arquivos existem
    if not os.path.exists(cert_path) or not os.path.exists(key_path) or not os.path.exists(ca_cert_path):
        raise FileNotFoundError("Arquivos de certificado ou chave não encontrados.")

    # Carregar os certificados
    with open(cert_path, 'rb') as f:
        cert = f.read()
    with open(key_path, 'rb') as f:
        key = f.read()
    with open(ca_cert_path, 'rb') as f:
        ca_cert = f.read()

    return cert, key, ca_cert

class OrderService(orders_pb2_grpc.OrderServiceServicer):
    def CreateOrder(self, request, context):
        with app.app_context():
            order_id = request.order_id
            description = request.description
            value = request.value

            # Validações
            if not order_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('ID do pedido é obrigatório.')
                return orders_pb2.OrderReply()
            if not description:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Descrição do pedido é obrigatória.')
                return orders_pb2.OrderReply()
            if value <= 0:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('Valor do pedido deve ser positivo.')
                return orders_pb2.OrderReply()
            if Pedido.query.get(order_id):
                context.set_code(grpc.StatusCode.ALREADY_EXISTS)
                context.set_details('ID do pedido já existe.')
                return orders_pb2.OrderReply()

            # Processar pagamento via RMI
            try:
                with Pyro4.locateNS(host=PYRO_NS_HOST, port=PYRO_NS_PORT) as ns:
                    uri = ns.lookup(PAGAMENTO_SERVICE_NAME)

                with Pyro4.Proxy(uri) as pagamento_service:
                    pagamento_service._pyroTimeout = 10
                    status_pagamento = pagamento_service.processarPagamento(order_id, value)

                if status_pagamento == "Aprovado":
                    novo_pedido = Pedido(id=order_id, descricao=description, valor=value, status="Pagamento Aprovado")
                    logging.info(f"Pagamento aprovado para o pedido {order_id}.")
                    enviar_notificacao_para_servidor(f"Pagamento aprovado para o pedido {order_id}")
                elif status_pagamento == "Reprovado":
                    novo_pedido = Pedido(id=order_id, descricao=description, valor=value, status="Pagamento Reprovado")
                    logging.info(f"Pagamento reprovado para o pedido {order_id}.")
                    enviar_notificacao_para_servidor(f"Pagamento reprovado para o pedido {order_id}")
                else:
                    novo_pedido = Pedido(id=order_id, descricao=description, valor=value, status="Erro no Pagamento")
                    logging.error(f"Erro no processamento de pagamento para o pedido {order_id}: Status desconhecido retornado pelo serviço de pagamento.")
                    enviar_notificacao_para_servidor(f"Erro no pagamento para o pedido {order_id}")

                db.session.add(novo_pedido)
                db.session.commit()
                return orders_pb2.OrderReply(message=f"Pedido {order_id} criado com sucesso! Status do pagamento: {status_pagamento}", order_id=order_id)

            except Pyro4.errors.TimeoutError as e:
                logging.error(f"Timeout na chamada RMI para o serviço de pagamento: {e}")
                context.set_code(grpc.StatusCode.DEADLINE_EXCEEDED)
                context.set_details("Tempo limite excedido ao processar o pagamento.")
                return orders_pb2.OrderReply()
            except Pyro4.errors.CommunicationError as e:
                logging.error(f"Erro de comunicação com o servidor de nomes Pyro4: {e}")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Serviço de pagamento indisponível.")
                return orders_pb2.OrderReply()
            except Pyro4.errors.NamingError as e:
                logging.error(f"Erro ao localizar o serviço de pagamento no servidor de nomes: {e}")
                context.set_code(grpc.StatusCode.UNAVAILABLE)
                context.set_details("Serviço de pagamento não encontrado.")
                return orders_pb2.OrderReply()
            except Exception as e:
                logging.error(f"Erro ao processar pagamento via RMI: {e}")
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details("Erro interno ao processar pagamento.")
                return orders_pb2.OrderReply()

    def GetOrderStatus(self, request, context):
        with app.app_context():
            order_id = request.order_id

            if not order_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('ID do pedido é obrigatório.')
                return orders_pb2.OrderStatusReply()

            pedido = Pedido.query.get(order_id)

            if pedido is None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Pedido não encontrado.')
                return orders_pb2.OrderStatusReply()

            logging.info(f"Consulta de status do pedido {order_id}: {pedido.status}")
            return orders_pb2.OrderStatusReply(order_id=order_id, status=pedido.status)

def serve():
    with app.app_context():
        db.create_all()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    orders_pb2_grpc.add_OrderServiceServicer_to_server(OrderService(), server)

    # Carregar certificados
    server_cert, server_key, ca_cert = carregar_certificados()

    credentials = grpc.ssl_server_credentials(
        [(server_key, server_cert)],
        root_certificates=ca_cert,
        require_client_auth=False
    )

    server.add_secure_port('[::]:50051', credentials)
    server.start()
    logging.info("Servidor de Pedidos iniciado na porta 50051 com SSL.")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

def run_pyro4_nameserver():
    """Inicia o servidor de nomes Pyro4 em uma thread separada."""
    try:
        Pyro4.naming.startNSloop(host=PYRO_NS_HOST, port=PYRO_NS_PORT)
    except Exception as e:
        logging.error(f"Erro ao iniciar o servidor de nomes Pyro4: {e}")

if __name__ == '__main__':
    nameserver_thread = threading.Thread(target=run_pyro4_nameserver)
    nameserver_thread.daemon = True
    nameserver_thread.start()

    serve()