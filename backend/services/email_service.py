import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

logger = logging.getLogger(__name__)


def _send_email(to_email, subject, html_body):
    mail_server = os.getenv('MAIL_SERVER', '')
    mail_port = int(os.getenv('MAIL_PORT', 587))
    mail_username = os.getenv('MAIL_USERNAME', '')
    mail_password = os.getenv('MAIL_PASSWORD', '')

    if not mail_server or not mail_username:
        logger.info(f'Email not configured. Would send to {to_email}: {subject}')
        return False

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = mail_username
        msg['To'] = to_email
        part = MIMEText(html_body, 'html')
        msg.attach(part)

        with smtplib.SMTP(mail_server, mail_port) as server:
            server.ehlo()
            server.starttls()
            server.login(mail_username, mail_password)
            server.sendmail(mail_username, to_email, msg.as_string())
        return True
    except Exception as e:
        logger.error(f'Failed to send email to {to_email}: {e}')
        return False


def send_verification_email(email, token, frontend_url):
    link = f'{frontend_url}/verify-email?token={token}'
    html = f"""
    <h2>Verify Your Email</h2>
    <p>Thank you for registering! Please click the link below to verify your email address:</p>
    <a href="{link}">Verify Email</a>
    <p>This link will expire in 24 hours.</p>
    """
    return _send_email(email, 'Verify Your T-Shirt Store Account', html)


def send_password_reset_email(email, token, frontend_url):
    link = f'{frontend_url}/reset-password?token={token}'
    html = f"""
    <h2>Reset Your Password</h2>
    <p>You requested a password reset. Click the link below:</p>
    <a href="{link}">Reset Password</a>
    <p>This link will expire in 1 hour. If you did not request this, ignore this email.</p>
    """
    return _send_email(email, 'Reset Your T-Shirt Store Password', html)


def send_order_confirmation_email(email, order):
    order_id = str(order.get('id') or order.get('_id', ''))
    total = order.get('total_amount', 0)
    items = order.get('items', [])
    items_html = ''.join(
        f'<tr><td>{item.get("name")}</td><td>{item.get("size")}</td><td>{item.get("color")}</td><td>{item.get("quantity")}</td><td>${item.get("price", 0):.2f}</td></tr>'
        for item in items
    )
    html = f"""
    <h2>Order Confirmation</h2>
    <p>Thank you for your order!</p>
    <p><strong>Order ID:</strong> {order_id}</p>
    <table border="1">
        <tr><th>Product</th><th>Size</th><th>Color</th><th>Qty</th><th>Price</th></tr>
        {items_html}
    </table>
    <p><strong>Total: ${total:.2f}</strong></p>
    """
    return _send_email(email, f'Order Confirmation #{order_id}', html)
