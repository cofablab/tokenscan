import commands

from flask import Flask

from live import views


def create_app():
    """An application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    register_commands(app)
    register_blueprints(app)
    return app


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(views.blueprint)
    return None


app = create_app()
