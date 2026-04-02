import re
from datetime import datetime, timezone, timedelta
from models.navigation import (
    record_visit as _record_visit,
    get_most_visited_pages,
    get_user_journeys,
    get_session_analytics,
    get_device_breakdown
)


def record_navigation(db, data):
    session_id = data.get('session_id', '')
    path = data.get('path', '/')
    user_id = data.get('user_id')
    referrer = data.get('referrer', '')
    user_agent = data.get('user_agent', '')
    ip_address = data.get('ip_address', '')
    device_info = data.get('device_info') or parse_user_agent(user_agent)

    visit = _record_visit(
        db,
        session_id=session_id,
        path=path,
        user_id=user_id,
        referrer=referrer,
        user_agent=user_agent,
        ip_address=ip_address,
        device_info=device_info
    )
    return visit


def get_analytics(db, days=30):
    return {
        'most_visited_pages': get_most_visited_pages(db, days=days),
        'user_journeys': get_user_journeys(db),
        'session_analytics': get_session_analytics(db, days=days),
        'device_breakdown': get_device_breakdown(db, days=days)
    }


def anonymize_ip(ip):
    if not ip:
        return ''
    parts = ip.split('.')
    if len(parts) == 4:
        return '.'.join(parts[:3]) + '.0'
    return ip


def parse_user_agent(ua_string):
    if not ua_string:
        return {'type': 'unknown', 'browser': 'unknown', 'os': 'unknown'}

    ua = ua_string.lower()

    # Device type
    if any(x in ua for x in ['mobile', 'android', 'iphone', 'ipad']):
        device_type = 'mobile' if 'ipad' not in ua else 'tablet'
    elif 'tablet' in ua:
        device_type = 'tablet'
    else:
        device_type = 'desktop'

    # Browser
    if 'firefox' in ua:
        browser = 'Firefox'
    elif 'edg' in ua:
        browser = 'Edge'
    elif 'chrome' in ua:
        browser = 'Chrome'
    elif 'safari' in ua:
        browser = 'Safari'
    elif 'opera' in ua or 'opr' in ua:
        browser = 'Opera'
    else:
        browser = 'Other'

    # OS
    if 'windows' in ua:
        os_name = 'Windows'
    elif 'mac os' in ua or 'macos' in ua:
        os_name = 'macOS'
    elif 'android' in ua:
        os_name = 'Android'
    elif 'iphone' in ua or 'ipad' in ua or 'ios' in ua:
        os_name = 'iOS'
    elif 'linux' in ua:
        os_name = 'Linux'
    else:
        os_name = 'Other'

    return {'type': device_type, 'browser': browser, 'os': os_name}
