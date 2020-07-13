# food-is-mood

from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory
from sqlalchemy import engine_from_config
from .engine import User, Engine
from .views import http_route_notfound
from .models import DBSession, Base

COOKIE_SECRET = "canyouf33litinth3airt0night?!"  # TODO: reset and remove this later


def addRoutes(config):
    config.add_route("home_view", "/")
    config.add_route("get_users_json", "/get_users.json")
    config.add_route("search_recipes", "/search_recipes/")
    config.add_route("recipe_add", "/add/")
    config.add_route("recipe_view", "/recipes/{uid}/")
    config.add_route("recipe_edit", "/recipes/{uid}/edit/")
    config.add_route("add_user", "/add_user/")
    config.add_route("get_users", "/get_users/")
    config.scan(".views")


def main(global_config, **settings):
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings, root_factory="recipes.models.Root")
    config.include("pyramid_chameleon")
    session_factory = SignedCookieSessionFactory(
        secret="COOKIE_SECRET", cookie_name="food-is-mood",
    )
    # config = Configurator(settings=settings, session_factory=session_factory)
    config.include("pyramid_jinja2")
    config.add_static_view(name="static", path="recipes:static")
    config.add_static_view("deform_static", "deform:static/")
    config.add_notfound_view(http_route_notfound, append_slash=True)
    addRoutes(config)
    print("Starting server...")
    return config.make_wsgi_app()
