from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models.navigation import (
    record_visit, update_visit_duration, get_user_history,
    get_most_visited_pages, get_user_journeys, get_session_analytics, get_device_breakdown
)
from services.navigation_service import parse_user_agent
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import exceptions as jwt_exc

navigation_bp = Blueprint('navigation', __name__)


@navigation_bp.route('/track', methods=['POST'])
def track():
    try:
        data = request.get_json() or {}
        path = data.get('path', '/')
        session_id = data.get('session_id', '')
        referrer = data.get('referrer', '')
        visit_id = data.get('visit_id')
        duration = data.get('duration')
        actions = data.get('actions', {'clicks': 0, 'scrolls': 0})
        device_info = data.get('device_info', {})

        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr or ''

        if not device_info:
            device_info = parse_user_agent(user_agent)

        # Get optional user identity
        user_id = None
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
        except Exception:
            pass

        db = current_app.db

        # If visit_id provided, update duration of previous visit
        if visit_id and duration is not None:
            next_page = path
            update_visit_duration(db, visit_id, duration, next_page, actions)

        visit = record_visit(
            db,
            session_id=session_id,
            path=path,
            user_id=user_id,
            referrer=referrer,
            user_agent=user_agent,
            ip_address=ip_address,
            device_info=device_info
        )
        return jsonify({'visit_id': str(visit['_id'])}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@navigation_bp.route('/history', methods=['GET'])
@jwt_required()
def history():
    try:
        user_id = get_jwt_identity()
        limit = int(request.args.get('limit', 50))
        db = current_app.db
        visits = get_user_history(db, user_id, limit)
        serialized = []
        for v in visits:
            v['id'] = str(v.pop('_id'))
            if v.get('user_id'):
                v['user_id'] = str(v['user_id'])
            if v.get('timestamp'):
                v['timestamp'] = v['timestamp'].isoformat()
            if v.get('created_at'):
                v['created_at'] = v['created_at'].isoformat()
            serialized.append(v)
        return jsonify({'history': serialized}), 200
    except Exception as e:
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@navigation_bp.route('/admin/analytics', methods=['GET'])
@jwt_required()
def analytics():
    try:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403

        days = int(request.args.get('days', 30))
        db = current_app.db
        most_visited = get_most_visited_pages(db, limit=20, days=days)
        user_journeys = get_user_journeys(db, limit=20)
        session_analytics = get_session_analytics(db, days=days)
        device_breakdown = get_device_breakdown(db, days=days)

        # Serialize user_journeys
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
        current_app.logger.error(f'Unexpected error in {__name__}: {e}', exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500
