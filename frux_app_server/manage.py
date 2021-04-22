"""Add db subcommand for flask migrate."""

from flask_migrate import MigrateCommand
from flask_script import Command, Manager
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from frux_app_server.app import create_app


class CreateDB(Command):
    """create database if not exists."""

    def __init__(self, flask_app):
        """Create command."""
        self.db_uri = flask_app.config['SQLALCHEMY_DATABASE_URI']
        super().__init__()

    def run(self):  # pylint: disable=method-hidden
        """Execute migrate command."""
        if not database_exists(self.db_uri):
            create_database(self.db_uri)


class DropDB(Command):
    """drop database if exists."""

    def __init__(self, flask_app):
        """Create command."""
        self.db_uri = flask_app.config['SQLALCHEMY_DATABASE_URI']
        super().__init__()

    def run(self):  # pylint: disable=method-hidden
        """Execute migrate command."""
        if database_exists(self.db_uri):
            drop_database(self.db_uri)


def main():
    """Entrypoint for main."""
    app = create_app()
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.add_command('db_create', CreateDB(app))
    manager.add_command('db_drop', DropDB(app))
    manager.run()


if __name__ == '__main__':
    main()
