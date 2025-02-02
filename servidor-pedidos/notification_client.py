import socket
import json
import logging
import ssl

# Configurações do Servidor de Notificações
NOTIFICATIONS_SERVER_HOST = 'servidor-notificacoes'  # Nome do serviço no Docker Compose
NOTIFICATIONS_SERVER_PORT = 6000

def enviar_notificacao_para_servidor(mensagem):
    """Envia uma notificação para o Servidor de Notificações via Socket."""
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile='certificados/ca.crt')
    context.load_cert_chain(certfile='certificados/servidor-pedidos.crt', keyfile='certificados/servidor-pedidos.key')

    try:
        with socket.create_connection((NOTIFICATIONS_SERVER_HOST, NOTIFICATIONS_SERVER_PORT)) as sock:
            with context.wrap_socket(sock, server_hostname=NOTIFICATIONS_SERVER_HOST) as ssock:
                ssock.sendall(json.dumps({"message": mensagem}).encode('utf-8'))
                logging.info(f"Notificação enviada para o Servidor de Notificações: {mensagem}")
    except Exception as e:
        logging.error(f"Erro ao enviar notificação para o Servidor de Notificações: {e}")