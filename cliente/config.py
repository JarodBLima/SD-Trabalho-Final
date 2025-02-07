import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave_secreta'  # Use uma chave secreta forte em produção
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///../instance/users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ORDERS_SERVER_HOST = os.environ.get('ORDERS_SERVER_HOST') or 'servidor-pedidos'
    ORDERS_SERVER_PORT = int(os.environ.get('ORDERS_SERVER_PORT') or 50051)
    NOTIFICATIONS_SERVER_HOST = os.environ.get('NOTIFICATIONS_SERVER_HOST') or 'servidor-notificacoes'
    NOTIFICATIONS_SERVER_PORT = int(os.environ.get('NOTIFICATIONS_SERVER_PORT') or 6000)
    GRPC_RETRY_MAX_RETRIES = 3
    GRPC_RETRY_DELAY = 2
    CA_CERT_PATH = 'certificados/ca.crt'
    SSL_CERT_PATH = 'certificados/cliente.crt'
    SSL_KEY_PATH = 'certificados/cliente.key'