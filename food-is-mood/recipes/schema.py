import colander, deform.widget
from deform.interfaces import FileUploadTempStore


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
    image = colander.SchemaNode(deform.FileData(), widget=deform.widget.FileUploadWidget(tmpstore), title="Upload Image")


