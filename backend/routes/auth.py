from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)
from datetime import datetime, timezone, timedelta
from models.user import create_user, find_user_by_email, find_user_by_id, update_user, verify_password
from services.auth_service import generate_reset_token, generate_verification_token
from services.email_service import send_verification_email, send_password_reset_email

auth_bp = Blueprint('auth', __name__)


def _user_to_dict(user):
    return {
        'id': str(user['_id']),
        'email': user['email'],
        'full_name': user['full_name'],
        'role': user.get('role', 'user'),
        'avatar': user.get('avatar', ''),
        'is_verified': user.get('is_verified', False)
    }


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()

        if not email or not password or not full_name:
            return jsonify({'error': 'Email, password, and full name are required'}), 400

        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        db = current_app.db
        existing = find_user_by_email(db, email)
        if existing:
            return jsonify({'error': 'Email already registered'}), 409

        user = create_user(db, email, password, full_name)
        user_id = str(user['_id'])

        verification_token = generate_verification_token()
        update_user(db, user_id, {'verification_token': verification_token})

        frontend_url = current_app.config['FRONTEND_URL']
        send_verification_email(email, verification_token, frontend_url)

        access_token = create_access_token(identity=user_id, additional_claims={'role': user['role']})
        refresh_token = create_refresh_token(identity=user_id)

        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': _user_to_dict(user)
        }), 201
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400

        db = current_app.db
        user = find_user_by_email(db, email)
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401

        user_id = str(user['_id'])
        access_token = create_access_token(identity=user_id, additional_claims={'role': user.get('role', 'user')})
        refresh_token = create_refresh_token(identity=user_id)

        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': _user_to_dict(user)
        }), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        from app import jwt_blocklist
        jti = get_jwt()['jti']
        jwt_blocklist.add(jti)
        return jsonify({'message': 'Logged out successfully'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        user = find_user_by_id(db, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        access_token = create_access_token(
            identity=user_id,
            additional_claims={'role': user.get('role', 'user')}
        )
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        db = current_app.db
        user = find_user_by_email(db, email)
        if user:
            token = generate_reset_token()
            expires = datetime.now(timezone.utc) + timedelta(hours=1)
            update_user(db, str(user['_id']), {
                'reset_token': token,
                'reset_token_expires': expires
            })
            send_password_reset_email(email, token, current_app.config['FRONTEND_URL'])

        return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        token = data.get('token', '')
        new_password = data.get('password', '')

        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400

        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400

        db = current_app.db
        user = db.users.find_one({
            'reset_token': token,
            'reset_token_expires': {'$gt': datetime.now(timezone.utc)}
        })
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400

        import bcrypt
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        update_user(db, str(user['_id']), {
            'password_hash': password_hash,
            'reset_token': '',
            'reset_token_expires': None
        })
        return jsonify({'message': 'Password reset successfully'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
