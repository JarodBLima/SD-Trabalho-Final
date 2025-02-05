from flask import Blueprint, request, jsonify, current_app, render_template
import jwt
import datetime
import logging
from models import User
import bcrypt
from app import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger('cliente_logger')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            # Gerar um token JWT
            token = jwt.encode({
                'username': user.username,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)  # Expira em 2 horas
            }, current_app.config['SECRET_KEY'], algorithm="HS256")

            logger.info(f"Usuário {username} logado com sucesso.")
            return jsonify({'token': token})

        logger.warning(f"Tentativa de login inválida para o usuário {username}.")
        return jsonify({'message': 'Credenciais inválidas!'}), 401

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    # No logout, o token JWT é invalidado no lado do cliente (removido do armazenamento)
    logger.info("Usuário deslogado.")
    return jsonify({'message': 'Logout realizado com sucesso!'})
