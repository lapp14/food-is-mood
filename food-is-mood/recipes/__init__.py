# food-is-mood

from pyramid.config import Configurator
from .engine import User, Engine
from sqlalchemy.orm import sessionmaker

engine = Engine()
Session = sessionmaker(bind=engine.get())

def addRoutes(config):
    config.add_route('hello_world', '/hello/{first_name}/{last_name}/')
    config.add_route('hello_world_base', '/hello/')
    config.add_route('home_view', '/')
    config.add_route('add_user', '/add_user/')
    config.add_route('get_users', '/get_users/')
    config.add_route('get_users_json', '/get_users.json')
    config.scan('.views')

def main(global_config, **settings):
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view(name='static', path='recipes:static')
    addRoutes(config)
    print('Starting server...')
    return config.make_wsgi_app()
