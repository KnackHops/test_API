import sqlite3

import click
from flask import current_app, g

def get_db():
    if 'db' not in g:
        # connects to the database
        # current_app.config['DATABASE'], tells the location of the database
        # detect_types, detects which type is the data. From text, integer, real, blob or null
        # PARSE_DECLTYPES is a constant, for multiple type. Each column of the db's declaration will be read. and declared from
        # sqlite3.Row, returns dictinary like object. think of a cursor, with callable rows. and with callable indexes
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
        
    return g.db

def init_db():
    db = get_db()
    # gets db connection, and then execute schema.sql to create db
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# command 'init-db' is registered in flask.
# this will execute init_db_command, in return would execut the actual init_db 
@click.command('init-db')
def init_db_command():
    init_db()
    click.echo("Initialized the database")
    
def close_db(e=None):
    db = g.pop('db', None)
    
    if db is not None:
        db.close()

def init_app(app):
    # executes after response is returned
    app.teardown_appcontext(close_db)
    # command line for flask
    app.cli.add_command(init_db_command)
    
