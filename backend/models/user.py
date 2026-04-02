from datetime import datetime, timezone
from bson import ObjectId
import bcrypt


def create_user(db, email, password, full_name):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = {
        'email': email.lower(),
        'password_hash': password_hash,
        'full_name': full_name,
        'avatar': '',
        'role': 'user',
        'is_verified': False,
        'verification_token': '',
        'reset_token': '',
        'reset_token_expires': None,
        'wishlist': [],
        'preferences': {},
        'created_at': datetime.now(timezone.utc),
        'updated_at': datetime.now(timezone.utc)
    }
    result = db.users.insert_one(user)
    user['_id'] = result.inserted_id
    return user


def find_user_by_email(db, email):
    return db.users.find_one({'email': email.lower()})


def find_user_by_id(db, user_id):
    try:
        return db.users.find_one({'_id': ObjectId(user_id)})
    except Exception:
        return None


def update_user(db, user_id, data):
    data['updated_at'] = datetime.now(timezone.utc)
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {'$set': data}
    )
    return result.modified_count > 0


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def add_to_wishlist(db, user_id, product_id):
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$addToSet': {'wishlist': product_id},
            '$set': {'updated_at': datetime.now(timezone.utc)}
        }
    )
    return result.modified_count > 0


def remove_from_wishlist(db, user_id, product_id):
    result = db.users.update_one(
        {'_id': ObjectId(user_id)},
        {
            '$pull': {'wishlist': product_id},
            '$set': {'updated_at': datetime.now(timezone.utc)}
        }
    )
    return result.modified_count > 0


def get_wishlist(db, user_id):
    user = find_user_by_id(db, user_id)
    if not user:
        return []
    return user.get('wishlist', [])


def create_indexes(db):
    db.users.create_index('email', unique=True)
