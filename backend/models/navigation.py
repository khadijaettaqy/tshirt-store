from datetime import datetime, timezone, timedelta
from bson import ObjectId


def record_visit(db, session_id, path, user_id=None, referrer='', user_agent='', ip_address='', device_info=None):
    visit = {
        'user_id': ObjectId(user_id) if user_id else None,
        'session_id': session_id,
        'path': path,
        'timestamp': datetime.now(timezone.utc),
        'duration': 0,
        'referrer': referrer,
        'next_page': '',
        'user_agent': user_agent,
        'ip_address': _anonymize_ip(ip_address),
        'actions': {'clicks': 0, 'scrolls': 0},
        'device_info': device_info or {'type': 'unknown', 'browser': 'unknown', 'os': 'unknown'},
        'created_at': datetime.now(timezone.utc)
    }
    result = db.navigation_history.insert_one(visit)
    visit['_id'] = result.inserted_id
    return visit


def update_visit_duration(db, visit_id, duration, next_page='', actions=None):
    try:
        update_data = {
            'duration': duration,
            'next_page': next_page,
        }
        if actions:
            update_data['actions'] = actions
        db.navigation_history.update_one(
            {'_id': ObjectId(visit_id)},
            {'$set': update_data}
        )
        return True
    except Exception:
        return False


def get_user_history(db, user_id, limit=50):
    cursor = db.navigation_history.find(
        {'user_id': ObjectId(user_id)}
    ).sort('timestamp', -1).limit(limit)
    return list(cursor)


def get_session_history(db, session_id):
    cursor = db.navigation_history.find(
        {'session_id': session_id}
    ).sort('timestamp', 1)
    return list(cursor)


def get_most_visited_pages(db, limit=10, days=30):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    pipeline = [
        {'$match': {'timestamp': {'$gte': since}}},
        {'$group': {'_id': '$path', 'count': {'$sum': 1}, 'avg_duration': {'$avg': '$duration'}}},
        {'$sort': {'count': -1}},
        {'$limit': limit},
        {'$project': {'path': '$_id', 'count': 1, 'avg_duration': {'$round': ['$avg_duration', 1]}, '_id': 0}}
    ]
    return list(db.navigation_history.aggregate(pipeline))


def get_user_journeys(db, limit=20):
    pipeline = [
        {'$match': {'user_id': {'$ne': None}}},
        {'$sort': {'session_id': 1, 'timestamp': 1}},
        {
            '$group': {
                '_id': '$session_id',
                'user_id': {'$first': '$user_id'},
                'pages': {'$push': '$path'},
                'start_time': {'$first': '$timestamp'},
                'end_time': {'$last': '$timestamp'},
                'page_count': {'$sum': 1}
            }
        },
        {'$sort': {'start_time': -1}},
        {'$limit': limit}
    ]
    return list(db.navigation_history.aggregate(pipeline))


def get_session_analytics(db, days=30):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    pipeline = [
        {'$match': {'timestamp': {'$gte': since}}},
        {
            '$group': {
                '_id': '$session_id',
                'page_views': {'$sum': 1},
                'total_duration': {'$sum': '$duration'},
                'user_id': {'$first': '$user_id'}
            }
        },
        {
            '$group': {
                '_id': None,
                'total_sessions': {'$sum': 1},
                'avg_pages_per_session': {'$avg': '$page_views'},
                'avg_session_duration': {'$avg': '$total_duration'},
                'authenticated_sessions': {'$sum': {'$cond': [{'$ne': ['$user_id', None]}, 1, 0]}}
            }
        }
    ]
    result = list(db.navigation_history.aggregate(pipeline))
    return result[0] if result else {}


def get_device_breakdown(db, days=30):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    pipeline = [
        {'$match': {'timestamp': {'$gte': since}}},
        {'$group': {'_id': '$device_info.type', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    return list(db.navigation_history.aggregate(pipeline))


def _anonymize_ip(ip):
    if not ip:
        return ''
    parts = ip.split('.')
    if len(parts) == 4:
        return '.'.join(parts[:3]) + '.0'
    return ip


def create_indexes(db):
    db.navigation_history.create_index('session_id')
    db.navigation_history.create_index('user_id')
    db.navigation_history.create_index('path')
    db.navigation_history.create_index('timestamp')
