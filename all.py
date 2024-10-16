# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
limiter = Limiter(key_func=get_remote_address, default_limits=["100 per day"])

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')


    db.init_app(app)
    jwt = JWTManager(app)
    cache.init_app(app)
    limiter.init_app(app)

    with app.app_context():
        from.routes import routes
        app.register_blueprint(routes)

        db.create_all() # Create tables for the first time
    
    return app

# app/config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@localhost/db_name'
    SQLALCHEMY_TRACK_MODIFICATION = False
    SECRET_KEY = 'your_secret_key' 
    JWT_SECRET_KEY = 'jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600

# app/models/customer.py
# SQLAlchemy models for Customer and CustomerAccount.
from app import db
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Coulmn(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    account = db.relationship('CustomerAccount', uselist=False, back_populates = 'customer')

class CustomerAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username =db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', back_populates='account')

# app/models/product.py

# SQLAlchemy model for product.
from app import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price= db.Column(db.Float, nullable=False)


# app/models/order.py
# SQLAlchemy model for Order with relationships to Customer and Product.
from app import db

order_products = db.Table('order_products',
db.Column('order_id', db.Integer, db.ForeignKey('order.id')),
db.Column('product_id', db.Integer, db.ForeignKey('product.id'))

)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    customer = db.relationship('Customer', backref='orders')
    products = db.relationship('Product', secondary=order_products, backref='orders')

# app/controllers/customer_controller.py
from flask import request, jsonify
from app import db
from app.modles.customer import Customer, CustomerAccount
from app.services.customer_service import create_customer, get_customer

def create_customer_controller():
    data = request.get_json()
    customer = create_customer(data['name'], data['email'], data['phone'])
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer created successfully'}), 201

def get_customer_controller(customer_id):
    customer = get_customer(customer_id)
    if customer:
        return jsonify({'name': customer.name, 'email': customer.email, 'phone': customer.phone})
    return jsonify({'message': 'Customer not found'}), 404

# app/services/customer_service.py
from app.models.customer import Customer

def create_customer(name, email, phone):
    return Customer(name=name, email=email, phone=phone)

def get_customer(customer_id):
    return Customer.query.get(customer_id)

# app/routes/routes.py
from flask import Blueprint
from app.controller.customer_controller import create_customer_controller, get_customer_controller

routes = Blueprint('routes', __name__)
    

# Customer routes
routes.route('/customers/create', methods=['POST'])(create_customer_controller)
routes.route('/customers/<int:customer_id>', methods=['GET'])(get_customer_controller)

# app/utils/auth.py
from flask_jwt_extended import create_access_token
from datetime import timedelta

def create_token(identity):
    return create_access_token(identity=identity, expires_delta=timedelta(hours=1))

# app/utils/cache.py
from app import cache

@cache.cached(timeout=300, key_prefix='all_products')
def get_all_products():
    # Simulate a database query
    pass

# app/test/test_app.py
import unittest
from app import create_app, db

class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearsDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_customer(self):
        response = self.client.post('/customers/create', json={
            'name': 'Alice Doe', 'email': 'alice@example.com', 'phone': '1234567890'
        })

        self.assertEqual(response.status_code, 201)

if __name__ == '__main__':
    unittest.main()

# run.py
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)







 


 
    
