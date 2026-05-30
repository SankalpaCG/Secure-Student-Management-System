import click

from app.extensions import db
from app.seeds import DEFAULT_SEED_PASSWORD, seed_database


def register_cli_commands(app):
    @app.cli.command("seed")
    @click.option(
        "--password",
        default=None,
        help="Password for all seeded users (default: ChangeMe123!)",
    )
    def seed_command(password):
        """Seed the database with sample users, courses, and records."""
        seed_database(password=password or DEFAULT_SEED_PASSWORD)

    @app.cli.command("init-db")
    def init_db_command():
        """Create all tables (use flask db migrate/upgrade for production)."""
        db.create_all()
        click.echo("Tables created.")
