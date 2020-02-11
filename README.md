# Food is Mood
Description of project

### Setting up virtualenv
  - install python3-venv
  - python3 -m venv venv
  - activate venv with `source venv/bin/activate`
  - cd ./food-is-mood/food-is-mood/
  - pip install -e .
  
### Initialize test database
  #### SQLite
  - cd to `./food-is-mood/food-is-mood/`
  - run `initialize_recipes_db dev.ini` to create database and tables
  
  #### Postgres
  - Install postgres
  - `# su postgres`
  - `$ psql`
  - Within the postgres command line, create user: `CREATE USER food WITH PASSWORD 'mood';`
  - Create the database: `CREATE DATABASE foodismood OWNER food;`
  - `\q` to quit psql, `exit` to get back to main console
  - Edit `/etc/postgresql/<version>/main/pg_hba.conf`
  - Add the following lines to the end
    
    ```
    local   foodismood    food                                    peer
    host    foodismood    food            127.0.0.1               md5
    ```
  - `service postgresql restart`
  - Initialize alembic `alembic init alembic`
  - In alembic.ini update sqlalchemy.url variable to the same sqlalchemy.url value set in dev.ini
  
  #### postgres 2
  sudo apt-get install postgresql
  sudo su - postgres
  
  
## Docker
  - docker build -t eg_postgresql .
  - docker run --rm -P -p 5432:5432 --name pg_test eg_postgresql
  - Now run `docker ps` to check its running
  - To enter postgres shell run `psql -h localhost -p 5432 -d docker -U docker --password`  
  
  
  
### Running dev server
  - activate venv with `source venv/bin/activate`
  - run `pserve ./food-is-mood/ini/dev.ini --reload `
  - load [0.0.0.0:6543](http://0.0.0.0:6543/)
  
### Running tests
  - run `pytest food-is-mood/recipes/tests.py`

