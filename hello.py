#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
flask-moment  学习使用moment同一时间，  对应的直接使用本地电脑的时间，不在从服务器中获取时间
'''

from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/time/')
def time():
    return render_template('moment.html',current_time = datetime.utcnow())

@app.route('/user/')
def users():
    return render_template('user.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500


if __name__ == "__main__":
    app.run(debug=True,port=int("80"))
