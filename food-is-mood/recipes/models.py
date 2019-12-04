from pyramid.security import Allow, Everyone

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    Text,
    String,
    ForeignKey)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship)

from zope.sqlalchemy import register

DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()

class Recipe(Base):
    __tablename__ = 'recipes'
    uid = Column(Integer, primary_key=True)
    title = Column(String, unique=True)
    description = Column(Text)
    rank = Column(Integer)

    ingredients = relationship('RecipeIngredient', backref="recipes")
    steps = relationship('RecipeStep', backref="recipes")
    tags = relationship('RecipeTag', backref="recipes")

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, value):
        setattr(self, key, value)

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    uid = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.uid'))
    ingredient = Column(String)
    shopping_list = Column(Boolean)

class RecipeStep(Base):
    __tablename__ = 'recipe_steps'
    uid = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.uid'))
    rank = Column(Integer)
    step = Column(String)

class Tag(Base):
    __tablename__ = 'tags'
    uid = Column(Integer, primary_key=True)
    tag = Column(String)

class RecipeTag(Base):
    __tablename__ = 'recipe_tags'
    uid = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipes.uid'))
    tag_id = Column(Integer, ForeignKey('tags.uid'))

class Root(object):
    __acl__ = [(Allow, Everyone, 'edit'),
               (Allow, 'group:editors', 'edit')]

    def __init__(self, request):
        pass
