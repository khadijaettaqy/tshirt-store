from datetime import datetime, timezone
from bson import ObjectId


def create_product(db, data):
    product = {
        'name': data.get('name'),
        'description': data.get('description', ''),
        'price': float(data.get('price', 0)),
        'sku': data.get('sku'),
        'category': data.get('category', ''),
        'sizes': data.get('sizes', []),
        'colors': data.get('colors', []),
        'images': data.get('images', []),
        'reviews': [],
        'avg_rating': 0.0,
        'num_reviews': 0,
        'is_active': True,
        'tags': data.get('tags', []),
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    result = db.products.insert_one(product)
    product['_id'] = result.inserted_id
    return product


def find_product_by_id(db, product_id):
    try:
        return db.products.find_one({'_id': ObjectId(product_id), 'is_active': True})
    except Exception:
        return None


def find_product_by_sku(db, sku):
    return db.products.find_one({'sku': sku})


def search_products(db, query=None, filters=None, sort='created_at', page=1, limit=12):
    filters = filters or {}
    match = {'is_active': True}

    if query:
        match['$text'] = {'$search': query}

    if filters.get('category'):
        match['category'] = filters['category']

    if filters.get('min_price') is not None or filters.get('max_price') is not None:
        price_filter = {}
        if filters.get('min_price') is not None:
            price_filter['$gte'] = float(filters['min_price'])
        if filters.get('max_price') is not None:
            price_filter['$lte'] = float(filters['max_price'])
        match['price'] = price_filter

    if filters.get('size'):
        match['sizes.size'] = filters['size']

    if filters.get('color'):
        match['colors'] = filters['color']

    sort_map = {
        'price_asc': [('price', 1)],
        'price_desc': [('price', -1)],
        'rating': [('avg_rating', -1)],
        'newest': [('created_at', -1)],
    }
    sort_order = sort_map.get(sort, [('created_at', -1)])

    skip = (page - 1) * limit
    cursor = db.products.find(match).sort(sort_order).skip(skip).limit(limit)
    total = db.products.count_documents(match)
    products = list(cursor)
    return products, total


def update_product(db, product_id, data):
    data['updated_at'] = datetime.now(timezone.utc)
    result = db.products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': data}
    )
    return result.modified_count > 0


def delete_product(db, product_id):
    result = db.products.update_one(
        {'_id': ObjectId(product_id)},
        {'$set': {'is_active': False, 'updated_at': datetime.now(timezone.utc)}}
    )
    return result.modified_count > 0


def update_stock(db, product_id, size, color, quantity_change):
    db.products.update_one(
        {'_id': ObjectId(product_id), 'sizes.size': size},
        {'$inc': {'sizes.$.stock': quantity_change}}
    )


def add_review_to_product(db, product_id, review_id, rating):
    product = db.products.find_one({'_id': ObjectId(product_id)})
    if not product:
        return
    current_avg = product.get('avg_rating', 0)
    num_reviews = product.get('num_reviews', 0)
    new_avg = ((current_avg * num_reviews) + rating) / (num_reviews + 1)
    db.products.update_one(
        {'_id': ObjectId(product_id)},
        {
            '$addToSet': {'reviews': review_id},
            '$set': {
                'avg_rating': round(new_avg, 2),
                'updated_at': datetime.now(timezone.utc)
            },
            '$inc': {'num_reviews': 1}
        }
    )


def create_indexes(db):
    db.products.create_index('sku', unique=True, sparse=True)
    db.products.create_index([('name', 'text'), ('description', 'text'), ('tags', 'text')])
    db.products.create_index('category')
    db.products.create_index('is_active')
