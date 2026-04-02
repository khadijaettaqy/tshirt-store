from datetime import datetime, timezone
from bson import ObjectId


def get_cart(db, user_id):
    cart = db.carts.find_one({'user_id': ObjectId(user_id)})
    if not cart:
        cart = {
            'user_id': ObjectId(user_id),
            'items': [],
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
        result = db.carts.insert_one(cart)
        cart['_id'] = result.inserted_id
    return cart


def add_item_to_cart(db, user_id, product_id, size, color, quantity):
    cart = get_cart(db, user_id)
    # Check if item already exists
    existing = None
    for item in cart.get('items', []):
        if (str(item['product_id']) == str(product_id) and
                item['size'] == size and item['color'] == color):
            existing = item
            break

    if existing:
        db.carts.update_one(
            {
                'user_id': ObjectId(user_id),
                'items.product_id': ObjectId(product_id),
                'items.size': size,
                'items.color': color
            },
            {
                '$inc': {'items.$.quantity': quantity},
                '$set': {'updated_at': datetime.now(timezone.utc)}
            }
        )
    else:
        db.carts.update_one(
            {'user_id': ObjectId(user_id)},
            {
                '$push': {
                    'items': {
                        'product_id': ObjectId(product_id),
                        'size': size,
                        'color': color,
                        'quantity': quantity
                    }
                },
                '$set': {'updated_at': datetime.now(timezone.utc)}
            }
        )
    return get_cart(db, user_id)


def remove_item_from_cart(db, user_id, product_id, size, color):
    db.carts.update_one(
        {'user_id': ObjectId(user_id)},
        {
            '$pull': {
                'items': {
                    'product_id': ObjectId(product_id),
                    'size': size,
                    'color': color
                }
            },
            '$set': {'updated_at': datetime.now(timezone.utc)}
        }
    )
    return get_cart(db, user_id)


def update_cart_item_quantity(db, user_id, product_id, size, color, quantity):
    if quantity <= 0:
        return remove_item_from_cart(db, user_id, product_id, size, color)
    db.carts.update_one(
        {
            'user_id': ObjectId(user_id),
            'items.product_id': ObjectId(product_id),
            'items.size': size,
            'items.color': color
        },
        {
            '$set': {
                'items.$.quantity': quantity,
                'updated_at': datetime.now(timezone.utc)
            }
        }
    )
    return get_cart(db, user_id)


def clear_cart(db, user_id):
    db.carts.update_one(
        {'user_id': ObjectId(user_id)},
        {'$set': {'items': [], 'updated_at': datetime.now(timezone.utc)}}
    )


def create_indexes(db):
    db.carts.create_index('user_id', unique=True)
