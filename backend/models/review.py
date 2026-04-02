from datetime import datetime, timezone
from bson import ObjectId


def create_review(db, product_id, user_id, rating, comment):
    is_verified = check_verified_purchase(db, user_id, product_id)
    review = {
        'product_id': ObjectId(product_id),
        'user_id': ObjectId(user_id),
        'rating': int(rating),
        'comment': comment,
        'is_verified_purchase': is_verified,
        'helpful_votes': [],
        'helpful_count': 0,
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    result = db.reviews.insert_one(review)
    review['_id'] = result.inserted_id
    return review


def find_review_by_id(db, review_id):
    try:
        return db.reviews.find_one({'_id': ObjectId(review_id)})
    except Exception:
        return None


def find_reviews_by_product(db, product_id, page=1, limit=10):
    skip = (page - 1) * limit
    cursor = db.reviews.find(
        {'product_id': ObjectId(product_id)}
    ).sort('created_at', -1).skip(skip).limit(limit)
    total = db.reviews.count_documents({'product_id': ObjectId(product_id)})
    return list(cursor), total


def update_review(db, review_id, rating, comment):
    result = db.reviews.update_one(
        {'_id': ObjectId(review_id)},
        {'$set': {
            'rating': int(rating),
            'comment': comment,
            'updated_at': datetime.now(timezone.utc)
        }}
    )
    return result.modified_count > 0


def delete_review(db, review_id):
    result = db.reviews.delete_one({'_id': ObjectId(review_id)})
    return result.deleted_count > 0


def mark_helpful(db, review_id, user_id):
    result = db.reviews.update_one(
        {'_id': ObjectId(review_id)},
        {
            '$addToSet': {'helpful_votes': user_id},
            '$inc': {'helpful_count': 1}
        }
    )
    return result.modified_count > 0


def check_verified_purchase(db, user_id, product_id):
    order = db.orders.find_one({
        'user_id': ObjectId(user_id),
        'items.product_id': ObjectId(product_id),
        'status': {'$in': ['processing', 'shipped', 'delivered']}
    })
    return order is not None


def create_indexes(db):
    db.reviews.create_index('product_id')
    db.reviews.create_index('user_id')
    db.reviews.create_index([('product_id', 1), ('user_id', 1)], unique=True, sparse=True)
