import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from TranSoft.configs_local import PRODUCTION, DATABASE_PASSWORD, APP_SECRET_KEY, get_node

# create extensions instances
db = SQLAlchemy()  # create a SQLAlchemy object to handle database operations
migrate = Migrate()  # create a Migrate object to handle database migrations
from TranSoft import events  # import the events module from the TranSoft package

NODE = get_node()

SERVER_NAME = f"{NODE['ip']}:{NODE['port']}"


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)  # create a Flask app object with relative instance path
    app.config.from_mapping(
        SECRET_KEY=APP_SECRET_KEY,  # set the secret key for the app
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(app.instance_path, 'TranSoft.sqlite'),
        # set the database URI for the app
    )
    app.config["SERVER_NAME"] = SERVER_NAME
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)  # load the config file from the instance folder
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)  # load the test config from the argument

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)  # create the instance folder if it does not exist
    except OSError:
        pass  # ignore the error if it already exists
    # initialize extensions
    db.init_app(app)  # initialize the SQLAlchemy object with the app
    migrate.init_app(app, db)  # initialize the Migrate object with the app and the database
    from . import auth  # import the auth module from the current package
    app.register_blueprint(auth.bp)  # register the auth blueprint with the app
    from . import reading  # import the reading module from the current package
    app.register_blueprint(reading.bp)  # register the reading blueprint with the app
    app.add_url_rule('/', endpoint='index')  # add a URL rule for the index endpoint of the app

    # define error handlers
    @app.errorhandler(404)
    def page_not_found(error):
        return 'Page not found', 404  # return a custom message and status code for 404 errors

    # import the TransmitterIntegrityCheck class from the integrity_check module in the background_processes package
    from TranSoft.background_processes.integrity_check import TransmitterIntegrityCheck
    # create an instance of the TransmitterIntegrityCheck class
    transmitter_integrity_check_thread = TransmitterIntegrityCheck()
    transmitter_integrity_check_thread.start()  # start the thread that runs the integrity check logic

    # import the HandleNonTransmittedReadings class from the non_transmitted module in the background_processes package
    from TranSoft.background_processes.non_transmitted import HandleNonTransmittedReadings
    # create an instance of the HandleNonTransmittedReadings class
    handle_non_transmitted_readings_thread = HandleNonTransmittedReadings()
    handle_non_transmitted_readings_thread.start()  # start the thread that runs the non-transmitted readings logic

    return app  # return the app object
