import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from concurrent.futures import ThreadPoolExecutor
import atexit
from flask_migrate import Migrate
import threading

# create extensions instances
db = SQLAlchemy()
migrate = Migrate()
executor = ThreadPoolExecutor(1)

from TranSoft import events


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'TranSoft.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import reading
    app.register_blueprint(reading.bp)
    app.add_url_rule('/', endpoint='index')

    # define error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return 'Page not found', 404

    from TranSoft.background_processes.integrity_check import TransmitterIntegrityCheck
    transmitter_integrity_check_thread = TransmitterIntegrityCheck()
    transmitter_integrity_check_thread.start()

    from TranSoft.background_processes.non_transmitted import HandleNonTransmittedReadings
    handle_non_transmitted_readings_thread = HandleNonTransmittedReadings()
    handle_non_transmitted_readings_thread.start()

    return app

