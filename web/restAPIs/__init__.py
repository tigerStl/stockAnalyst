from flask import Flask
from .klineSvc import klineSvc

app = Flask(__name__)
app.register_blueprint(klineSvc)
