from flask import Flask
from config import DB_CONFIG
from models.grade import db
from controllers.grade_controller import grade_bp

def create_app():
    app = Flask(__name__)
    app.config.update(DB_CONFIG)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(grade_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
