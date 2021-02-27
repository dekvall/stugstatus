from flask import Flask, request, abort
from functools import wraps
import os

def create_app():
    def require_apikey(view_function):
        @wraps(view_function)
        def decorated_function(*args, **kwargs):
            if request.headers.get('X-Api-key') == API_KEY:
                return view_function(*args, **kwargs)
            else:
                abort(401)
        return decorated_function

    API_KEY = os.getenv("FLASK_API_KEY")
    if API_KEY is None:
        raise RuntimeError("You must set an api key with FLASK_API_KEY")
    app = Flask(__name__)

    @app.route('/temp', methods=["GET","POST"])
    @require_apikey
    def temp():
        if request.method == "POST":
            return submit_temp()
        elif request.method == "GET":
            return "No info"

    def submit_temp():
        content = request.get_json()
        if content is not None:
            if content.get('temperature') is not None:
                last_temp = content.get('temperature')
                return f"Successfully submitted {last_temp}"
            else:
                abort(400)
    return app

if __name__ == "__main__":
    app = create_app()

