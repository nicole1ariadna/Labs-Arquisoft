import os

DB_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': os.getenv('DATABASE_URL', 'sqlite:///grades.db'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
}
