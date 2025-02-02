import pytest
from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Banco de dados em memória para testes
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()

def test_index_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 302  # Redireciona para o login

def test_login_logout(client):
    # Cria um usuário para teste
    with app.app_context():
        user = User(username='testuser', password='password')
        db.session.add(user)
        db.session.commit()

    # Login
    response = client.post('/login', data={'username': 'testuser', 'password': 'password'})
    assert response.status_code == 302  # Redireciona para /
    assert b'Redirecting...' in response.data

    # Logout
    response = client.get('/logout')
    assert response.status_code == 302  # Redireciona para /login
    assert b'Redirecting...' in response.data

def test_create_order_page(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get('/create_order')
    assert response.status_code == 200
    assert b'Criar Pedido' in response.data  # Verifica se o texto está na página

def test_users_page(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get('/users')
    assert response.status_code == 200

def test_create_user(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.post('/users/create', data={'username': 'newuser', 'password': 'newpassword'})
    assert response.status_code == 302  # Redireciona para a lista de usuários
    with app.app_context():
        assert User.query.filter_by(username='newuser').first() is not None

def test_edit_user(client):
    with app.app_context():
        user = User(username='edituser', password='password')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.post('/users/edit/edituser', data={'password': 'newpassword'})
    assert response.status_code == 302
    with app.app_context():
        edited_user = User.query.filter_by(username='edituser').first()
        assert edited_user.password != 'password'

def test_remove_user(client):
    with app.app_context():
        user = User(username='removeuser', password='password')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.post('/users/remove/removeuser')
    assert response.status_code == 302
    with app.app_context():
        assert User.query.filter_by(username='removeuser').first() is None

def test_notifications_page(client):
    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get('/notifications')
    assert response.status_code == 200
    assert b'Notificações' in response.data

# Adicione mais testes conforme necessário (ex: testes de integração com o Servidor de Pedidos)