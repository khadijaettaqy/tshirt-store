from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.review import (
    create_review, find_review_by_id, find_reviews_by_product,
    update_review, delete_review, mark_helpful
)
from models.product import add_review_to_product
from models.user import find_user_by_id

reviews_bp = Blueprint('reviews', __name__)


def _serialize_review(r, db=None):
    r['id'] = str(r.pop('_id'))
    r['product_id'] = str(r.get('product_id', ''))
    user_id = r.get('user_id')
    r['user_id'] = str(user_id) if user_id else ''
    if db and user_id:
        user = db.users.find_one({'_id': user_id}, {'full_name': 1})
        r['author_name'] = user['full_name'] if user else 'Anonymous'
    if 'created_at' in r:
        r['created_at'] = r['created_at'].isoformat()
    if 'updated_at' in r:
        r['updated_at'] = r['updated_at'].isoformat()
    return r


@reviews_bp.route('/', methods=['POST'])
@jwt_required()
def create():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        product_id = data.get('product_id')
        rating = data.get('rating')
        comment = data.get('comment', '')

        if not product_id or rating is None:
            return jsonify({'error': 'product_id and rating are required'}), 400
        if not 1 <= int(rating) <= 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        db = current_app.db
        # Check for existing review
        from bson import ObjectId as _ObjId
        existing = db.reviews.find_one({'product_id': _ObjId(product_id), 'user_id': _ObjId(user_id)})

        review = create_review(db, product_id, user_id, rating, comment)
        add_review_to_product(db, product_id, str(review['_id']), int(rating))
        return jsonify({'review': _serialize_review(review, db)}), 201
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@reviews_bp.route('/product/<product_id>', methods=['GET'])
def get_reviews(product_id):
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        db = current_app.db
        reviews, total = find_reviews_by_product(db, product_id, page, limit)
        return jsonify({
            'reviews': [_serialize_review(r, db) for r in reviews],
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@reviews_bp.route('/<review_id>', methods=['PUT'])
@jwt_required()
def update(review_id):
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        db = current_app.db
        review = find_review_by_id(db, review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        if str(review['user_id']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        rating = data.get('rating', review['rating'])
        comment = data.get('comment', review['comment'])
        update_review(db, review_id, rating, comment)
        review = find_review_by_id(db, review_id)
        return jsonify({'review': _serialize_review(review, db)}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@reviews_bp.route('/<review_id>', methods=['DELETE'])
@jwt_required()
def delete(review_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        review = find_review_by_id(db, review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        if str(review['user_id']) != user_id:
            return jsonify({'error': 'Not authorized'}), 403
        delete_review(db, review_id)
        return jsonify({'message': 'Review deleted'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@reviews_bp.route('/<review_id>/helpful', methods=['POST'])
@jwt_required()
def helpful(review_id):
    try:
        user_id = get_jwt_identity()
        db = current_app.db
        mark_helpful(db, review_id, user_id)
        return jsonify({'message': 'Marked as helpful'}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
