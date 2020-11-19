import os, sys, transaction
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from .models import DBSession, Recipe, Base, RecipeStep, RecipeIngredient


def usage(argv):
    cmd = os.path.basename(argv[0])
    print("usage: %s <config_uri>\n" '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, "sqlalchemy.")
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        model = Recipe(title="Root", description="<p>Root</p>")
        model.steps.append(RecipeStep(rank=1, step="wash vegetables"))
        model.steps.append(RecipeStep(rank=2, step="boil water"))
        model.ingredients.append(RecipeIngredient(ingredient="Broccoli", shopping_list=True))
        model.ingredients.append(RecipeIngredient(ingredient="Carrots (2)", shopping_list=True))
        model.ingredients.append(
            RecipeIngredient(ingredient="Pasta Sauce (1 jar)", shopping_list=True)
        )
        DBSession.add(model)
