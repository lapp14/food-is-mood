# food-is-mood

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from .engine import User, Engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

engine = Engine()
Session = sessionmaker(bind=engine.get())

@contextmanager
def session_scope():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

def add_user(request):
    first_name = request.GET.getone('first_name')
    last_name = request.GET.getone('last_name')
    user = User(first_name=first_name, last_name=last_name)

    with session_scope() as session:
        session.add(user)
        new_user = session.query(User).filter_by(first_name=first_name, last_name=last_name).first()

        if new_user is user:
            print('New user added, {new_user}'.format(new_user=new_user))

        all_users = session.query(User.first_name, User.last_name).all()

    return Response("<pre>" + "\n".join(map(str, all_users)) + "</pre>")

def get_users(request):
    with session_scope() as session:
        all_users = session.query(User.first_name, User.last_name).all()

    return Response("<pre>" + "\n".join(map(str, all_users)) + "</pre>")

def hello_world(request):
    return Response('<h1>Hello World!</h1>')

def addRoutes(config):
    config.add_route('hello_world', '/')
    config.add_view(hello_world, route_name='hello_world')
    config.add_route('add_user', '/add_user')
    config.add_view(add_user, route_name='add_user')
    config.add_route('get_users', '/get_users')
    config.add_view(get_users, route_name='get_users')

def main(global_config, **settings):
    config = Configurator(settings=settings)
    addRoutes(config)
    print('Starting server...')
    return config.make_wsgi_app()
