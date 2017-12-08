#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,PasswordField
from wtforms.validators import Required,Length,Email

class LoginForm(FlaskForm):
    email = StringField(label=u"Email",
                        validators=[
                            Required(),
                            Length(1,64),
                            Email(u"邮箱格式不正确！")
                            ]
                        )
    password = PasswordField(label="Password",
                             validators=[
                             Required()
                            ]
                        )
    remember_me = BooleanField(label="Keep me logged in")
    submit = SubmitField(label='login')