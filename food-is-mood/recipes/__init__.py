# food-is-mood

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy.orm import sessionmaker
from .engine import User, Engine
from .views import http_route_notfound

COOKIE_SECRET = 'canyouf33litinth3airt0night?!'  # TODO: reset and remove this later
engine = Engine()
Session = sessionmaker(bind=engine.get())

def addRoutes(config):
    config.add_route('home_view', '/')
    config.add_route('recipe_add', '/add/')
    config.add_route('recipe_view', '/{uid}/')
    config.add_route('recipe_edit', '/{uid}/edit/')
    config.add_route('add_user', '/add_user/')
    config.add_route('get_users', '/get_users/')
    config.add_route('get_users_json', '/get_users.json')
    config.scan('.views')

def main(global_config, **settings):
    session_factory = SignedCookieSessionFactory(
        secret='COOKIE_SECRET',
        cookie_name='food-is-mood',
    )
    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_jinja2')
    config.add_static_view(name='static', path='recipes:static')
    config.add_static_view('deform_static', 'deform:static/')
    config.add_notfound_view(http_route_notfound, append_slash=True)
    addRoutes(config)
    print('Starting server...')
    return config.make_wsgi_app()
