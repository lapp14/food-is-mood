import colander, deform.widget


class RecipeIngredient(colander.MappingSchema):
    ingredient = colander.SchemaNode(colander.String())
    shopping_list = colander.SchemaNode(colander.Boolean())


class RecipeStep(colander.TupleSchema):
    rank = colander.SchemaNode(colander.Int(), validator=colander.Range(0, 9999))
    step = colander.SchemaNode(colander.String())


class RecipeTag(colander.MappingSchema):
    tag = colander.SchemaNode(colander.String())


class RecipeIngredients(colander.SequenceSchema):
    ingredient = RecipeIngredient()


class RecipeSteps(colander.SequenceSchema):
    step = RecipeStep()


class RecipeTags(colander.MappingSchema):
    tag = RecipeTag()


class RecipePage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    description = colander.SchemaNode(
        colander.String(), widget=deform.widget.RichTextWidget()
    )
    ingredients = RecipeIngredients()
    steps = RecipeSteps()
    # tags = RecipeTags()
    rank = colander.SchemaNode(colander.Int(), validator=colander.Range(1, 5))
