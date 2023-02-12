from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from flask_migrate import Migrate

import authentification
from connect_db import db

app = Flask(__name__)

app.register_blueprint(authentification.bp)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_test.db'
app.config['SECRET_KEY'] = "test"
db.init_app(app)

Migrate(app,db)

if __name__ == "__main__":
    app.run(debug=True)

