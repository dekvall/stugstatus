from flask import Flask, request, abort
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json


def create_app():
    API_KEY = os.getenv("FLASK_API_KEY")
    if API_KEY is None:
        raise RuntimeError("You must set an api key with FLASK_API_KEY")

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/temps.sqlite"
    db = SQLAlchemy(app)


    class Temperature(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        timestamp = db.Column(db.TIMESTAMP, default=datetime.utcnow, nullable=False)
        temp = db.Column(db.Integer, nullable=False)

        def as_dict(self):
            return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c.name == 'id'}
    db.create_all()


    def require_apikey(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            if request.headers.get('X-Api-key') == API_KEY:
                return view_function(*args, **kwargs)
            else:
                abort(401)
        return decorated_function



    @app.route('/temp', methods=["POST"])
    @require_apikey
    def submit_temp():
        content = request.get_json()
        if content is not None:
            if content.get('temperature') is not None:
                last_temp = content.get('temperature')
                db.session.add(Temperature(temp=last_temp))
                db.session.commit()
                return f"Successfully submitted {last_temp}"
            else:
                abort(400)

    @app.route("/temp", methods=["GET"])
    def show_temp():
        result = Temperature.query.order_by(Temperature.id.desc()).first()
        return json.dumps(result.as_dict(), default=str, indent=2)


    return app

if __name__ == "__main__":
    app = create_app()

