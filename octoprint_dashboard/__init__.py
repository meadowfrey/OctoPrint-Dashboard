from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = "something"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
import octoprint_dashboard.model
db.create_all()

import octoprint_dashboard.cli_commands

import octoprint_dashboard.login.routes
import octoprint_dashboard.api

from octoprint_dashboard.scheduler import Scheduler

scheduler = Scheduler()


@app.route('/')
@app.route('/admin')
def frontend():
    return send_from_directory('dist', 'index.html')


@app.route('/<text>.js')
def neco(text):
    return send_from_directory('dist', text + ".js")


@app.route('/uploadtest', methods=['POST'])
def upload():
    print(request.data)
    for i in request.files.keys():
        print(i)
    return 'parek', 201
