from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.order import get_all_orders, update_order_status, find_order_by_id
from models.product import search_products
from models.navigation import (
    get_most_visited_pages, get_user_journeys, get_session_analytics, get_device_breakdown
)
from bson import ObjectId
from datetime import datetime, timezone, timedelta

admin_bp = Blueprint('admin', __name__)


def _require_admin():
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return False
    return True


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        db = current_app.db
        total_orders = db.orders.count_documents({})
        total_users = db.users.count_documents({})
        total_products = db.products.count_documents({'is_active': True})
        pipeline = [{'$group': {'_id': None, 'total': {'$sum': '$total_amount'}}}]
        rev_result = list(db.orders.aggregate(pipeline))
        total_revenue = rev_result[0]['total'] if rev_result else 0

        recent_orders = list(db.orders.find({}).sort('created_at', -1).limit(10))
        for o in recent_orders:
            o['id'] = str(o.pop('_id'))
            o['user_id'] = str(o.get('user_id', ''))
            for item in o.get('items', []):
                item['product_id'] = str(item['product_id'])
            if o.get('created_at'):
                o['created_at'] = o['created_at'].isoformat()
            if o.get('updated_at'):
                o['updated_at'] = o['updated_at'].isoformat()

        return jsonify({
            'stats': {
                'total_orders': total_orders,
                'total_revenue': round(total_revenue, 2),
                'total_users': total_users,
                'total_products': total_products
            },
            'recent_orders': recent_orders
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/sales-analytics', methods=['GET'])
@jwt_required()
def sales_analytics():
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        days = int(request.args.get('days', 30))
        since = datetime.now(timezone.utc) - timedelta(days=days)
        db = current_app.db
        pipeline = [
            {'$match': {'created_at': {'$gte': since}}},
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$created_at'},
                        'month': {'$month': '$created_at'},
                        'day': {'$dayOfMonth': '$created_at'}
                    },
                    'revenue': {'$sum': '$total_amount'},
                    'orders': {'$sum': 1}
                }
            },
            {'$sort': {'_id': 1}}
        ]
        data = list(db.orders.aggregate(pipeline))
        for d in data:
            d['date'] = f"{d['_id']['year']}-{d['_id']['month']:02d}-{d['_id']['day']:02d}"
            del d['_id']
        return jsonify({'sales_data': data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        db = current_app.db
        cursor = db.users.find({}, {'password_hash': 0}).skip(skip).limit(limit)
        total = db.users.count_documents({})
        users = []
        for u in cursor:
            u['id'] = str(u.pop('_id'))
            if u.get('created_at'):
                u['created_at'] = u['created_at'].isoformat()
            users.append(u)
        return jsonify({'users': users, 'total': total, 'page': page}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@jwt_required()
def update_user_route(user_id):
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        data = request.get_json()
        allowed = ['role', 'is_verified']
        update_data = {k: v for k, v in data.items() if k in allowed}
        db = current_app.db
        from datetime import datetime, timezone
        update_data['updated_at'] = datetime.now(timezone.utc)
        db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
        return jsonify({'message': 'User updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/inventory', methods=['GET'])
@jwt_required()
def inventory():
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        db = current_app.db
        products = list(db.products.find({'is_active': True}))
        low_stock = []
        for p in products:
            p['id'] = str(p.pop('_id'))
            total_stock = sum(s.get('stock', 0) for s in p.get('sizes', []))
            p['total_stock'] = total_stock
            if total_stock < 10:
                low_stock.append(p)
            if p.get('created_at'):
                p['created_at'] = p['created_at'].isoformat()
            if p.get('updated_at'):
                p['updated_at'] = p['updated_at'].isoformat()
        return jsonify({'products': products, 'low_stock': low_stock}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
def list_orders():
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        status_filter = request.args.get('status')
        db = current_app.db
        orders, total = get_all_orders(db, page, limit, status_filter)
        serialized = []
        for o in orders:
            o['id'] = str(o.pop('_id'))
            o['user_id'] = str(o.get('user_id', ''))
            for item in o.get('items', []):
                item['product_id'] = str(item['product_id'])
            if o.get('created_at'):
                o['created_at'] = o['created_at'].isoformat()
            if o.get('updated_at'):
                o['updated_at'] = o['updated_at'].isoformat()
            serialized.append(o)
        return jsonify({'orders': serialized, 'total': total, 'page': page}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/orders/<order_id>/status', methods=['PUT'])
@jwt_required()
def update_status(order_id):
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        data = request.get_json()
        status = data.get('status')
        valid_statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        db = current_app.db
        update_order_status(db, order_id, status)
        return jsonify({'message': 'Order status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/navigation-analytics', methods=['GET'])
@jwt_required()
def navigation_analytics():
    try:
        if not _require_admin():
            return jsonify({'error': 'Admin access required'}), 403
        days = int(request.args.get('days', 30))
        db = current_app.db
        most_visited = get_most_visited_pages(db, limit=20, days=days)
        user_journeys = get_user_journeys(db, limit=20)
        session_analytics = get_session_analytics(db, days=days)
        device_breakdown = get_device_breakdown(db, days=days)
        for j in user_journeys:
            j['session_id'] = str(j.pop('_id', ''))
            if j.get('user_id'):
                j['user_id'] = str(j['user_id'])
            if j.get('start_time'):
                j['start_time'] = j['start_time'].isoformat()
            if j.get('end_time'):
                j['end_time'] = j['end_time'].isoformat()
        if session_analytics and '_id' in session_analytics:
            del session_analytics['_id']
        return jsonify({
            'most_visited_pages': most_visited,
            'user_journeys': user_journeys,
            'session_analytics': session_analytics,
            'device_breakdown': device_breakdown
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
