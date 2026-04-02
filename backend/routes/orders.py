from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.order import (
    create_order, find_order_by_id, find_orders_by_user, update_order_status, update_payment_intent
)
from models.cart import clear_cart
from services.stripe_service import create_payment_intent
from bson import ObjectId

orders_bp = Blueprint('orders', __name__)


def _serialize_order(order):
    if not order:
        return None
    order['id'] = str(order.pop('_id'))
    order['user_id'] = str(order.get('user_id', ''))
    for item in order.get('items', []):
        item['product_id'] = str(item['product_id'])
    if 'created_at' in order:
        order['created_at'] = order['created_at'].isoformat()
    if 'updated_at' in order:
        order['updated_at'] = order['updated_at'].isoformat()
    return order


@orders_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        items = data.get('items', [])
        shipping_address = data.get('shipping_address', {})
        total_amount = data.get('total_amount', 0)

        if not items:
            return jsonify({'error': 'No items in order'}), 400

        db = current_app.db
        payment_info = {'method': 'stripe', 'status': 'pending'}
        order = create_order(db, user_id, items, total_amount, shipping_address, payment_info)
        order_id = str(order['_id'])

        # Create Stripe payment intent
        client_secret = None
        try:
            pi = create_payment_intent(
                amount=int(total_amount * 100),
                currency='usd',
                metadata={'order_id': order_id, 'user_id': user_id}
            )
            if pi:
                update_payment_intent(db, order_id, pi['id'])
                client_secret = pi['client_secret']
        except Exception as stripe_err:
            current_app.logger.warning(f'Stripe error: {stripe_err}')

        return jsonify({
            'order': _serialize_order(order),
            'client_secret': client_secret
        }), 201
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/', methods=['GET'])
@jwt_required()
def list_orders():
    try:
        user_id = get_jwt_identity()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        db = current_app.db
        orders, total = find_orders_by_user(db, user_id, page, limit)
        return jsonify({
            'orders': [_serialize_order(o) for o in orders],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        order = find_order_by_id(db, order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        if str(order['user_id']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        return jsonify({'order': _serialize_order(order)}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/<order_id>/confirm-payment', methods=['POST'])
@jwt_required()
def confirm_payment(order_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        order = find_order_by_id(db, order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        if str(order['user_id']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403

        update_order_status(db, order_id, 'processing')
        db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {'payment_info.status': 'paid'}}
        )
        clear_cart(db, user_id)
        order = find_order_by_id(db, order_id)
        return jsonify({'order': _serialize_order(order)}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@orders_bp.route('/<order_id>/tracking', methods=['GET'])
@jwt_required()
def tracking(order_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        order = find_order_by_id(db, order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        if str(order['user_id']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        return jsonify({
            'order_id': order_id,
            'status': order.get('status'),
            'tracking_number': order.get('tracking_number', ''),
            'updated_at': order.get('updated_at').isoformat() if order.get('updated_at') else None
        }), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
