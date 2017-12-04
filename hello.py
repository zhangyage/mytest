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
app.config['SECRET_KEY']='hard to guess string'   #设置一个跨站请求伪造的key
bootstrap = Bootstrap(app)
moment = Moment(app)

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required

class NameForm(FlaskForm):
    name = StringField('What is your name?',validators=[Required()])
    sex = StringField('Sex?',validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/',methods=["GET","POST"])
def index():
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data=''
    return render_template('index.html',form=form,name=name)


if __name__ == "__main__":
    app.run(debug=True,port=int("80"))
