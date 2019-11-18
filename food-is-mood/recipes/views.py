from contextlib import contextmanager
from .engine import User, Engine
from sqlalchemy.orm import sessionmaker
from pyramid.response import Response
from pyramid.view import view_config, view_defaults

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

@view_config(route_name='add_user')
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

@view_config(route_name='get_users', renderer='templates/get_users.pt')
def get_users(request):
    with session_scope() as session:
        all_users = session.query(User.first_name, User.last_name).all()

    return {
        'users': all_users,
        'name': 'All Users'
    }

@view_defaults(renderer='templates/home.pt')
class TutorialViews:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='hello_world')
    def hello_world(self):
        first_name = self.request.matchdict['first_name']
        last_name = self.request.matchdict['last_name']
        return {
            'name': 'Hello View',
            'first_name': first_name,
            'last_name': last_name
        }

    @view_config(route_name='hello_world_base')
    def hello_world_base(self):
        return {
            'name': 'Hello View',
            'first_name': '',
            'last_name': ''
        }

    @view_config(route_name='home_view')
    def home_view(self):
        return {
            'name': 'Home View',
            'first_name': '',
            'last_name': ''
        }