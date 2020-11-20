import colander, logging, deform.widget, json, os
import pyramid.httpexceptions as exc
from contextlib import contextmanager

from pyramid.httpexceptions import HTTPNotFound

from recipes.schema import RecipePage, RecipeImageUploadPage, RecipeTagsPage
from sqlalchemy.orm.exc import NoResultFound

from .engine import User, Engine
from .images import upload_image, delete_image
from .models import DBSession, Recipe, RecipeStep, RecipeIngredient, Tag, RecipeTag
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
        new_user = session.query(User).filter_by(first_name=first_name, last_name=last_name).first()

        if new_user is user:
            log.debug("add_user(): New user added, {new_user}".format(new_user=new_user))
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
    SEARCH_LIMIT = 20

    def __init__(self, request):
        self.request = request

    def add_recipe_ingredients(self, recipe, ingredients):
        recipe.ingredients.clear()
        for ingredient in ingredients:
            recipe.ingredients.append(
                RecipeIngredient(
                    ingredient=ingredient["ingredient"], shopping_list=ingredient["shopping_list"],
                )
            )

    def add_recipe_image(self, recipe, image):
        if image is None:
            print(">> No image to upload")
            return

        if image["filename"] == recipe.image_path:
            print(">> Not changing existing image")
            return

        if recipe.image_path:
            delete_image(recipe.image_path)

        image_path = upload_image(image)
        recipe.image_path = image_path

    def add_recipe_steps(self, recipe, steps):
        recipe.steps.clear()
        for index, step in enumerate(steps):
            recipe.steps.append(RecipeStep(rank=index, step=step["step"]))

    def add_recipe_tags(self, recipe, tags):
        recipe.tags.clear()
        for tag in tags:
            new_tag = self.add_or_get_tag(tag)
            recipe.tags.append(RecipeTag(recipe_id=recipe.uid, tag_id=new_tag.uid))

    def add_or_get_tag(self, tag_label):
        try:
            result = DBSession.query(Tag).filter_by(tag=tag_label).one()
            print("Tag found, returning tag " + result.tag)
        except NoResultFound:
            result = Tag(tag=tag_label)
            print("Creating new tag: " + tag_label)
            DBSession.add(result)
            DBSession.flush()

        return result

    def get_recipe_image_url(self, recipe):
        if recipe.image_path:
            return os.path.join(os.environ["AWS_S3_BASE_URL"], recipe.image_path)

    def get_recipe_tags(self, recipe):
        result = (
            DBSession.query(RecipeTag, Tag)
            .filter(RecipeTag.recipe_id == recipe.uid)
            .filter(RecipeTag.tag_id == Tag.uid)
            .all()
        )
        return [tuple[1] for tuple in result]

    def jsonify_recipe_search(self, recipes):
        return json.dumps([dict(title=r.title, uid=r.uid) for r in recipes.all()])

    @property
    def recipe_form(self):
        return deform.Form(schema=RecipePage(), buttons=("submit",))

    def recipe_image_form(self, image_path):
        schema = RecipeImageUploadPage()

        if image_path:
            return deform.Form(
                schema, buttons=("upload new image", "keep existing image", "delete image",)
            )

        return deform.Form(schema, buttons=("upload image", "skip",))

    @property
    def reqts(self):
        return self.recipe_form.get_widget_resources()

    @view_config(route_name="home_view", renderer="templates/home_view.jinja2")
    def home_view(self):
        recipes = DBSession.query(Recipe).order_by(Recipe.title)
        links = [{"title": "Add a Recipe", "route_name": "recipe_add"}]
        return dict(title="Home View", pages=recipes, links=links)

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
            new_rank = int(appstruct["rank"])
            recipe = Recipe(title=new_title, description=new_body, rank=new_rank)
            DBSession.add(recipe)

            self.add_recipe_ingredients(recipe, appstruct["ingredients"])
            self.add_recipe_steps(recipe, appstruct["steps"])
            self.add_recipe_tags(recipe, appstruct["tags"])

            page = DBSession.query(Recipe).filter_by(title=new_title).one()
            new_uid = page.uid

            url = self.request.route_url("recipe_edit_tags", uid=new_uid)
            return HTTPFound(url)

        return dict(form=form, page="add")

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

            self.add_recipe_ingredients(recipe, appstruct["ingredients"])
            self.add_recipe_steps(recipe, appstruct["steps"])

            recipe["rank"] = int(appstruct["rank"])
            url = self.request.route_url("recipe_edit_tags", uid=uid)
            return HTTPFound(url)

        appstruct = {
            "title": recipe.title,
            "description": recipe.description,
            "steps": [{"step": step.step} for step in recipe.steps],
            "ingredients": [
                {"ingredient": ingredient.ingredient, "shopping_list": ingredient.shopping_list,}
                for ingredient in recipe.ingredients
            ],
            "tags": [{"tag": tag.tag} for tag in self.get_recipe_tags(recipe)],
        }

        if recipe.rank:
            appstruct["rank"] = recipe.rank

        form = recipe_form.render(appstruct)

        return dict(recipe=recipe, form=form, page="edit", uid=uid)

    @view_config(route_name="recipe_edit_image", renderer="templates/recipe_edit_image.jinja2")
    def recipe_edit_image(self):
        uid = int(self.request.matchdict["uid"])
        recipe = DBSession.query(Recipe).filter_by(uid=uid).one()

        if "upload_new_image" in self.request.params or "upload_image" in self.request.params:
            print("UPLOAD NEW IMAGE")
            controls = self.request.POST.items()
            try:
                appstruct = recipe_image_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(recipe=recipe, form=e.render())

            self.add_recipe_image(recipe, appstruct["image"])
            url = self.request.route_url("recipe_view", uid=uid)
            return HTTPFound(url)

        if "keep_existing_image" in self.request.params or "skip" in self.request.params:
            print("KEEP IMAGE")
            url = self.request.route_url("recipe_view", uid=uid)
            return HTTPFound(url)

        if "delete_image" in self.request.params:
            print("DELETE IMAGE")
            if recipe.image_path:
                delete_image(recipe.image_path)
                recipe.image_path = None

            url = self.request.route_url("recipe_view", uid=uid)
            return HTTPFound(url)
        
        recipe_image_form = self.recipe_image_form(recipe.image_path)

        form = recipe_image_form.render()

        image = self.get_recipe_image_url(recipe)
        question = "Would you like to edit the image?" if recipe.image_path else "Would you like to add an image?"
        template_data = dict(form=form, recipe=recipe, question=question, page="image", uid=uid)
        
        if image:
            template_data["image"] = image

        return template_data

    @view_config(route_name="recipe_edit_tags", renderer="templates/recipe_edit_tags.jinja2")
    def recipe_edit_tags(self):
        uid = int(self.request.matchdict["uid"])
        recipe = DBSession.query(Recipe).filter_by(uid=uid).one()

        if "tags_json" in self.request.POST:
            tags = RecipeTagsPage().validate(tags_json=self.request.POST['tags_json'])
            self.add_recipe_tags(recipe, tags)
            url = self.request.route_url("recipe_edit_image", uid=uid)
            return HTTPFound(url)
        
        tags = self.get_recipe_tags(recipe)       
        question = "Add some tags to your recipe!" if tags else "Would you like to edit the recipe tags?"
        template_data = dict(recipe=recipe, tags=tags, question=question, page="tags", uid=uid, max_tags=RecipeTagsPage.MAX_ALLOWED_TAGS)   

        return template_data

    @view_config(route_name="recipe_view", renderer="templates/recipe_view.jinja2")
    def recipe_view(self):
        uid = int(self.request.matchdict["uid"])
        recipe = DBSession.query(Recipe).filter_by(uid=uid).one()
        links = [
            {"title": "Edit This", "route_name": "recipe_edit", "uid": uid},
            {"title": "Add a Recipe", "route_name": "recipe_add"},
        ]
        tags = self.get_recipe_tags(recipe)
        image = self.get_recipe_image_url(recipe)
        recipe_item = dict(recipe=recipe, tags=tags)

        if image:
            print(">> Serving image: {}".format(image))
            recipe_item["image"] = image

        return dict(item=recipe_item, links=links)

    @view_config(route_name="search_recipes", renderer="templates/recipe_search.jinja2")
    def search_recipes(self):
        title = self.request.json_body.get("title", "").strip()
        recipes = (
            DBSession.query(Recipe)
            .filter(Recipe.title.contains(title))
            .order_by(Recipe.title)
            .limit(self.SEARCH_LIMIT)
        )

        if recipes.count() <= 0:
            return dict()

        recipes = [
            {"recipe": recipe, "image": self.get_recipe_image_url(recipe), "tag_names": self.get_recipe_tags(recipe)} for recipe in recipes
        ]
        return dict(recipes=recipes)

    @view_config(route_name="search_tags", renderer="templates/tag_search.jinja2")
    def search_tags(self):
        tag_name = self.request.json_body.get("title", "").strip()
        selected_tags = self.request.json_body.get("selectedTags", [])

        if not isinstance(selected_tags, list):
            raise exc.HTTPBadRequest('Parameter selected_tags is not valid')

        if not tag_name:
            return dict()

        tags = (
            DBSession.query(Tag)
            .filter(Tag.tag.contains(tag_name))
            .filter(Tag.tag.notin_(selected_tags))
            .order_by(Tag.tag)
            .limit(self.SEARCH_LIMIT)
        )

        if tags.count() <= 0:
            return dict()

        tags = [tag.tag for tag in tags]
        return dict(tags=tags)
