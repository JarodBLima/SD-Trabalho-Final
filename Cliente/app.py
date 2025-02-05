from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from utils.logs import setup_logger
import logging
from concurrent.futures import ThreadPoolExecutor
import time
import socket
import json

db = SQLAlchemy()
notifications = []

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    # Configuração de Logging
    app.logger = setup_logger('cliente_logger', 'cliente.log', logging.DEBUG)

    # Importar as rotas
    from routes.orders import orders_bp
    from routes.users import users_bp
    from routes.notifications import notifications_bp
    from routes.auth import auth_bp

    # Registrar as blueprints
    app.register_blueprint(orders_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(auth_bp)

    def conectar_ao_servidor_notificacoes():
        """Conecta-se ao Servidor de Notificações em uma thread separada."""
        def thread_func():
            global notifications
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            retries = 0
            max_retries = 5
            retry_delay = 5

            while retries < max_retries:
                try:
                    client_socket.connect((app.config['NOTIFICATIONS_SERVER_HOST'], app.config['NOTIFICATIONS_SERVER_PORT']))
                    app.logger.info(f"Conectado ao Servidor de Notificações em {app.config['NOTIFICATIONS_SERVER_HOST']}:{app.config['NOTIFICATIONS_SERVER_PORT']}")
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        mensagem = json.loads(data.decode('utf-8'))
                        app.logger.info(f"Notificação recebida: {mensagem['message']}")
                        notifications.append(mensagem['message'])
                except Exception as e:
                    app.logger.error(f"Erro na conexão com o Servidor de Notificações: {e}")
                    retries += 1
                    app.logger.info(f"Tentando reconectar ao Servidor de Notificações em {retry_delay} segundos... (Tentativa {retries}/{max_retries})")
                    time.sleep(retry_delay)
                finally:
                    client_socket.close()

            if retries == max_retries:
                app.logger.error("Não foi possível estabelecer conexão com o Servidor de Notificações após várias tentativas.")

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(thread_func)

    with app.app_context():
        db.create_all()
        conectar_ao_servidor_notificacoes()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=8080, ssl_context=(app.config['SSL_CERT_PATH'], app.config['SSL_KEY_PATH']))
