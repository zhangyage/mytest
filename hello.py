#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
    flask_sqlalchemy  (ORM)
'''


from flask import Flask,render_template,session,url_for,redirect,flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///' +os.path.join(basedir, 'data.sqlite')   #设置数据库uri
app.config[' SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True   #设置参数每次更改数据都需要提交
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
bootstarp = Bootstrap(app)
moment = Moment(app)
db=SQLAlchemy(app)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username



class NameForm(FlaskForm):
    name = StringField('What is your name?',validators=[Required()])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),known=session.get('known', False))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

#manager = Manager(app)

if __name__ == "__main__":
    app.run(debug=True,port=int("80"))
    #manager.run()    #使用这个方式启动，是为了在shel模式下简历我们的数据库表
