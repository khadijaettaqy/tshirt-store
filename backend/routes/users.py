from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import find_user_by_id, update_user, add_to_wishlist, remove_from_wishlist, get_wishlist
from models.product import find_product_by_id

users_bp = Blueprint('users', __name__)


def _user_to_dict(user):
    return {
        'id': str(user['_id']),
        'email': user['email'],
        'full_name': user['full_name'],
        'role': user.get('role', 'user'),
        'avatar': user.get('avatar', ''),
        'is_verified': user.get('is_verified', False),
        'preferences': user.get('preferences', {}),
        'wishlist': user.get('wishlist', [])
    }


@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        user = find_user_by_id(db, user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        return jsonify({'user': _user_to_dict(user)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        allowed = ['full_name', 'avatar', 'preferences']
        update_data = {k: v for k, v in data.items() if k in allowed}
        db = current_app.db
        update_user(db, user_id, update_data)
        user = find_user_by_id(db, user_id)
        return jsonify({'user': _user_to_dict(user)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/wishlist', methods=['GET'])
@jwt_required()
def get_wishlist_route():
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        wishlist_ids = get_wishlist(db, user_id)
        products = []
        for pid in wishlist_ids:
            p = find_product_by_id(db, pid)
            if p:
                p['id'] = str(p.pop('_id'))
                if 'created_at' in p:
                    p['created_at'] = p['created_at'].isoformat()
                if 'updated_at' in p:
                    p['updated_at'] = p['updated_at'].isoformat()
                products.append(p)
        return jsonify({'wishlist': products}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/wishlist/<product_id>', methods=['POST'])
@jwt_required()
def add_to_wishlist_route(product_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        product = find_product_by_id(db, product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        add_to_wishlist(db, user_id, product_id)
        return jsonify({'message': 'Added to wishlist'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/wishlist/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wishlist_route(product_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        remove_from_wishlist(db, user_id, product_id)
        return jsonify({'message': 'Removed from wishlist'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
