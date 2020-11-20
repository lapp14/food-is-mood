# Food is Mood
Recipe book project. Currently using SQLite as db.

## Manual Setup
### Setting up virtualenv
  - install python3-venv
  - python3 -m venv venv
  - source venv/bin/activate
  - Install requirements with `pip install -r requirements.txt`
  - (Optional) Install dev dependencies with `pip install -e ./food-is-mood/."[dev]"`
  
### Initialize test SQLite database
  - run `initialize_recipes_db dev.ini` to create database and tables

### Environment vars
The following environment vars are required
```
AWS_ACCESS_KEY_ID=""
AWS_SECRET_ACCESS_KEY=""
AWS_S3_BUCKET_NAME="food-is-mood"
AWS_S3_BUCKET_URL=""
AWS_S3_BASE_PATH="dev/"
AWS_S3_BASE_URL=""
```

### `.ini` files
The ini files are used as pyramid config. In production, logging levels of `WARN` can be useful.
For production, specify `host` and `port` under `[server:main]`

### Running dev server
  - activate venv with `source venv/bin/activate`
  - run `pserve dev.ini --reload `
  - load [0.0.0.0:6543](http://0.0.0.0:6543/)
  
### Running tests
  - run `pytest recipes/tests.py`

### Formatting
  - Format python files by running `black food-is-mood/*.py`
  
## Docker
  - docker build .
  - docker run -d --name food-is-mood  -p 6543:6543 -v /home/dan/public_html/food-is-mood/:/app/ <container-id>
 

## Notes

Sometimes you need to cd into `recipes/` and run `export PYTHONPATH=.` to fix the module not found error for recipes package

### Testing json endpoints
Using `httpie` you can hit the endpoints via command line

```http -v POST  localhost:6543/search_recipes/ "Content-Type:application/json" searchQuery="asd"```


