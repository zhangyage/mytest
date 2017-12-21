#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,BooleanField,PasswordField,TextAreaField
from wtforms.validators import Required,Length,Email, regexp, EqualTo,\
    ValidationError, DataRequired
from app.models import User



#用户登录表单
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
    
#用户注册表单
class RegistrationForm(FlaskForm):
    email = StringField(label=u"Email",
                        validators=[
                            Required(),
                            Length(1,64),
                            Email(u"邮箱格式不正确！")
                            ]
                        )
    
    username = StringField(label="Username",
                    validators=[
                        Required(),
                        Length(1,64),
                        regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                               'Username must have only letters,number, dots or underscores')
                        ]
                    )
    password = PasswordField(label="Password",
                             validators=[
                             Required(),
                             EqualTo('password2',message='Passwords must match.')
                            ]
                        )
    password2 = PasswordField(label="Confirm Password",
                             validators=[
                             Required()
                             ]
                        )
    
    submit = SubmitField(label='Register')
    
    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')
    
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use')  

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm new password',
                              validators=[DataRequired()])
    submit = SubmitField('Update Password')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class ChangeEmailForm(FlaskForm):
    email = StringField('New Email', validators=[DataRequired(), Length(1, 64),
                                                 Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.') 
        
 
