from flask import Blueprint, request, render_template, redirect, url_for, jsonify
from app import db
from models import User
from utils.auth import token_required, create_user, edit_user, remove_user
import logging

users_bp = Blueprint('users', __name__, url_prefix='/users')
logger = logging.getLogger('cliente_logger')

@users_bp.route('/', methods=['GET'])
@token_required
def list_users(current_user):
    page = request.args.get('page', 1, type=int)
    per_page = 5
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('users.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@token_required
def create_user_route(current_user):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            create_user(username, password)
            logger.info(f"Usuário {username} criado com sucesso.")
            return redirect(url_for('users.list_users'))
        except Exception as e:
            logger.error(f"Erro ao criar usuário: {e}")
            return "Erro ao criar usuário", 500

    return render_template('create_user.html')

@users_bp.route('/edit/<username>', methods=['GET', 'POST'])
@token_required
def edit_user_route(current_user, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "Usuário não encontrado", 404

    if request.method == 'POST':
        new_password = request.form['password']
        try:
            edit_user(user, new_password)
            logger.info(f"Senha do usuário {username} alterada com sucesso.")
            return redirect(url_for('users.list_users'))
        except Exception as e:
            logger.error(f"Erro ao editar usuário: {e}")
            return "Erro ao editar usuário", 500

    return render_template('edit_user.html', user=user)

@users_bp.route('/remove/<username>', methods=['POST'])
@token_required
def remove_user_route(current_user, username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return "Usuário não encontrado", 404

    try:
        remove_user(user)
        logger.info(f"Usuário {username} removido com sucesso.")
        return redirect(url_for('users.list_users'))
    except Exception as e:
        logger.error(f"Erro ao remover usuário: {e}")
        return "Erro ao remover usuário", 500