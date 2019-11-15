# Food is Mood
Description of project

### Setting up virtualenv
  - install python3-venv
  - python3 -m venv venv
  - activate venv with `source venv/bin/activate`
  - pip install -e ./food-is-mood/ini/
  
### Initialize test SQLite database
  - run `python engine.py` to create database and tables

### Running dev server
  - activate venv with `source venv/bin/activate`
  - run `pserve ./food-is-mood/ini/dev.ini --reload `
  - load [0.0.0.0:6543](http://0.0.0.0:6543/)
  
### Running tests
  - run `pytest food-is-mood/recipes/tests.py`

