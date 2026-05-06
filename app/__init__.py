from flask import Flask
import os
from dotenv import load_dotenv

from app.config import load_config


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__, static_folder="../static", static_url_path="/static")
    load_config(app)
    app.config["DATABASE"] = os.path.join(os.getcwd(), "store.db")
    app.config["MEDIA_DIR"] = os.path.join(os.getcwd(), "media")
    if test_config:
        app.config.update(test_config)

    with app.app_context():
        from . import db
        from . import seed

        db.init_app(app)
        seed.seed_products()

    from . import routes

    app.register_blueprint(routes.bp)

    return app
