from functools import wraps
from flask import request, jsonify, current_app
import jwt
from models import User
from app import db
import bcrypt

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Token inválido!'}), 401

        if not token:
            return jsonify({'message': 'Token ausente!'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(username=data['username']).first()
            if not current_user:
                raise Exception('Usuário não encontrado')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token inválido: {str(e)}'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def create_user(username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

def edit_user(user, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.password = hashed_password
    db.session.commit()

def remove_user(user):
    db.session.delete(user)
    db.session.commit()