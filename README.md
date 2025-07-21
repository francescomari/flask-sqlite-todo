# To-Do List in Flask and SQLite

This is a simple web application for managing a to-do list, built using
[Flask](https://flask.palletsprojects.com/) and
[SQLite](https://www.sqlite.org/).

## Prerequisites

This repository builds on the concepts explained in:

- [Introduction to Flask](https://github.com/francescomari/flask-introduction)
- [To-Do List in Flask](https://github.com/francescomari/flask-todo)
- [Introduction to Databases and SQLite](https://github.com/francescomari/sqlite-todo)

The application can be set up and run using the same techniques described in the
repositories above.

## The code

Pay attention to both [the application code](app.py) and the
[web application template](templates/index.html). The application code defines
all the routes that the application responds to, while the template is
responsible for dynamically rendering the HTML of the web application depending
on the to-do list. The code that is unique to this project is heavily commented.

This application is a bit different than the previous ones. Instead of using a
global `app` variable, it uses an application factory `create_app` instead. The
application factory is automatically called by the `flask` CLI to create a new
application. The behavior of the `flask` CLI is documented [here][1].
Application factories are a known Flask patterns and are documented [here][2].

The reason for an application factory is that this pattern allows you to create
an application during tests and tweak the configuration of the application
before the tests start. See how [the tests](test_app.py) create an application
before each test starts, configure the application to enable the test client,
and point each test to a different, temporary database.

[1]: https://flask.palletsprojects.com/en/stable/cli/
[2]: https://flask.palletsprojects.com/en/stable/patterns/appfactories/
