import os
from flask import Flask
from .models import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Renderが提供するPostgreSQLのURLを取得（なければSQLite）
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        # SQLAlchemyの仕様に合わせるための文字列置換
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    else:
        database_url = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')

    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key-for-action-os'),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        from . import routes

    return app