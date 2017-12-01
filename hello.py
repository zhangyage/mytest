#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import Flask,render_template


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>/')
def user(name):
    return render_template('user.html',user=name)



if __name__ == "__main__":
    app.run(debug=True,port=int("80"))
