from datetime import datetime, timezone
from bson import ObjectId


def create_order(db, user_id, items, total_amount, shipping_address, payment_info):
    order = {
        'user_id': ObjectId(user_id),
        'items': [
            {
                'product_id': ObjectId(item['product_id']),
                'name': item['name'],
                'size': item['size'],
                'color': item['color'],
                'quantity': item['quantity'],
                'price': float(item['price'])
            }
            for item in items
        ],
        'total_amount': float(total_amount),
        'status': 'pending',
        'shipping_address': shipping_address,
        'payment_info': payment_info,
        'stripe_payment_intent_id': '',
        'tracking_number': '',
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    result = db.orders.insert_one(order)
    order['_id'] = result.inserted_id
    return order


def find_order_by_id(db, order_id):
    try:
        return db.orders.find_one({'_id': ObjectId(order_id)})
    except Exception:
        return None


def find_orders_by_user(db, user_id, page=1, limit=10):
    skip = (page - 1) * limit
    cursor = db.orders.find({'user_id': ObjectId(user_id)}).sort('created_at', -1).skip(skip).limit(limit)
    total = db.orders.count_documents({'user_id': ObjectId(user_id)})
    return list(cursor), total


def update_order_status(db, order_id, status):
    result = db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {'status': status, 'updated_at': datetime.now(timezone.utc)}}
    )
    return result.modified_count > 0


def update_payment_intent(db, order_id, stripe_payment_intent_id):
    result = db.orders.update_one(
        {'_id': ObjectId(order_id)},
        {'$set': {
            'stripe_payment_intent_id': stripe_payment_intent_id,
            'updated_at': datetime.now(timezone.utc)
        }}
    )
    return result.modified_count > 0


def get_all_orders(db, page=1, limit=20, status_filter=None):
    match = {}
    if status_filter:
        match['status'] = status_filter
    skip = (page - 1) * limit
    cursor = db.orders.find(match).sort('created_at', -1).skip(skip).limit(limit)
    total = db.orders.count_documents(match)
    return list(cursor), total


def create_indexes(db):
    db.orders.create_index('user_id')
    db.orders.create_index('status')
    db.orders.create_index('created_at')
