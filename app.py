import sqlite3
from dataclasses import dataclass

from flask import Flask, current_app, g, redirect, render_template, request, url_for


def initialize_database():
    db = sqlite3.connect(current_app.config["DB"])
    try:
        with current_app.open_resource("init.sql", "r") as f:
            db.executescript(f.read())
    finally:
        db.close()


def create_app(**config):
    app = Flask(__name__)

    app.config.from_mapping(DB="todo.db")
    app.config.from_mapping(**config)

    # The database is initialized before the application starts. The code that
    # in the rest of this application assumes that the database already has
    # the required structure. Please note that the database connection used
    # in initialize_database() is not the one used by the routes. The database
    # connection opened by initialize_database() is used exclusively for setting up
    # the structure of the database, if needed.
    #
    # This function also shows that, if you have to execute several statements at
    # once, it's often convenient to write them in a separate file and use the
    # executescript() method on the database connection to execute them all at once.
    # Even if init.sql defines only a single table, in a regular application you
    # usually have several tables, and therefore several CREATE TABLE statements.

    with app.app_context():
        initialize_database()

    # The functions below are automatically called by Flask before the request is
    # processed by a route, and after the route returns (either with an error or
    # not). We want to open the database at the beginning of every request and close
    # it at the end. For more details about the lifecycle of an application and
    # other ways to hook into the request processing, see:
    #
    # https://flask.palletsprojects.com/en/stable/lifecycle/
    #
    # Once connected, the database is saved into `g`, a special object that saves
    # data pertinent to a single request. `g` is useful to transfer data between
    # before_request handlers and routes. To read more about `g`, see:
    #
    # https://flask.palletsprojects.com/en/stable/api/#application-globals
    #
    # Please note that this code opens a connection before every request, and closes
    # it after every request. This happens also for requests that don't need a
    # database, like for the static assets. In a more complex application, you might
    # want to open the database on demand, as described here:
    #
    # https://flask.palletsprojects.com/en/stable/patterns/sqlite3/

    @app.before_request
    def open_db():
        g.db = sqlite3.connect(current_app.config["DB"])

    @app.teardown_request
    def close_db(err):
        if db := g.pop("db", None):
            db.close()

    # This dataclass holds the basic information about a to-do item. The templates
    # assume objects with `id` and `value` properties, which this dataclass has.
    # Python dataclasses are a shorthand for declaring classes with properties and a
    # special constructor. For all the functionalities that come for free with
    # dataclasses, see:
    #
    # https://docs.python.org/3/library/dataclasses.html
    #
    # Another way to do something similar is to have the database connection return
    # lists of sqlite3.Row instead of lists of tuples. You can do that by
    # configuring `g.db.row_factory` to `sqlite3.Row`. To know more about row
    # factories, see:
    #
    # https://docs.python.org/3/library/sqlite3.html#sqlite3-howto-row-factory

    @dataclass
    class Todo:
        id: int
        value: str

    # Fetch all the to-do items from the database as a sequence of (id, value)
    # tuples. Convert the tuples into the Todo dataclass defined above, because the
    # template expects objects with .id and .value properties.

    @app.get("/")
    def index():
        rows = g.db.execute("SELECT id, value FROM todos")
        todos = [Todo(id, value) for (id, value) in rows]
        return render_template("index.html", todos=todos)

    # Insert the to-do item into the database. Duplicate values are not handled: two
    # to-do items might have the same text. Because this route changes the state of
    # the database, it must commit its changes to save them in a durable way.

    @app.post("/add")
    def add():
        item = request.form.get("item")
        if item:
            g.db.execute("INSERT INTO todos (value) VALUES (?)", (item,))
            g.db.commit()
        return redirect(url_for("index"))

    # Delete the to-do item with the given ID from the database. As in the
    # previous route, before this changes the data in the database, the route must
    # commit the change to the database.

    @app.post("/done/<int:id>")
    def done(id):
        g.db.execute("DELETE FROM todos WHERE id = ?", (id,))
        g.db.commit()
        return redirect(url_for("index"))

    return app
