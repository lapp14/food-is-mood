import logging, deform.widget
from contextlib import contextmanager

from pyramid.httpexceptions import HTTPNotFound

from recipes.schema import RecipePage
from .engine import User, Engine
from .models import DBSession, Recipe, RecipeStep, RecipeIngredient
from sqlalchemy.orm import sessionmaker
from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

log = logging.getLogger(__name__)
engine = Engine()
Session = sessionmaker(bind=engine.get())


@contextmanager
def session_scope():
    session = Session()
    try:
        log.debug("session_scope(): trying session")
        yield session
        session.commit()
    except:
        log.error("session_scope(): rolling back session")
        session.rollback()
        raise
    finally:
        session.close()


def http_route_notfound(request):
    return HTTPNotFound()


@view_config(route_name="add_user")
def add_user(request):
    first_name = request.GET.getone("first_name")
    last_name = request.GET.getone("last_name")
    user = User(first_name=first_name, last_name=last_name)

    with session_scope() as session:
        session.add(user)
        new_user = (
            session.query(User)
            .filter_by(first_name=first_name, last_name=last_name)
            .first()
        )

        if new_user is user:
            log.debug(
                "add_user(): New user added, {new_user}".format(new_user=new_user)
            )
            print("New user added, {new_user}".format(new_user=new_user))

        all_users = session.query(User.first_name, User.last_name).all()

    return Response("<pre>" + "\n".join(map(str, all_users)) + "</pre>")


@view_config(route_name="get_users", renderer="templates/get_users.jinja2")
@view_config(route_name="get_users_json", renderer="json")
def get_users(request):
    cookie = request.session
    if "counter" in cookie:
        cookie["counter"] += 1
    else:
        cookie["counter"] = 1

    with session_scope() as session:
        all_users = session.query(User.first_name, User.last_name).all()

    return {"users": all_users, "name": "All Users", "counter": cookie["counter"]}


class RecipeViews(object):
    def __init__(self, request):
        self.request = request

    @property
    def recipe_form(self):
        schema = RecipePage()
        return deform.Form(schema, buttons=("submit",))

    @property
    def reqts(self):
        return self.recipe_form.get_widget_resources()

    @view_config(route_name="home_view", renderer="templates/home_view.jinja2")
    def home_view(self):
        recipes = DBSession.query(Recipe).order_by(Recipe.title)
        return dict(title="Home View", pages=recipes)

    @view_config(route_name="recipe_add", renderer="templates/recipe_add_edit.jinja2")
    def recipe_add(self):
        form = self.recipe_form.render()

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.recipe_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            new_title = appstruct["title"]
            new_body = appstruct["description"]
            DBSession.add(Recipe(title=new_title, description=new_body))

            page = DBSession.query(Recipe).filter_by(title=new_title).one()
            new_uid = page.uid

            # Now visit new page
            url = self.request.route_url("recipe_view", uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)

    @view_config(route_name="recipe_view", renderer="templates/recipe_view.jinja2")
    def recipe_view(self):
        uid = int(self.request.matchdict["uid"])
        recipe = DBSession.query(Recipe).filter_by(uid=uid).one()
        return dict(page=recipe)

    @view_config(route_name="recipe_edit", renderer="templates/recipe_add_edit.jinja2")
    def recipe_edit(self):
        uid = int(self.request.matchdict["uid"])
        recipe = DBSession.query(Recipe).filter_by(uid=uid).one()

        recipe_form = self.recipe_form

        if "submit" in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = recipe_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(page=recipe, form=e.render())

            # Change the content and redirect to the view
            recipe["title"] = appstruct["title"]
            recipe["description"] = appstruct["description"]

            recipe.ingredients.clear()
            for ingredient in appstruct["ingredients"]:
                recipe.ingredients.append(
                    RecipeIngredient(
                        ingredient=ingredient["ingredient"],
                        shopping_list=ingredient["shopping_list"],
                    )
                )

            recipe.steps.clear()
            for index, step in enumerate(appstruct["steps"]):
                recipe.steps.append(RecipeStep(rank=index, step=step["step"]))

            # recipe.tags.clear()
            # for tag in appstruct['tags']:
            #    recipe.tags.append(RecipeTag)

            recipe["rank"] = int(appstruct["rank"])
            url = self.request.route_url("recipe_view", uid=uid)
            return HTTPFound(url)

        appstruct = {
            "title": recipe.title,
            "description": recipe.description,
            "steps": [{"step": step.step} for step in recipe.steps],
            "ingredients": [
                {
                    "ingredient": ingredient.ingredient,
                    "shopping_list": ingredient.shopping_list,
                }
                for ingredient in recipe.ingredients
            ],
            # 'tags': [tag.tag for tag in recipe.tags],
        }

        if recipe.rank:
            appstruct["rank"] = recipe.rank

        form = recipe_form.render(appstruct)

        return dict(recipe=recipe, form=form)
