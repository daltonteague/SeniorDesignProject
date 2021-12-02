# Nile Loadtest Server

This server receives Locust request data from the Nile Test Library and System Metrics from the metrics scraper (scraper not yet implemented). These results, along with the test that created them, are saved and can be viewed at localhost:5000/tests while the server is running. The endpoint code resides in webservice.py, and server code coverage is provided by test_endpoint.py.

### Setup up Postgres Database and Server

1. Install Docker
2. Start and setup the virtual environment
    ```
    pipenv shell
    ```
    ```
    pipenv install 
    ```
3. From the pipenv shell, run
    ```
    docker-compose up -d
    ```
    - This will start the postgres container
4. If the database is being set up for the first time
    - Delete the migrations folder
    - Run:
    ```
    python manage.py db init; python manage.py db migrate; python manage.py db upgrade
    ```
5. To stop the postgres container, run
    ```
    docker-compose down
    ```

### Start the Webserver

5. Start the webservice with 
    ```
    python webservice.py
    ```
6. To stop the webservice, hit ctrl-c

### Use Database Shell

1. Run the Postgres database from the docker compose file
    ```
    docker exec -it <docker-container-id> bash
    ```
2. Switch to the database owner, postgres
    ```
    su postgres
    ```
3. Enter postgres shell like normal as postgres user
    ```
    psql
    ```
 
### Migrate the Database

1. Delete migrations folder
2. Run:
    ```
    python manage.py db init
    ```
    ```
    python manage.py db migrate
    ```
    ```
    python manage.py db upgrade
    ```
    OR
    ```
    python manage.py db init; python manage.py db migrate; python manage.py db upgrade
    ```

### Run server tests

While the server is stopped, run the following command to test the server and display coverage report:
    ```
    python manage.py test
    ```
