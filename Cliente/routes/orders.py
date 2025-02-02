from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
import grpc
import logging
import time
from utils.auth import token_required
from config import Config
import orders_pb2
import orders_pb2_grpc
from pybreaker import CircuitBreaker

orders_bp = Blueprint('orders', __name__)
logger = logging.getLogger('cliente_logger')

# Cria uma instância do CircuitBreaker
order_breaker = CircuitBreaker(fail_max=3, reset_timeout=10)

def grpc_retry(func, max_retries=Config.GRPC_RETRY_MAX_RETRIES, retry_delay=Config.GRPC_RETRY_DELAY):
    """Decorador para retentar chamadas gRPC."""
    def wrapper(*args, **kwargs):
        retries = 0
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except grpc.RpcError as e:
                retries += 1
                logger.warning(f"Erro gRPC (tentativa {retries}/{max_retries}): {e.details()}")
                if retries < max_retries:
                    time.sleep(retry_delay)
                else:
                    raise  # Lança a exceção após a última tentativa
    return wrapper

@orders_bp.route('/')
@token_required
def index(current_user):
    from app import notifications
    page = request.args.get('page', 1, type=int)
    per_page = 5
    notifications_subset = notifications[(page - 1) * per_page:page * per_page]
    pagination = {
        'page': page,
        'total': len(notifications),
        'per_page': per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < len(notifications)
    }
    return render_template('index.html', notifications=notifications_subset, pagination=pagination)

@orders_bp.route('/create_order', methods=['GET', 'POST'])
@token_required
def create_order(current_user):
    if request.method == 'POST':
        order_id = request.form['order_id']
        description = request.form['description']
        value = request.form['value']

        if not order_id:
            flash('ID do pedido é obrigatório.', 'error')
            return render_template('create_order.html')
        if not description:
            flash('Descrição do pedido é obrigatória.', 'error')
            return render_template('create_order.html')
        if not value:
            flash('Valor do pedido é obrigatório.', 'error')
            return render_template('create_order.html')
        try:
            value = float(value)
            if value <= 0:
                raise ValueError
        except ValueError:
            flash('Valor do pedido deve ser um número positivo.', 'error')
            return render_template('create_order.html')

        @order_breaker
        @grpc_retry
        def _create_order(order_id, description, value):
            with grpc.secure_channel(f'{Config.ORDERS_SERVER_HOST}:{Config.ORDERS_SERVER_PORT}', grpc.ssl_channel_credentials(root_certificates=open(Config.CA_CERT_PATH, 'rb').read()), options=[('grpc.enable_retries', 0)]) as channel:
                stub = orders_pb2_grpc.OrderServiceStub(channel)
                response = stub.CreateOrder(orders_pb2.OrderRequest(order_id=order_id, description=description, value=value), timeout=5)
                logger.info(f"Resposta do Servidor de Pedidos: {response.message}")
                return response

        try:
            response = _create_order(order_id, description, value)
            flash(response.message, 'success')
            return redirect(url_for('orders.index'))

        except grpc.RpcError as e:
            logger.error(f"Erro ao criar pedido (gRPC): {e.details()}")
            flash(f"Erro de comunicação com o servidor: {e.details()}", 'error')
            return render_template('create_order.html')

        except Exception as e:
            logger.error(f"Erro ao criar pedido: {e}")
            flash(f"Erro ao criar pedido: {e}", 'error')
            return render_template('create_order.html')

    return render_template('create_order.html')

@orders_bp.route('/get_order_status/<order_id>')
@token_required
def get_order_status(current_user, order_id):
    if not order_id:
        return jsonify({"error": "ID do pedido é obrigatório."}), 400

    @order_breaker
    @grpc_retry
    def _get_order_status(order_id):
        with grpc.secure_channel(f'{Config.ORDERS_SERVER_HOST}:{Config.ORDERS_SERVER_PORT}', grpc.ssl_channel_credentials(root_certificates=open(Config.CA_CERT_PATH, 'rb').read()), options=[('grpc.enable_retries', 0)]) as channel:
            stub = orders_pb2_grpc.OrderServiceStub(channel)
            response = stub.GetOrderStatus(orders_pb2.OrderStatusRequest(order_id=order_id), timeout=5)
            logger.info(f"Status do pedido {order_id}: {response.status}")
            return response

    try:
        response = _get_order_status(order_id)
        return jsonify({"order_id": order_id, "status": response.status})

    except grpc.RpcError as e:
        logger.error(f"Erro ao consultar status do pedido (gRPC): {e.details()}")
        return jsonify({"error": f"Erro de comunicação com o servidor: {e.details()}"}), 500

    except Exception as e:
        logger.error(f"Erro ao consultar status do pedido: {e}")
        return jsonify({"error": f"Erro ao consultar status do pedido: {e}"}), 500