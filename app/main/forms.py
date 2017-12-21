#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,PasswordField,TextAreaField
from wtforms.validators import Required,Length,Email, regexp, EqualTo,\
    ValidationError, DataRequired
from app.models import User



class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
#用户资料编辑表单        
class EditProfileForm(FlaskForm):
     name = StringField('Real name', validators=[Length(0, 64)])
     location = StringField('Location', validators=[Length(0, 64)])
     about_me = TextAreaField('About me')
     submit = SubmitField('Submit')