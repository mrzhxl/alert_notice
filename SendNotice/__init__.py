#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from flask import Flask
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.TestConfig')
    db.init_app(app)

    from .feishu import feishu
    app.register_blueprint(feishu)
    return app

