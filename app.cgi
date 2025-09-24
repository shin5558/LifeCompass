#!/usr/bin/env python3
import cgitb
cgitb.enable()  # CGIエラーログを表示

from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, World! This is Flask running as CGI."

if __name__ == "__main__":
    from wsgiref.handlers import CGIHandler
    CGIHandler().run(app)