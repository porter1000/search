from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        print("Creating virtual table if not exists...")
        db.session.execute(text('CREATE VIRTUAL TABLE IF NOT EXISTS pages USING fts5(url, title, content)'))
        db.session.commit()
        print("Virtual table created.")
