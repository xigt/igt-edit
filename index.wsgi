import sys, os

from flask import Flask

sys.path.append(os.path.dirname(__file__))

from browser import app
import sleipnir
import config

application = app

app.register_blueprint(sleipnir.blueprint)

