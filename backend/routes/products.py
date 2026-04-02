from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from models.product import (
    create_product, find_product_by_id, search_products,
    update_product, delete_product
)
from models.review import find_reviews_by_product
from bson import ObjectId

products_bp = Blueprint('products', __name__)


def _serialize_product(p):
    if not p:
        return None
    p['id'] = str(p.pop('_id'))
    if 'created_at' in p:
        p['created_at'] = p['created_at'].isoformat()
    if 'updated_at' in p:
        p['updated_at'] = p['updated_at'].isoformat()
    return p


@products_bp.route('/', methods=['GET'])
def list_products():
    try:
        db = current_app.db
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 12))
        sort = request.args.get('sort', 'newest')
        filters = {
            'category': request.args.get('category'),
            'min_price': request.args.get('min_price'),
            'max_price': request.args.get('max_price'),
            'size': request.args.get('size'),
            'color': request.args.get('color')
        }
        filters = {k: v for k, v in filters.items() if v is not None}
        products, total = search_products(db, filters=filters, sort=sort, page=page, limit=limit)
        return jsonify({
            'products': [_serialize_product(p) for p in products],
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        }), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/search', methods=['GET'])
def search():
    try:
        db = current_app.db
        query = request.args.get('q', '')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 12))
        products, total = search_products(db, query=query, page=page, limit=limit)
        return jsonify({
            'products': [_serialize_product(p) for p in products],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/categories', methods=['GET'])
def categories():
    try:
        db = current_app.db
        cats = db.products.distinct('category', {'is_active': True})
        return jsonify({'categories': cats}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        db = current_app.db
        product = find_product_by_id(db, product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        reviews, _ = find_reviews_by_product(db, product_id, page=1, limit=5)
        serialized = _serialize_product(product)
        serialized['recent_reviews'] = [_serialize_review(r) for r in reviews]
        return jsonify({'product': serialized}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


def _serialize_review(r):
    r['id'] = str(r.pop('_id'))
    r['product_id'] = str(r.get('product_id', ''))
    r['user_id'] = str(r.get('user_id', ''))
    if 'created_at' in r:
        r['created_at'] = r['created_at'].isoformat()
    if 'updated_at' in r:
        r['updated_at'] = r['updated_at'].isoformat()
    return r


@products_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        db = current_app.db
        product = create_product(db, data)
        return jsonify({'product': _serialize_product(product)}), 201
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/<product_id>', methods=['PUT'])
@jwt_required()
def update(product_id):
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        data = request.get_json()
        db = current_app.db
        updated = update_product(db, product_id, data)
        if not updated:
            return jsonify({'error': 'Product not found'}), 404
        product = find_product_by_id(db, product_id)
        return jsonify({'product': _serialize_product(product)}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@products_bp.route('/<product_id>', methods=['DELETE'])
@jwt_required()
def delete(product_id):
    try:
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        db = current_app.db
        deleted = delete_product(db, product_id)
        if not deleted:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify({'message': 'Product deleted'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
