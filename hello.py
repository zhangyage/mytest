#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask,request,make_response,redirect
from flask_script import Manager

app = Flask(__name__)

# @app.route('/')
# def index():
#     return '<h1>Hello World!</h1>'

# @app.route('/')
# def index():
#     response = make_response('<h1>This document carries a cookie!</h1>') #定义返回值
#     response.set_cookie('answer','42')    #设置cookie
#     return response   
@app.route('/')
def index():
    return redirect("http://baidu.com")


@app.route('/user/<name>')
def user(name):
    return '<h1>Hello,%s!</h1>' % name

@app.route('/browser')
def browser():
    user_agent = request.headers.get('User-Agent')
    return '<h1>your browser is %s</h1>' % user_agent

manager = Manager(app)

if __name__ == "__main__":
    #app.run(debug=True,port=int("80"))
    manager.run()