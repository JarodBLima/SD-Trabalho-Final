import socket
import threading
import json
import logging
import time
import ssl

# Configuração do servidor
HOST = '0.0.0.0'
PORT = 6000

# Lista de clientes conectados
clientes = []

# Configuração de Logging
logging.basicConfig(filename='notificacoes.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def handle_client(conn, addr):
    """Gerencia a conexão com um cliente."""
    logging.info(f"Novo cliente conectado: {addr}")
    clientes.append(conn)
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break  # Cliente desconectou
            # Não faz nada com os dados recebidos, apenas mantém a conexão
    except Exception as e:
        logging.error(f"Erro na conexão com {addr}: {e}")
    finally:
        clientes.remove(conn)
        conn.close()
        logging.info(f"Cliente desconectado: {addr}")

def enviar_notificacao(mensagem):
    """Envia uma notificação para todos os clientes conectados."""
    logging.info(f"Enviando notificação: {mensagem}")
    for cliente in clientes:
        try:
            cliente.sendall(mensagem.encode('utf-8'))
        except Exception as e:
            logging.error(f"Erro ao enviar notificação: {e}")

def main():
    """Função principal do servidor."""
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile='certificados/servidor-notificacoes.crt', keyfile='certificados/servidor-notificacoes.key')
    context.load_verify_locations(cafile='certificados/ca.crt')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        logging.info(f"Servidor de Notificações ouvindo em {HOST}:{PORT}")

        with context.wrap_socket(server, server_side=True) as ssock:
            # Simulando o recebimento de notificações do Servidor de Pedidos
            threading.Thread(target=simular_recebimento_notificacoes, daemon=True).start()

            while True:
                conn, addr = ssock.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.start()
                logging.info(f"Clientes ativos: {threading.active_count() - 2}")

def simular_recebimento_notificacoes():
    """Simula o recebimento de notificações a cada 10 segundos."""
    i = 1
    while True:
        time.sleep(10)
        mensagem = json.dumps({"message": f"Notificação nº {i} do servidor!"})
        enviar_notificacao(mensagem)
        i += 1

if __name__ == "__main__":
    main()