# Food is Mood
Recipe book project. Currently using SQLite as db.

## Manual Setup
### Setting up virtualenv
  - install python3-venv
  - python3 -m venv venv
  - source venv/bin/activate
  - pip install -e ./food-is-mood/."[dev]"
  
### Initialize test SQLite database
  - cd to `./food-is-mood/`
  - run `initialize_recipes_db dev.ini` to create database and tables

### Running dev server
  - activate venv with `source venv/bin/activate`
  - run `pserve ./food-is-mood/dev.ini --reload `
  - load [0.0.0.0:6543](http://0.0.0.0:6543/)
  
### Running tests
  - run `pytest food-is-mood/recipes/tests.py`

### Formatting
  - Format python files by running `black food-is-mood/*.py`
  
## Docker
### localhost
  - docker build .
  - docker run --network="host" -p 6543:6543
  

## Notes
### Testing json endpoints
Using `httpie` you can hit the endpoints via command line

```http -v POST  localhost:6543/search_recipes/ "Content-Type:application/json" searchQuery="asd"```


