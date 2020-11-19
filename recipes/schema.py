import colander, deform.widget, json

from .images import verify_image
from deform.interfaces import FileUploadTempStore
from deform.template import ZPTTemplateLoader, ZPTRendererFactory


def validate_image_upload_form(node, image):
    print("VALIDATING the image form")
    print(image)
    try:
        verify_image(image)
    except Exception as e:
        raise colander.Invalid(node, str(e))


class RecipeIngredient(colander.MappingSchema):
    ingredient = colander.SchemaNode(colander.String())
    shopping_list = colander.SchemaNode(colander.Boolean())


class RecipeStep(colander.MappingSchema):
    # rank = colander.SchemaNode(colander.Int(), validator=colander.Range(0, 9999))
    step = colander.SchemaNode(colander.String())


class Tag(colander.MappingSchema):
    tag = colander.SchemaNode(colander.String())


class RecipeIngredients(colander.SequenceSchema):
    ingredient = RecipeIngredient()


class RecipeSteps(colander.SequenceSchema):
    step = RecipeStep()


class RecipeTags(colander.SequenceSchema):
    tag = Tag()


class FileUploadMemoryTempStore(dict):
    def preview_url(self, uid):
        return None


class RecipePage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget())
    ingredients = RecipeIngredients()
    steps = RecipeSteps()
    #tags = RecipeTags()
    rank = colander.SchemaNode(colander.Int(), validator=colander.Range(1, 5))

class RecipeTagsPage(object):
    MAX_ALLOWED_TAGS = 10

    def validate(self, tags_json):
        tags = json.loads(tags_json)['tags']
        
        if not isinstance(tags, list) or not all(isinstance(item, str) for item in tags):
            raise Exception('Invalid format') 

        if len(tags) > self.MAX_ALLOWED_TAGS:
            raise Exception('Too many tags')

        return tags
        

class RecipeImageUploadPage(colander.MappingSchema):
    tmpstore = FileUploadMemoryTempStore()
    # to switch to custom templates add `template="recipes:templates/deform/image_upload.pt"` to widget
    image_upload_widget = deform.widget.FileUploadWidget(tmpstore)
    image = colander.SchemaNode(
        deform.FileData(),
        validator=validate_image_upload_form,
        widget=image_upload_widget,
        title="Upload Image",
    )
