from flask import g, current_app
import analyticsdb.database as db
'''
This module provides a few helper functions for using a
database handle for the request context, "g".
'''


def get_db() -> db.Database:
    """Add database connection to the request object, `g`."""
    if 'db' not in g:
        # Create database if not exists
        g.db = db.Database(current_app.config['DATABASE_PATH'])

    return g.db


def close_db(e=None):
    """Close the database connection attached to the request object, `g`."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db(schemapath: str):
    """Initialize the database instance."""
    db = get_db()
    with open(schemapath) as f:
        db.execute_script(f.read())
