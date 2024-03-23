from flask import Flask
from .routes import configure_routes

# def create_app():
#     app = Flask(__name__, template_folder='templates', static_folder='static')
#     app.config['UPLOAD_FOLDER'] = 'uploads/'
#     configure_routes(app)
#     return app

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config['UPLOAD_FOLDER'] = 'uploads/'
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set a secret key for session management
    configure_routes(app)
    return app
