from flask import Blueprint, request, render_template, jsonify
from utils.auth import token_required
from app import notifications
import logging

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')
logger = logging.getLogger('cliente_logger')

@notifications_bp.route('/')
@token_required
def get_notifications(current_user):
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
    return render_template('notifications.html', notifications=notifications_subset, pagination=pagination)