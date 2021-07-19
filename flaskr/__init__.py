import os

import click
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
    def hello_there():
        click.echo("welp, hallo!")
        
    app.cli.add_command(hello_there)
    
    from . import auth
    app.register_blueprint(auth.bp)
    
    from . import blog
    app.register_blueprint(blog.bp)
    # list bp.index as index when using url_for
    # for example in auth plain 'index' is used
    # this way, bp.index and index pertains to the '/' of blog
    app.add_url_rule('/', endpoint='index')
    return app
