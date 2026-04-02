from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from pymongo import MongoClient
from config import Config

jwt = JWTManager()
# Simple in-memory JWT blocklist (use Redis in production)
jwt_blocklist = set()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    # Initialize extensions
    CORS(app, origins=[app.config['FRONTEND_URL'], 'http://localhost:3000'], supports_credentials=True)
    jwt.init_app(app)

    # MongoDB
    client = MongoClient(app.config['MONGODB_URI'])
    app.db = client.get_default_database()

    # JWT blocklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return jti in jwt_blocklist

    # Create indexes
    from models.user import create_indexes as user_indexes
    from models.product import create_indexes as product_indexes
    from models.order import create_indexes as order_indexes
    from models.cart import create_indexes as cart_indexes
    from models.navigation import create_indexes as nav_indexes
    from models.review import create_indexes as review_indexes
    user_indexes(app.db)
    product_indexes(app.db)
    order_indexes(app.db)
    cart_indexes(app.db)
    nav_indexes(app.db)
    review_indexes(app.db)

    # Register blueprints
    from routes.auth import auth_bp
    from routes.products import products_bp
    from routes.cart import cart_bp
    from routes.orders import orders_bp
    from routes.navigation import navigation_bp
    from routes.users import users_bp
    from routes.reviews import reviews_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(products_bp, url_prefix='/api/products')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(navigation_bp, url_prefix='/api/navigation')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)
