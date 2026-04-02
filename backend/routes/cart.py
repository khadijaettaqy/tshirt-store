from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.cart import get_cart, add_item_to_cart, remove_item_from_cart, update_cart_item_quantity, clear_cart
from models.product import find_product_by_id
from bson import ObjectId

cart_bp = Blueprint('cart', __name__)


def _serialize_cart(cart, db):
    items = []
    for item in cart.get('items', []):
        product = find_product_by_id(db, str(item['product_id']))
        if product:
            items.append({
                'product_id': str(item['product_id']),
                'name': product.get('name'),
                'price': product.get('price'),
                'image': product.get('images', [''])[0] if product.get('images') else '',
                'size': item['size'],
                'color': item['color'],
                'quantity': item['quantity']
            })
    return {
        'id': str(cart.get('_id', '')),
        'items': items,
        'item_count': sum(i['quantity'] for i in items)
    }


@cart_bp.route('/', methods=['GET'])
@jwt_required()
def get():
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        cart = get_cart(db, user_id)
        return jsonify({'cart': _serialize_cart(cart, db)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/add', methods=['POST'])
@jwt_required()
def add():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        size = data.get('size')
        color = data.get('color')
        quantity = int(data.get('quantity', 1))

        if not product_id or not size or not color:
            return jsonify({'error': 'product_id, size, and color are required'}), 400

        db = current_app.db
        product = find_product_by_id(db, product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        cart = add_item_to_cart(db, user_id, product_id, size, color, quantity)
        return jsonify({'cart': _serialize_cart(cart, db)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/remove', methods=['DELETE'])
@jwt_required()
def remove():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        size = data.get('size')
        color = data.get('color')
        db = current_app.db
        cart = remove_item_from_cart(db, user_id, product_id, size, color)
        return jsonify({'cart': _serialize_cart(cart, db)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/update', methods=['PUT'])
@jwt_required()
def update():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        size = data.get('size')
        color = data.get('color')
        quantity = int(data.get('quantity', 1))
        db = current_app.db
        cart = update_cart_item_quantity(db, user_id, product_id, size, color, quantity)
        return jsonify({'cart': _serialize_cart(cart, db)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
def clear():
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        clear_cart(db, user_id)
        return jsonify({'message': 'Cart cleared'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
