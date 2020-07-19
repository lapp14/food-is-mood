import colander, deform.widget
from deform.interfaces import FileUploadTempStore
from deform.template import ZPTTemplateLoader, ZPTRendererFactory


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
    tmpstore = FileUploadMemoryTempStore()
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(colander.String(), widget=deform.widget.TextAreaWidget())
    ingredients = RecipeIngredients()
    steps = RecipeSteps()
    tags = RecipeTags()
    rank = colander.SchemaNode(colander.Int(), validator=colander.Range(1, 5))

    image_upload_widget = deform.widget.FileUploadWidget(tmpstore, template="recipes:templates/deform/image_upload.pt")
    image = colander.SchemaNode(deform.FileData(), widget=image_upload_widget, title="Upload Image")


