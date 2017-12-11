#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import render_template,redirect,url_for,request,flash
from . import auth
from flask_login import login_required,login_user,logout_user
#login_required 相当与一个认证用户是否登陆的方法，可以通过装饰器显示用户访问权限
from forms import LoginForm
from app.models import User



@auth.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid Username or Password' , 'error')
    return render_template('auth/login.html',form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'