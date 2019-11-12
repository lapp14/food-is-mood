from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from engine import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

engine = create_engine('sqlite:///tmp/test.db', echo=True)
Session = sessionmaker(bind=engine)

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

# https://trypyramid.com
def hello_world(request):
    return Response('Hello World!')

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

def addRoutes():
    config.add_route('hello', '/')
    config.add_view(hello_world, route_name='hello')
    config.add_route('add_user', '/add_user')
    config.add_view(add_user, route_name='add_user')
    config.add_route('get_users', '/get_users')
    config.add_view(get_users, route_name='get_users')

if __name__ == '__main__':
    with Configurator() as config:
        addRoutes()
        app = config.make_wsgi_app()
    print('Starting server...')
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()

