from flask import Flask, request, abort, render_template
from functools import wraps
import os
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

app = Flask(__name__, static_folder="static", template_folder="template")

debug_mode = app.config["ENV"] == "development"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///temps.sqlite" if debug_mode else "sqlite:////data/temps.sqlite"

API_KEY = "test" if debug_mode else os.getenv("FLASK_API_KEY")
if API_KEY is None:
    raise RuntimeError("You must provide an api key with FLASK_API_KEY")


db = SQLAlchemy(app)

class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.TIMESTAMP, default=datetime.now, nullable=False)
    temp = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns if not c.name == 'id'}

class LivingRoomTemperature(Temperature):
    pass

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
    latest_temp = Temperature.query.order_by(Temperature.id.desc()).first()
    if latest_temp is None:
        abort(503)
    week_data = Temperature.query.filter(Temperature.timestamp > datetime.now() - timedelta(days=7)).all()
    return render_template('temperature_chart.html', latest_temp=latest_temp, history=week_data)

@app.route('/templr', methods=["POST"])
@require_apikey
def submit_living_room_temp():
    content = request.get_json()
    if content is not None:
        if content.get('temperature') is not None:
            last_temp = content.get('temperature')
            db.session.add(LivingRoomTemperature(temp=last_temp))
            db.session.commit()
            return f"Successfully submitted {last_temp}"
        else:
            abort(400)

@app.route("/templr", methods=["GET"])
def show_living_room_temp():
    latest_temp = LivingRoomTemperature.query.order_by(LivingRoomTemperature.id.desc()).first()
    if latest_temp is None:
        abort(503)
    week_data = LivingRoomTemperature.query.filter(LivingRoomTemperature.timestamp > datetime.now() - timedelta(days=7)).all()
    return render_template('temperature_chart.html', latest_temp=latest_temp, history=week_data)