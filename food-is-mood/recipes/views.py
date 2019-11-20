import logging, colander, deform.widget
from contextlib import contextmanager

from pyramid.httpexceptions import HTTPNotFound

from .engine import User, Engine
from sqlalchemy.orm import sessionmaker
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config, view_defaults

log = logging.getLogger(__name__)
engine = Engine()
Session = sessionmaker(bind=engine.get())

@contextmanager
def session_scope():
    session = Session()
    try:
        log.debug('session_scope(): trying session')
        yield session
        session.commit()
    except:
        log.error('session_scope(): rolling back session')
        session.rollback()
        raise
    finally:
        session.close()


def http_route_notfound(request):
    return HTTPNotFound()

@view_config(route_name='add_user')
def add_user(request):
    first_name = request.GET.getone('first_name')
    last_name = request.GET.getone('last_name')
    user = User(first_name=first_name, last_name=last_name)

    with session_scope() as session:
        session.add(user)
        new_user = session.query(User).filter_by(first_name=first_name, last_name=last_name).first()

        if new_user is user:
            log.debug('add_user(): New user added, {new_user}'.format(new_user=new_user))
            print('New user added, {new_user}'.format(new_user=new_user))

        all_users = session.query(User.first_name, User.last_name).all()

    return Response("<pre>" + "\n".join(map(str, all_users)) + "</pre>")

@view_config(route_name='get_users', renderer='templates/get_users.jinja2')
@view_config(route_name='get_users_json', renderer='json')
def get_users(request):
    cookie = request.session
    if 'counter' in cookie:
        cookie['counter'] += 1
    else:
        cookie['counter'] = 1

    with session_scope() as session:
        all_users = session.query(User.first_name, User.last_name).all()

    return {
        'users': all_users,
        'name': 'All Users',
        'counter': cookie['counter'],
    }

pages = {
    '100': dict(
        uid='100',
        title='Page 100',
        body='<em>100</em>',
        steps=[
            'One',
            'Two',
            'Three',
            'Four'
        ]
    ),
    '101': dict(
        uid='101',
        title='Page 101',
        body='<em>101</em>',
        steps=[
            'One',
            'Two'
        ]
    ),
    '102': dict(
        uid='102',
        title='Page 102',
        body='<em>102</em>',
        steps=[
            'One',
            'Two',
            'Three',
            'Four',
            'Five',
            'Six',
            'Seven',
            'Eight'
        ]
    )
}

class RecipePage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )

class RecipeViews(object):
    def __init__(self, request):
        self.request = request

    @property
    def recipe_form(self):
        schema = RecipePage()
        return deform.Form(schema, buttons=('submit',))

    @property
    def reqts(self):
        return self.recipe_form.get_widget_resources()

    @view_config(route_name='home_view', renderer='templates/home_view.jinja2')
    def home_view(self):
        return dict(pages=pages.values())

    @view_config(route_name='recipe_add', renderer='templates/recipe_add_edit.jinja2')
    def recipe_add(self):
        form = self.recipe_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.recipe_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            # Form is valid, make a new identifier and add to list
            last_uid = int(sorted(pages.keys())[-1])
            new_uid = str(last_uid + 1)
            pages[new_uid] = dict(
                uid=new_uid, title=appstruct['title'],
                body=appstruct['body']
            )

            # Now visit new page
            url = self.request.route_url('recipe_view', uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)

    @view_config(route_name='recipe_view', renderer='templates/recipe_view.jinja2')
    def recipe_view(self):
        uid = self.request.matchdict['uid']
        page = pages[uid]
        return dict(page=page)

    @view_config(route_name='recipe_edit', renderer='templates/recipe_add_edit.jinja2')
    def recipe_edit(self):
        uid = self.request.matchdict['uid']
        page = pages[uid]

        recipe_form = self.recipe_form

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = recipe_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(page=page, form=e.render())

            # Change the content and redirect to the view
            page['title'] = appstruct['title']
            page['body'] = appstruct['body']

            url = self.request.route_url('recipe_view', uid=page['uid'])
            return HTTPFound(url)

        form = recipe_form.render(page)

        return dict(page=page, form=form)
