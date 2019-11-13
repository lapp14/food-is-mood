from sqlalchemy import create_engine, Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Engine():
    DATABASE_URI = 'sqlite:///tmp/test.db'
    def __init__(self):
        self.engine = create_engine(self.DATABASE_URI, echo=True)

    def get(self):
        return self.engine

# https://docs.sqlalchemy.org/en/13/orm/tutorial.html
if __name__ == '__main__':
    print('Creating database from engine')
    engine = Engine()
    Base.metadata.create_all(engine.get())

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)

    def __repr__(self):
        return '<User(first_name={self.first_name}, last_name={self.last_name})>'.format(self=self)

    def __str__(self):
        return 'User: {self.last_name}, {self.first_name}'.format(self=self)

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(String)
    created_by_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_date_time = Column(DateTime, nullable=False)
    updated_date_time = Column(DateTime, nullable=False)

class RecipeSteps(Base):
    __tablename__ = 'recipe_steps'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)

class Ingredient(Base):
    __tablename__ = 'ingredients'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    measurement_unit_id = Column(Integer, ForeignKey('measurement_units.id'), nullable=False)

class MeasurementUnit(Base):
    __tablename__ = 'measurement_units'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
