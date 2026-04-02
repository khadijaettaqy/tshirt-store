import stripe
import os
import logging

logger = logging.getLogger(__name__)


def _get_stripe():
    key = os.getenv('STRIPE_SECRET_KEY', '')
    if not key:
        logger.warning('STRIPE_SECRET_KEY not configured')
        return None
    stripe.api_key = key
    return stripe


def create_payment_intent(amount, currency='usd', metadata=None):
    s = _get_stripe()
    if not s:
        return None
    try:
        intent = s.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata=metadata or {},
            automatic_payment_methods={'enabled': True}
        )
        return {'id': intent.id, 'client_secret': intent.client_secret}
    except Exception as e:
        logger.error(f'Stripe create_payment_intent error: {e}')
        raise


def confirm_payment(payment_intent_id):
    s = _get_stripe()
    if not s:
        return None
    try:
        intent = s.PaymentIntent.retrieve(payment_intent_id)
        return {'status': intent.status, 'id': intent.id}
    except Exception as e:
        logger.error(f'Stripe confirm_payment error: {e}')
        raise


def create_refund(payment_intent_id, amount=None):
    s = _get_stripe()
    if not s:
        return None
    try:
        params = {'payment_intent': payment_intent_id}
        if amount:
            params['amount'] = amount
        refund = s.Refund.create(**params)
        return {'id': refund.id, 'status': refund.status}
    except Exception as e:
        logger.error(f'Stripe create_refund error: {e}')
        raise
