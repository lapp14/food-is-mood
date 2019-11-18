# food-is-mood

from pyramid.config import Configurator
from .engine import User, Engine
from sqlalchemy.orm import sessionmaker

engine = Engine()
Session = sessionmaker(bind=engine.get())

def addRoutes(config):
    config.add_route('hello_world', '/hello')
    config.add_route('home_view', '/')
    config.add_route('add_user', '/add_user')
    config.add_route('get_users', '/get_users')
    config.scan('.views')

def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    addRoutes(config)
    print('Starting server...')
    return config.make_wsgi_app()
