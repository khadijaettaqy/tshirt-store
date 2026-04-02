import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { trackNavigation, setSessionId } from '../store/slices/navigationSlice';

function generateSessionId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

function getDeviceInfo() {
  const ua = navigator.userAgent;
  const uaLower = ua.toLowerCase();

  let type = 'desktop';
  if (/mobile|android|iphone/.test(uaLower)) type = 'mobile';
  else if (/ipad|tablet/.test(uaLower)) type = 'tablet';

  let browser = 'Other';
  if (/firefox/.test(uaLower)) browser = 'Firefox';
  else if (/edg/.test(uaLower)) browser = 'Edge';
  else if (/chrome/.test(uaLower)) browser = 'Chrome';
  else if (/safari/.test(uaLower)) browser = 'Safari';

  let os = 'Other';
  if (/windows/.test(uaLower)) os = 'Windows';
  else if (/mac os/.test(uaLower)) os = 'macOS';
  else if (/android/.test(uaLower)) os = 'Android';
  else if (/iphone|ipad|ios/.test(uaLower)) os = 'iOS';
  else if (/linux/.test(uaLower)) os = 'Linux';

  return { type, browser, os };
}

export default function useNavigationTracker() {
  const location = useLocation();
  const dispatch = useDispatch();
  const { currentSession } = useSelector((state) => state.navigation);

  const visitIdRef = useRef(null);
  const visitStartRef = useRef(Date.now());
  const clicksRef = useRef(0);
  const scrollsRef = useRef(0);

  // Initialize session ID
  useEffect(() => {
    let sessionId = sessionStorage.getItem('nav_session_id');
    if (!sessionId) {
      sessionId = generateSessionId();
      sessionStorage.setItem('nav_session_id', sessionId);
    }
    if (!currentSession.id) {
      dispatch(setSessionId(sessionId));
    }
  }, []);

  // Track clicks and scrolls
  useEffect(() => {
    const handleClick = () => { clicksRef.current += 1; };
    const handleScroll = () => { scrollsRef.current += 1; };
    window.addEventListener('click', handleClick);
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('click', handleClick);
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Track route changes
  useEffect(() => {
    const sessionId = sessionStorage.getItem('nav_session_id') || generateSessionId();
    const now = Date.now();
    const duration = Math.round((now - visitStartRef.current) / 1000);
    const actions = { clicks: clicksRef.current, scrolls: scrollsRef.current };

    const trackData = {
      path: location.pathname + location.search,
      session_id: sessionId,
      referrer: document.referrer || '',
      device_info: getDeviceInfo(),
      visit_id: visitIdRef.current,
      duration: visitIdRef.current ? duration : undefined,
      actions: visitIdRef.current ? actions : undefined,
    };

    // Reset counters
    clicksRef.current = 0;
    scrollsRef.current = 0;
    visitStartRef.current = now;

    dispatch(trackNavigation(trackData)).then((result) => {
      if (trackNavigation.fulfilled.match(result)) {
        visitIdRef.current = result.payload.visit_id;
      }
    });
  }, [location.pathname, location.search]);
}
