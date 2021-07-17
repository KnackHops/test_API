import os

import click
from flask.cli import with_appcontext
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
#    @app.route('/hello')
#    def hello():
#        return 'Hello! World!'
    
    from . import db
    db.init_app(app)
    
    @click.command('hello-there')
    @with_appcontext
    def hello_there():
        click.echo("welp, hallo!")
        
    app.cli.add_command(hello_there)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    
    return app
